"""The small interface and deterministic atoms shared by HRR and MAP."""

from __future__ import annotations

import hashlib
from collections.abc import Sequence
from typing import Protocol

import torch


class Algebra(Protocol):
    """The four operations needed by the shared encoder."""

    dimensions: int

    def atom(self, key: str) -> torch.Tensor: ...

    def bind(self, left: torch.Tensor, right: torch.Tensor) -> torch.Tensor: ...

    def bundle(self, vectors: Sequence[torch.Tensor]) -> torch.Tensor: ...

    def normalize(self, vector: torch.Tensor) -> torch.Tensor: ...


def symbol_seed(algebra_name: str, dimensions: int, seed: int, key: str) -> int:
    """Derive a stable random seed for one symbol in one VSA space."""
    # Including the algebra name keeps HRR and MAP deterministic but independent.
    payload = f"{algebra_name}\0{dimensions}\0{seed}\0{key}".encode()
    digest = hashlib.blake2b(payload, digest_size=8).digest()
    # Torch accepts signed 64-bit seeds, so keep the derived value in that range.
    return int.from_bytes(digest, "little") % (2**63)
