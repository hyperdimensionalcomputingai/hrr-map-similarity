from __future__ import annotations

from evaluation import pair_disagreements


def test_disagreements_match_equal_source_scores_first() -> None:
    hrr_only = [
        {"result_id": "A", "rank": 3, "source_similarity": 0.25},
        {"result_id": "B", "rank": 4, "source_similarity": 0.50},
    ]
    map_only = [
        {"result_id": "C", "rank": 3, "source_similarity": 0.50},
        {"result_id": "D", "rank": 4, "source_similarity": 0.10},
    ]
    disagreements = pair_disagreements("Q", hrr_only, map_only)
    tied = [item for item in disagreements if item["inside_source_tie"]]
    assert len(tied) == 1
    assert tied[0]["hrr_result_id"] == "B"
    assert tied[0]["map_result_id"] == "C"
