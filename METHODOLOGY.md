# HRR/MAP experiment methodology

## How is source-level similarity defined?

Each tea record is converted into a set of exact `(role, value)` terms. The current encoder uses:

| Field | Terms contributed by one record | Match rule |
| --- | ---: | --- |
| `tea_type` | 1 | Exact normalized string match |
| `origin` | 1 | Exact normalized string match |
| `oxidation` | 1 | Exact normalized string match |
| `roast` | 1 | Exact normalized string match |
| `elevation_m` | 1 | Exact 500-meter bin match |
| `aroma_notes` | One per distinct note | Exact normalized note match |

For records (A) and (B), let (T_A) and (T_B) be their term sets. Source similarity is cosine similarity in an explicit one-hot space of those terms:

$$
S_{source}(A,B)
=
\frac{|T_A \cap T_B|}{\sqrt{|T_A||T_B|}}
$$

Expanded field by field, the numerator is:

$$
\begin{aligned}
|T_A \cap T_B| ={}&
\mathbf{1}[type_A = type_B] \\
&+ \mathbf{1}[origin_A = origin_B] \\
&+ \mathbf{1}[oxidation_A = oxidation_B] \\
&+ \mathbf{1}[roast_A = roast_B] \\
&+ \mathbf{1}[elevationBin_A = elevationBin_B] \\
&+ |aromas_A \cap aromas_B|
\end{aligned}
$$

Every current tea has three distinct aroma notes, so each record has eight terms: five scalar terms and three aroma terms. For this fixture, the denominator is therefore:

$$
\sqrt{8 \times 8} = 8
$$

and source similarity reduces to `number of exact shared terms / 8`.

## How is `elevation_m` handled?

Elevation is converted to a 500-meter categorical bin:

$$
start = \left\lfloor \frac{elevation}{500} \right\rfloor \times 500
$$

The encoded value is the half-open interval:

$$
[start, start + 500)
$$

Examples:

```text
600 m  -> [500,1000)
800 m  -> [500,1000)
1400 m -> [1000,1500)
```

Elevation similarity is categorical:

- one exact matching term when they fall in the same bin;
- zero matching terms when they fall in different bins, including adjacent bins.

The hypervector encoder uses the same categorical rule by assigning an atom to the bin string.

## How are oxidation and roast handled?

`oxidation` and `roast` are exact, independent categorical values. Values such as `low`, `medium`, and `high` each receive their own symbol.

For example:

```text
oxidation=medium vs oxidation=high -> 0 matching terms
roast=light vs roast=medium        -> 0 matching terms
```

The hypervector encoder implements this rule with an independent deterministic random atom for each value. An ordered variant would define graded terms in both `record_terms()` and the source baseline.

## How are `aroma_notes` handled?

Each distinct normalized aroma note becomes its own exact term:

```text
aroma_notes=floral
aroma_notes=honey
aroma_notes=orchid
```

The source baseline counts the size of the exact set intersection:

$$
|aromas_A \cap aromas_B|
$$

The overall source cosine includes the exact aroma intersection alongside every scalar term. For example, `floral` and `orchid` contribute zero shared aroma terms.

Inside the HDC encoder, every note is represented as a bound role-value term:

```python
algebra.bind(
    algebra.atom("role:aroma_notes"),
    algebra.atom("value:aroma_notes:floral"),
)
```

Those bound note vectors are bundled with the terms from every other field. Thus the HDC representation uses bundled note hypervectors, while the intended source geometry is defined by exact note overlap.

## Are source and encoder weights consistent?

Yes, at the individual-term level. Every term has unit weight:

- every exact role-value match contributes one unit to the source numerator;
- every bound role-value hypervector is added once to the encoded bundle;
- both the source representation and the hypervector are normalized afterward.

There is an implicit field weighting caused by term count. Each scalar field contributes one term, while the three aroma notes contribute three terms collectively. For the current eight-term records:

| Component | Maximum contribution |
| --- | ---: |
| `tea_type` | 1/8 |
| `origin` | 1/8 |
| `oxidation` | 1/8 |
| `roast` | 1/8 |
| `elevation_m` | 1/8 |
| All three aroma notes | 3/8 |

Finite-dimensional HRR and MAP cosines approximate the exact source score, with small random cross-talk among independent bundled terms.

## Does the same encoder run for HRR and MAP?

Yes. Both representations go through the same call path:

```python
hrr = make_algebra("hrr", dimensions=4096, seed=2026)
map_ = make_algebra("map", dimensions=4096, seed=2026)

hrr_vector = encode_record(record, hrr)
map_vector = encode_record(record, map_)
```

`encode_record()` and `encode_terms()` share one implementation. The algebra object supplies four operations:

```text
atom
bind
bundle
normalize
```

HRR implements binding with circular convolution over real-valued hypervectors. MAP implements binding with element-wise multiplication over bipolar hypervectors. Their coordinates and atomic memories are independent; only the logical vocabulary and encoder skeleton are shared.

## Worked example: T12 versus T13

The source rows are:

| Field | T12: Dong Ding | T13: Oriental Beauty | Contribution |
| --- | --- | --- | ---: |
| `tea_type` | `oolong` | `oolong` | 1 |
| `origin` | `taiwan` | `taiwan` | 1 |
| `oxidation` | `medium` | `high` | 0 |
| `roast` | `medium` | `light` | 0 |
| `elevation_m` | 800 -> `[500,1000)` | 600 -> `[500,1000)` | 1 |
| `aroma_notes` | `roasted nuts`, `honey`, `orchid` | `honey`, `muscatel`, `floral` | 1 (`honey`) |

They share four of eight terms:

$$
S_{source}(T12,T13) = \frac{4}{\sqrt{8 \times 8}} = \frac{4}{8} = 0.5
$$

At 4,096 dimensions and seed 2,026, the generated vectors produce:

| Representation | Similarity |
| --- | ---: |
| Exact source baseline | 0.5000 |
| HRR cosine | 0.4987 |
| MAP cosine | 0.5108 |

Both algebras closely recover the intended 0.5 relationship in independent coordinate spaces.

## What changes during the dimension sweep?

Only two values change:

```text
hypervector dimension
random seed
```

The script loads the dataset once before the loop and computes the source terms once. The following remain fixed:

```text
record IDs and order
dataset rows
record_terms() semantics
field and term weighting
source-similarity formula
HRR and MAP operation definitions
```

The dimension sweep measures the primary all-pairs source-similarity benchmark. The separate fixed-dimension retrieval evaluation uses the same six deterministic query IDs for HRR and MAP.

## What is the simplest final plot?

Use one scatter plot:

```text
x-axis: exact source similarity
y-axis: hypervector cosine similarity
series: HRR and MAP
reference: y = x
```

This plot directly answers the main question:

> Do HRR and MAP both preserve the similarity relationships we intended to encode?

If both point clouds follow the `y = x` line, both algebras recover the source geometry. The dimension-sweep line chart is useful as a secondary plot for the separate capacity question: how many dimensions are needed before that preservation becomes stable across seeds?
