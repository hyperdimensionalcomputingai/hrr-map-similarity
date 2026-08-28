---
name: vsa-dimension-sweep
description: Run and interpret the repository's direct multi-dimension, multi-seed HRR/MAP source-preservation experiment.
---

# VSA dimension sweep

Use this skill after `src/03_evaluate.py` succeeds for a fixed dimension and seed.

The sweep asks how many dimensions this frozen dataset and encoder need before HRR and MAP reliably preserve exact source similarity. Its conclusion applies to that experiment configuration.

## Freeze everything except dimension and seed

Inspect `src/04_dimension_sweep.py`. Confirm that:

- `DATABASE` and `LIMIT` select the intended fixed records;
- `record_terms()` is accepted and stays fixed during the sweep;
- HRR and MAP use the same dimension in every cell;
- `DIMENSIONS` and `SEEDS` are the only experimental variables.

Use user-provided values when available. Otherwise, the teaching defaults are:

```python
DIMENSIONS = [512, 1024, 2048, 4096, 8192, 10000]
SEEDS = [2026, 2027, 2028, 2029, 2030]
```

Five seeds expose random item-memory variability.

## Run the script

```bash
uv run src/04_dimension_sweep.py
```

The script writes:

- `artifacts/sweep.parquet`: one row per dimension and seed;
- `artifacts/figures/dimension-sweep.png`.

The figure intentionally shows only the two primary curves: HRR versus source similarity and MAP versus source similarity. HRR-versus-MAP correlation and both absolute errors remain available in the Parquet file as supporting diagnostics.

## Validate and interpret

Using Polars, confirm that `sweep.parquet` has one unique row per `(dimensions, seed)` and finite values for:

```text
hrr_vs_source
map_vs_source
hrr_vs_map
hrr_source_mae
map_source_mae
```

Inspect the individual seed points and error bars. Look for the smallest practical dimension where both source correlations are consistently strong and the next dimensions yield small gains. Allow mild nonmonotonicity, show every seed, and base the recommendation on the observed empirical knee.

Use `src/03_evaluate.py` for the separate fixed-dimension raw and tie-aware neighbor check.

Report the result as capacity for the frozen dataset, term encoder, dimensions, and seeds. Include anomalies and limitations.
