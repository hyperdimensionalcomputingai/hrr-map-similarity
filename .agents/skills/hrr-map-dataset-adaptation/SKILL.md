---
name: hrr-map-dataset-adaptation
description: Adapt the small HRR/MAP teaching experiment to another dataset while preserving its shared encoder and source-similarity evaluation.
---

# HRR/MAP dataset adaptation

Use this skill when replacing the tea data with another small categorical dataset.

## Preserve the central invariant

Both representations must use the same logical path:

```python
hrr_vector = encode_record(record, hrr)
map_vector = encode_record(record, map_)
```

Only `make_algebra(...)` chooses HRR or MAP. Keep `src/encoding/encoder.py`, the evaluation modules, and the numbered scripts algebra-agnostic.

## Adapt the dataset

1. Inspect the source with PyArrow or Polars, and use those libraries exclusively for tabular work.
2. Start with 20 to 100 deterministic records and one non-null, unique ID column.
3. Put raw JSON somewhere under `data/raw/`, or change `create_demo_dataset()` in `src/storage/ingest.py` for the actual source format.
4. Update the path, table, and ID constants in `src/storage/ingest.py` only when needed.
5. Edit `record_terms()` in `src/encoding/terms.py` so one record becomes a short list of `(role, value)` facts.

Prefer exact categorical facts first. Normalize text deterministically. Bin continuous numbers when the bin has a defensible source-level meaning. For identity-based list values, add a concise comment explaining their exact-match semantics.

Keep dataset adaptation focused on the explicit record-to-terms mapping. The algebra remains the reusable abstraction.

## Run and inspect

Run the teaching workflow directly:

```bash
uv run src/01_make_demo_data.py
uv run src/02_encode.py
uv run src/03_evaluate.py
uv run src/04_dimension_sweep.py
```

Inspect:

- `artifacts/pairwise.parquet` for source, HRR, and MAP similarities;
- `artifacts/metrics.json` for both source correlations;
- `artifacts/retrieval.parquet` for concrete neighbor results;
- `artifacts/retrieval-disagreements.parquet` for source-tie swaps;
- `artifacts/sweep.parquet` and both figures for dimension behavior.

## Acceptance checks

- The same ordered records and terms feed HRR and MAP.
- Both vector matrices have the same row count and dimension.
- Both representations are compared directly with the exact source baseline.
- Raw and tie-aware retrieval overlap are both reported.
- `uv run pytest -q` passes, including deterministic algebra checks, the shared-encoder test, and the tabular-library guard.

Interpret results as evidence for this dataset, encoder, dimension, seeds, queries, and `k`. Describe the experiment as **same encoder, different algebra**.
