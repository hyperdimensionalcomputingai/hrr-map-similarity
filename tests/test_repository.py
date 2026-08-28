from __future__ import annotations

from pathlib import Path

import polars as pl

from storage import RAW_DATA_PATH


def test_raw_fixture_is_inspectable_json() -> None:
    frame = pl.read_json(RAW_DATA_PATH)
    assert frame.height == 20
    assert frame["sample_id"].n_unique() == 20
    assert frame.schema["aroma_notes"] == pl.List(pl.String)


def test_project_source_does_not_import_pandas_or_scipy() -> None:
    source_root = Path(__file__).resolve().parents[1] / "src"
    source = "\n".join(path.read_text() for path in source_root.rglob("*.py"))
    assert "import pandas" not in source
    assert "from pandas" not in source
    assert "import scipy" not in source
    assert "from scipy" not in source
