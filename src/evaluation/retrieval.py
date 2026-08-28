"""Small LanceDB retrieval check with a source-tie disagreement audit."""

from __future__ import annotations

import math
from collections.abc import Mapping, Sequence
from pathlib import Path

import lancedb
import numpy as np
import polars as pl

from encoding import Term

from .similarity import source_similarity


def retrieval_check(
    *,
    database_path: Path,
    table_name: str,
    id_column: str,
    ids: Sequence[str],
    terms_by_id: Mapping[str, Sequence[Term]],
    hrr_vectors: np.ndarray,
    map_vectors: np.ndarray,
    top_k: int,
    query_count: int,
) -> tuple[pl.DataFrame, pl.DataFrame, dict[str, object]]:
    """Query both vector columns and audit exact and tie-aware top-k agreement."""
    if top_k < 1 or query_count < 1:
        raise ValueError("top_k and query_count must be positive")
    top_k = min(top_k, len(ids) - 1)
    table = lancedb.connect(database_path).open_table(table_name)
    # Even spacing gives a deterministic sample that includes both ends of the table.
    query_indices = np.unique(
        np.linspace(0, len(ids) - 1, min(query_count, len(ids)), dtype=int)
    )

    rows: list[dict[str, object]] = []
    rankings: dict[str, dict[str, list[dict[str, object]]]] = {}
    for query_index in query_indices:
        query_id = ids[int(query_index)]
        rankings[query_id] = {}
        for name, column, vectors in (
            ("HRR", "hrr_vector", hrr_vectors),
            ("MAP", "map_vector", map_vectors),
        ):
            result = (
                table.search(vectors[int(query_index)], vector_column_name=column)
                .distance_type("cosine")
                .select([id_column, "_distance"])
                .limit(min(top_k + 1, len(ids)))
                .to_arrow()
            )
            candidates = [
                (str(candidate_id), float(distance))
                for candidate_id, distance in zip(
                    result[id_column].to_pylist(),
                    result["_distance"].to_pylist(),
                    strict=True,
                )
                if str(candidate_id) != query_id
            ][:top_k]

            ranked_results = []
            for rank, (candidate_id, distance) in enumerate(candidates, start=1):
                source = source_similarity(
                    terms_by_id[query_id], terms_by_id[candidate_id]
                )
                ranked = {
                    "result_id": candidate_id,
                    "rank": rank,
                    "source_similarity": source,
                }
                ranked_results.append(ranked)
                rows.append(
                    {
                        "query_id": query_id,
                        "representation": name,
                        **ranked,
                        "cosine": 1.0 - distance,
                    }
                )
            rankings[query_id][name] = ranked_results

    disagreements: list[dict[str, object]] = []
    per_query = []
    for query_id, results in rankings.items():
        hrr_ids = {str(item["result_id"]) for item in results["HRR"]}
        map_ids = {str(item["result_id"]) for item in results["MAP"]}
        common_ids = hrr_ids & map_ids
        hrr_only = [
            item for item in results["HRR"] if str(item["result_id"]) not in common_ids
        ]
        map_only = [
            item for item in results["MAP"] if str(item["result_id"]) not in common_ids
        ]
        pairs = pair_disagreements(query_id, hrr_only, map_only)
        disagreements.extend(pairs)
        tied_count = sum(bool(item["inside_source_tie"]) for item in pairs)
        per_query.append(
            {
                "query_id": query_id,
                "raw_overlap": len(common_ids) / top_k,
                "tie_aware_overlap": (len(common_ids) + tied_count) / top_k,
                "disagreement_slots": len(pairs),
                "source_tie_slots": tied_count,
            }
        )

    disagreement_count = sum(int(item["disagreement_slots"]) for item in per_query)
    tied_count = sum(int(item["source_tie_slots"]) for item in per_query)
    metrics: dict[str, object] = {
        "top_k": top_k,
        "query_ids": [item["query_id"] for item in per_query],
        "raw_top_k_overlap": float(
            np.mean([item["raw_overlap"] for item in per_query])
        ),
        "tie_aware_top_k_overlap": float(
            np.mean([item["tie_aware_overlap"] for item in per_query])
        ),
        "disagreement_slots": disagreement_count,
        "source_tie_slots": tied_count,
        "source_tie_share_of_disagreements": (
            tied_count / disagreement_count if disagreement_count else None
        ),
        "per_query": per_query,
    }
    return pl.DataFrame(rows), _disagreement_frame(disagreements), metrics


def pair_disagreements(
    query_id: str,
    hrr_only: Sequence[Mapping[str, object]],
    map_only: Sequence[Mapping[str, object]],
) -> list[dict[str, object]]:
    """Pair exclusive results, matching equal source scores whenever possible."""
    if len(hrr_only) != len(map_only):
        raise ValueError("HRR-only and MAP-only result counts must match")

    remaining_map = list(map_only)
    matched: list[tuple[Mapping[str, object], Mapping[str, object], bool]] = []
    unmatched_hrr = []
    for hrr_item in hrr_only:
        hrr_score = float(hrr_item["source_similarity"])
        match_index = next(
            (
                index
                for index, map_item in enumerate(remaining_map)
                if math.isclose(
                    hrr_score,
                    float(map_item["source_similarity"]),
                    rel_tol=0.0,
                    abs_tol=1e-12,
                )
            ),
            None,
        )
        if match_index is None:
            unmatched_hrr.append(hrr_item)
        else:
            matched.append((hrr_item, remaining_map.pop(match_index), True))

    matched.extend(
        (hrr_item, map_item, False)
        for hrr_item, map_item in zip(unmatched_hrr, remaining_map, strict=True)
    )
    return [
        {
            "query_id": query_id,
            "pair_index": pair_index,
            "hrr_result_id": str(hrr_item["result_id"]),
            "hrr_rank": int(hrr_item["rank"]),
            "hrr_source_similarity": float(hrr_item["source_similarity"]),
            "map_result_id": str(map_item["result_id"]),
            "map_rank": int(map_item["rank"]),
            "map_source_similarity": float(map_item["source_similarity"]),
            "source_delta": abs(
                float(hrr_item["source_similarity"])
                - float(map_item["source_similarity"])
            ),
            "inside_source_tie": inside_source_tie,
        }
        for pair_index, (hrr_item, map_item, inside_source_tie) in enumerate(
            matched, start=1
        )
    ]


def _disagreement_frame(rows: list[dict[str, object]]) -> pl.DataFrame:
    if rows:
        return pl.DataFrame(rows)
    return pl.DataFrame(
        schema={
            "query_id": pl.String,
            "pair_index": pl.Int64,
            "hrr_result_id": pl.String,
            "hrr_rank": pl.Int64,
            "hrr_source_similarity": pl.Float64,
            "map_result_id": pl.String,
            "map_rank": pl.Int64,
            "map_source_similarity": pl.Float64,
            "source_delta": pl.Float64,
            "inside_source_tie": pl.Boolean,
        }
    )
