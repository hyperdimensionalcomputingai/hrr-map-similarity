"""Read the raw fixture and persist source and encoded records in LanceDB."""

from __future__ import annotations

from pathlib import Path

import lancedb
import numpy as np
import polars as pl
import pyarrow as pa

PROJECT_ROOT = Path(__file__).resolve().parents[2]
RAW_DATA_PATH = PROJECT_ROOT / "data/raw/tea-samples.json"
DATABASE_PATH = PROJECT_ROOT / "data/tea-demo.lancedb"
SOURCE_TABLE = "tea_samples"
ENCODED_TABLE = "tea_samples_hdc"
ID_COLUMN = "sample_id"


def create_demo_dataset(
    path: Path = DATABASE_PATH,
    *,
    raw_path: Path = RAW_DATA_PATH,
    n: int = 20,
) -> int:
    """Load up to ``n`` raw JSON rows into the demo LanceDB table."""
    if n < 1:
        raise ValueError("n must be positive")
    frame = pl.read_json(raw_path).head(n)
    _validate_ids(frame)
    path.parent.mkdir(parents=True, exist_ok=True)
    lancedb.connect(path).create_table(SOURCE_TABLE, frame.to_arrow(), mode="overwrite")
    return frame.height


def load_records(
    path: Path = DATABASE_PATH,
    *,
    table_name: str = SOURCE_TABLE,
    limit: int | None = None,
) -> pl.DataFrame:
    """Read source or encoded records through Arrow into Polars."""
    table = lancedb.connect(path).open_table(table_name)
    arrow = table.to_arrow() if limit is None else table.head(limit)
    frame = pl.from_arrow(arrow)
    if not isinstance(frame, pl.DataFrame):
        raise TypeError("expected a Polars DataFrame")
    _validate_ids(frame)
    return frame


def write_encoded_vectors(
    records: pl.DataFrame,
    hrr_vectors: np.ndarray,
    map_vectors: np.ndarray,
    path: Path = DATABASE_PATH,
) -> pl.DataFrame:
    """Write the source columns plus fixed-size HRR and MAP vectors to LanceDB."""
    if hrr_vectors.shape != map_vectors.shape:
        raise ValueError("HRR and MAP matrices must have the same shape")
    if hrr_vectors.shape[0] != records.height:
        raise ValueError("vector count must match record count")
    if not np.isfinite(hrr_vectors).all() or not np.isfinite(map_vectors).all():
        raise ValueError("vectors must contain only finite values")

    dimensions = hrr_vectors.shape[1]
    vector_type = pa.list_(pa.float32(), dimensions)
    encoded = (
        records.to_arrow()
        .append_column("hrr_vector", pa.array(hrr_vectors.tolist(), type=vector_type))
        .append_column("map_vector", pa.array(map_vectors.tolist(), type=vector_type))
    )
    lancedb.connect(path).create_table(ENCODED_TABLE, encoded, mode="overwrite")
    frame = pl.from_arrow(encoded)
    if not isinstance(frame, pl.DataFrame):
        raise TypeError("expected a Polars DataFrame")
    return frame


def _validate_ids(frame: pl.DataFrame) -> None:
    if ID_COLUMN not in frame.columns:
        raise ValueError(f"missing required ID column {ID_COLUMN!r}")
    ids = frame[ID_COLUMN]
    if ids.null_count() or ids.n_unique() != frame.height:
        raise ValueError(f"{ID_COLUMN!r} must be non-null and unique")
