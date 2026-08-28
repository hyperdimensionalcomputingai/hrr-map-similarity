"""One logical encoder shared unchanged by HRR and MAP."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

import numpy as np
import torch

from algebra import Algebra

from .terms import Term, record_terms


def encode_terms(terms: Sequence[Term], algebra: Algebra) -> torch.Tensor:
    """Bind each role to its value, then bundle all facts into one hypervector."""
    bound = []
    for role, value in terms:
        role_vector = algebra.atom(f"role:{role}")
        # Role-qualified values keep identical text in different fields distinct.
        value_vector = algebra.atom(f"value:{role}:{value}")
        bound.append(algebra.bind(role_vector, value_vector))
    return algebra.normalize(algebra.bundle(bound))


def encode_record(record: Mapping[str, Any], algebra: Algebra) -> torch.Tensor:
    """Encode one record through the same path for every algebra."""
    return encode_terms(record_terms(record), algebra)


def encode_all(records: Sequence[Mapping[str, Any]], algebra: Algebra) -> np.ndarray:
    """Encode records and return a storage-friendly NumPy matrix."""
    with torch.inference_mode():
        vectors = torch.stack([encode_record(record, algebra) for record in records])
    return vectors.as_subclass(torch.Tensor).cpu().numpy()
