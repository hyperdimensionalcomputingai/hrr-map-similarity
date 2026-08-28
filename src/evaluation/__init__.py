"""Public API for source similarity, vector comparison, and retrieval checks."""

from .retrieval import pair_disagreements, retrieval_check
from .similarity import pairwise_scores, similarity_metrics, source_similarity

__all__ = [
    "pair_disagreements",
    "pairwise_scores",
    "retrieval_check",
    "similarity_metrics",
    "source_similarity",
]
