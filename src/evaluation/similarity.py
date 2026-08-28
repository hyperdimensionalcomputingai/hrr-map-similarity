"""Compare both vector spaces with the exact source-level geometry."""

from __future__ import annotations

import math
from collections.abc import Sequence

import numpy as np
import polars as pl

from encoding import Term


def source_similarity(left: Sequence[Term], right: Sequence[Term]) -> float:
    """Measure exact role-value overlap in an explicit one-hot space."""
    left_set = set(left)
    right_set = set(right)
    return len(left_set & right_set) / math.sqrt(len(left_set) * len(right_set))


def pairwise_scores(
    ids: Sequence[str],
    terms: Sequence[Sequence[Term]],
    hrr_vectors: np.ndarray,
    map_vectors: np.ndarray,
) -> pl.DataFrame:
    """Calculate source, HRR, and MAP similarity for every record pair."""
    rows: list[dict[str, object]] = []
    for left in range(len(ids)):
        for right in range(left + 1, len(ids)):
            source = source_similarity(terms[left], terms[right])
            rows.append(
                {
                    "id_left": ids[left],
                    "id_right": ids[right],
                    "source_similarity": source,
                    "hrr_cosine": float(np.dot(hrr_vectors[left], hrr_vectors[right])),
                    "map_cosine": float(np.dot(map_vectors[left], map_vectors[right])),
                }
            )
    return pl.DataFrame(rows)


def similarity_metrics(pairwise: pl.DataFrame) -> dict[str, float]:
    """Summarize how well both spaces preserve source similarity."""
    source = pairwise["source_similarity"].to_numpy()
    hrr = pairwise["hrr_cosine"].to_numpy()
    map_vectors = pairwise["map_cosine"].to_numpy()
    return {
        "hrr_vs_source": _correlation(hrr, source),
        "map_vs_source": _correlation(map_vectors, source),
        "hrr_vs_map": _correlation(hrr, map_vectors),
        "hrr_source_mae": float(np.mean(np.abs(hrr - source))),
        "map_source_mae": float(np.mean(np.abs(map_vectors - source))),
    }


def _correlation(left: np.ndarray, right: np.ndarray) -> float:
    return float(np.corrcoef(left, right)[0, 1])
