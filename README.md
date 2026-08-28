# Same encoder, different algebra

This repository asks one question: if the same HDC encoder is expressed with HRR and MAP, do both representations preserve the relationships in the source records?

The encoder is shared. HRR binds real-valued hypervectors with circular convolution. MAP binds bipolar hypervectors with element-wise multiplication. Both bundle with addition and normalize the result for cosine similarity.

The central code is exactly this simple:

```python
hrr = make_algebra("hrr", dimensions=4096, seed=2026)
map_ = make_algebra("map", dimensions=4096, seed=2026)

hrr_vector = encode_record(record, hrr)
map_vector = encode_record(record, map_)
```

Both calls pass through the same `encode_record()` function. The numerical operations differ only inside [`hrr.py`](src/algebra/hrr.py) and [`map.py`](src/algebra/map.py).

[`METHODOLOGY.md`](METHODOLOGY.md) gives the exact field-by-field source formula, encoding assumptions, sweep controls, and a worked T12/T13 comparison.
[`AGENTS.md`](AGENTS.md) documents the repository structure and development conventions for people and coding agents.

## Run the experiment

Install the locked dependencies:

```bash
uv sync --frozen
```

Then read and run the four scripts in order:

```bash
uv run src/01_make_demo_data.py
uv run src/02_encode.py
uv run src/03_evaluate.py
uv run src/04_dimension_sweep.py
```

Each script has a short block of editable constants near the top. Running these scripts directly is the complete workflow.

### 1. Create the dataset

[`01_make_demo_data.py`](src/01_make_demo_data.py) loads the 20 fabricated records from [`data/raw/tea-samples.json`](data/raw/tea-samples.json) through Polars and writes them to LanceDB.

### 2. Encode the records

[`02_encode.py`](src/02_encode.py) loads the records, creates one HRR algebra and one MAP algebra, and passes both through the shared encoder in [`encoding/encoder.py`](src/encoding/encoder.py). It stores both vector columns in LanceDB and writes `artifacts/encoded.parquet` for inspection.

Each tea becomes a set of role-value facts such as:

```text
tea_type=black
origin=india
aroma_notes=muscatel
elevation_m=[1500,2000)
```

The strings use exact identity semantics: `floral` matches `floral`, while `floral` and `orchid` contribute zero shared terms. Deterministic random hypervectors give each symbol a stable identity.

### 3. Evaluate similarity and retrieval

[`03_evaluate.py`](src/03_evaluate.py) compares every record pair using:

```text
exact source similarity
HRR cosine similarity
MAP cosine similarity
```

Source similarity is the normalized count of identical role-value facts. This explicit baseline tells us what structure the encoder is supposed to preserve.

The script also performs a small top-4 retrieval check against both vector columns. Raw overlap requires identical neighbor IDs. Tie-aware overlap also accepts a different ID when both alternatives have equal source similarity.

The current 20-record run at 4,096 dimensions and seed 2,026 produces:

| Measurement | Result |
| --- | ---: |
| HRR correlation with source similarity | 0.9972 |
| MAP correlation with source similarity | 0.9975 |
| HRR correlation with MAP | 0.9945 |
| Raw top-4 overlap | 0.9167 |
| Tie-aware top-4 overlap | 1.0000 |
| Disagreements inside source ties | 2 of 2 |

The two raw disagreements occur for queries T08 and T20. In both cases, HRR and MAP chose different IDs with equal source similarity to the query. Treating source-equivalent neighbors as interchangeable therefore accounts for all observed top-k disagreement slots in this run.

The tie-aware result says that the observed ID swaps preserve the symbolic ranking defined by this dataset. These values apply to this dataset, encoder, dimension, seed, query sample, and `k`.

### 4. Sweep dimensions

[`04_dimension_sweep.py`](src/04_dimension_sweep.py) repeats the primary source-similarity benchmark across six dimensions and five seeds while keeping every encoder and dataset choice fixed.

The current means are:

| Dimensions | HRR vs source | MAP vs source |
| ---: | ---: | ---: |
| 512 | 0.9706 | 0.9760 |
| 1,024 | 0.9849 | 0.9870 |
| 2,048 | 0.9928 | 0.9944 |
| 4,096 | 0.9966 | 0.9974 |
| 8,192 | 0.9981 | 0.9987 |
| 10,000 | 0.9981 | 0.9988 |

For this experiment, 2,048 dimensions is a clear empirical knee and 4,096 is a conservative default. The figure includes the individual seed points alongside the mean curves.

## Generated outputs

Running all four scripts recreates:

```text
artifacts/
├── encoded.parquet
├── metrics.json
├── pairwise.parquet
├── retrieval.parquet
├── retrieval-disagreements.parquet
├── sweep.parquet
└── figures/
    ├── similarity-comparison.png
    └── dimension-sweep.png
```

Generated artifacts, LanceDB tables, Python caches, and `dist/` are ignored by Git. The raw JSON remains visible and versionable.

## Change the data

For another small categorical dataset:

1. Replace the raw JSON and update the paths at the top of [`01_make_demo_data.py`](src/01_make_demo_data.py).
2. Edit `record_terms()` in [`encoding/terms.py`](src/encoding/terms.py) so one record becomes the intended `(role, value)` facts.
3. Update the ID or table constants in [`storage/ingest.py`](src/storage/ingest.py) if necessary.
4. Run the same four scripts again. Both plots and every result table will be regenerated.

Dataset-specific code decides which facts matter; the shared encoder and algebra implementations remain unchanged.

## Interpretation and scope

The results support a focused representational claim: on this exact symbolic encoder, both HRR and MAP closely recover the source geometry, and the observed retrieval differences occur within source-level ties.

The evidence covers a small fabricated dataset, exact symbol identity, 500-meter elevation bins, unordered oxidation and roast categories, all-pairs similarity, six retrieval queries, and a six-dimension sweep across five seeds.

For independent review, check whether:

- the source formula in [`METHODOLOGY.md`](METHODOLOGY.md) matches the intended semantics;
- equal source similarities are the right definition of interchangeable neighbors;
- independent random atom memories are the right HRR/MAP comparison;
- the dimension recommendation remains explicitly workload-specific;
- the commands above reproduce the generated metrics and figures.

The implementation layout and contribution commands live in [`AGENTS.md`](AGENTS.md).

The project source uses NumPy, PyArrow, Polars, and TorchHD. TorchHD brings SciPy into the locked environment as a transitive dependency.

The completed validation run executed all four scripts, passed all 8 tests, confirmed 30 unique finite sweep cells, validated both repository skills, and visually checked both PNG figures. Plot titles and legends are agnostic to the storage layer.
