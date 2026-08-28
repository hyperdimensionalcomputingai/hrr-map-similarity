# Repository instructions

## Purpose

Keep this repository a small teaching experiment. A reader should be able to run four obvious scripts, inspect the fabricated source data, and see how one symbolic encoder behaves under HRR and MAP.

The project interface is four directly runnable scripts. Prefer short modules, explicit constants, and concise comments for assumptions that benefit a new reader.

## Environment and commands

Use `uv` for dependency management and every Python-based command. Prefix script, test, and formatting commands with `uv run`; let `uv` manage `.venv`.

Install exactly the locked environment:

```bash
uv sync --frozen
```

Run the experiment in order:

```bash
uv run src/01_make_demo_data.py
uv run src/02_encode.py
uv run src/03_evaluate.py
uv run src/04_dimension_sweep.py
```

Format, lint, and test before handing off a change:

```bash
uv run ruff format .
uv run ruff check .
uv run pytest -q
```

Use `uv add <dependency>` or `uv add --dev <dependency>` when changing dependencies so `pyproject.toml` and the generated `uv.lock` stay synchronized.

## Project structure

The runnable scripts stay directly under `src/`. Shared logic is grouped by responsibility:

```text
src/
├── 01_make_demo_data.py
├── 02_encode.py
├── 03_evaluate.py
├── 04_dimension_sweep.py
├── algebra/
│   ├── __init__.py
│   ├── base.py
│   ├── hrr.py
│   └── map.py
├── encoding/
│   ├── __init__.py
│   ├── encoder.py
│   └── terms.py
├── evaluation/
│   ├── __init__.py
│   ├── retrieval.py
│   └── similarity.py
├── storage/
│   ├── __init__.py
│   └── ingest.py
└── visualization/
    ├── __init__.py
    └── viz.py
```

- `algebra` owns the common operation contract and the HRR/MAP implementations.
- `encoding` owns dataset semantics and the one shared encoder skeleton.
- `evaluation` owns source similarity, vector comparisons, retrieval, and tie analysis.
- `storage` owns raw JSON, Polars, PyArrow, and LanceDB I/O.
- `visualization` owns publication-friendly charts and must remain storage-agnostic.
- `tests` contains focused behavior and repository-policy checks.
- `.agents/skills` contains the reusable dataset-adaptation and dimension-sweep instructions.

The directories expose small APIs through `__init__.py`. `[tool.uv] package = false` keeps the four scripts as the project interface.

## Invariants

- HRR and MAP must use the exact same `encode_record()` and term vocabulary. Only the algebra object changes.
- A dimension sweep may change only dimension and seed. Dataset, record order, term semantics, field weights, and source baseline stay fixed.
- Raw inspectable input belongs in `data/raw/`. Generated LanceDB state belongs in `data/*.lancedb`.
- Generated tables, metrics, and figures stay local in the Git-ignored `artifacts/` directory.
- Use Polars and PyArrow for tabular work, and NumPy or TorchHD for numerical operations. SciPy stays transitive through TorchHD.
- Keep plots agnostic to LanceDB or any other storage layer.
- If dataset semantics change, update `METHODOLOGY.md`, relevant tests, and the reusable skills together.

## Repository skills

Read the applicable skill in `.agents/skills/` completely before acting:

- Use `hrr-map-dataset-adaptation` when replacing the source dataset or changing
  its ingest schema, record IDs, or `record_terms()` semantics. It guides the
  data-to-terms contract and the full four-script acceptance run. Do not use it
  for an unchanged-dataset benchmark rerun or a visualization-only change.
- Use `vsa-dimension-sweep` after `src/03_evaluate.py` succeeds when running,
  changing, validating, or interpreting the multi-dimension, multi-seed
  benchmark. It requires dataset order, term semantics, field weights, and the
  source baseline to remain fixed while only dimension and seed vary.

For a new dataset followed by a capacity benchmark, use the skills in that
order: adapt and validate the dataset first, then run and interpret the sweep.
Keep a skill's documented outputs synchronized with the scripts when their
artifact contract changes.

## Changing the dataset

Replace the raw JSON, update the ingest constants if needed, and adapt `record_terms()` in `src/encoding/terms.py`. That function is the explicit semantic contract between source records and both vector spaces. Then rerun all four scripts and the validation commands above.
