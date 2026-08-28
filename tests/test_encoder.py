from __future__ import annotations

import pytest
import torch

from algebra import make_algebra
from encoding import encode_record, record_terms
from evaluation import source_similarity

RECORD = {
    "tea_type": "Black",
    "origin": "India",
    "oxidation": "high",
    "roast": "none",
    "aroma_notes": ["Floral", "muscatel", "citrus"],
    "elevation_m": 1900,
}


def test_record_terms_make_exact_source_facts() -> None:
    terms = record_terms(RECORD)
    assert len(terms) == 8
    assert ("aroma_notes", "floral") in terms
    assert ("elevation_m", "[1500,2000)") in terms


def test_same_encoder_function_accepts_both_algebras() -> None:
    hrr = make_algebra("hrr", dimensions=512, seed=1)
    map_ = make_algebra("map", dimensions=512, seed=1)
    hrr_vector = encode_record(RECORD, hrr)
    map_vector = encode_record(RECORD, map_)
    assert hrr_vector.shape == map_vector.shape == (512,)
    assert torch.linalg.vector_norm(hrr_vector).item() == pytest.approx(1.0)
    assert torch.linalg.vector_norm(map_vector).item() == pytest.approx(1.0)


def test_source_similarity_counts_exact_matches_only() -> None:
    left = (("aroma_notes", "floral"), ("tea_type", "black"))
    right = (("aroma_notes", "orchid"), ("tea_type", "black"))
    assert source_similarity(left, right) == pytest.approx(0.5)
