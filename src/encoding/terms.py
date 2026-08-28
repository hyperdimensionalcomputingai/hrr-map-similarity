"""Translate tea records into the exact facts the encoder should preserve."""

from __future__ import annotations

import math
from collections.abc import Mapping
from typing import Any

type Term = tuple[str, str]
CATEGORICAL_FIELDS = ("tea_type", "origin", "oxidation", "roast")
ELEVATION_BIN_METERS = 500


def record_terms(record: Mapping[str, Any]) -> tuple[Term, ...]:
    """Translate one tea row into deterministic role-value terms."""
    terms: set[Term] = set()

    for role in CATEGORICAL_FIELDS:
        value = _normalize(record.get(role))
        if value:
            terms.add((role, value))

    aroma_notes = record.get("aroma_notes") or []
    if isinstance(aroma_notes, (str, bytes)):
        raise TypeError("'aroma_notes' must be a list of strings")
    # Aroma words use exact identity semantics in this experiment.
    for note in aroma_notes:
        value = _normalize(note)
        if value:
            terms.add(("aroma_notes", value))

    elevation = record.get("elevation_m")
    if elevation is not None and math.isfinite(float(elevation)):
        # The bin makes nearby elevations the same categorical fact.
        start = math.floor(float(elevation) / ELEVATION_BIN_METERS)
        start *= ELEVATION_BIN_METERS
        terms.add(("elevation_m", f"[{start},{start + ELEVATION_BIN_METERS})"))

    if not terms:
        raise ValueError("record produced no role-value terms")
    # Sorting makes repeated runs independent of source dictionary ordering.
    return tuple(sorted(terms))


def _normalize(value: Any) -> str:
    if value is None:
        return ""
    return " ".join(str(value).strip().casefold().split())
