"""Public algebra API used by the teaching scripts and shared encoder."""

from __future__ import annotations

from typing import Literal

from .base import Algebra
from .hrr import HRR
from .map import MAP


def make_algebra(name: Literal["hrr", "map"], *, dimensions: int, seed: int) -> Algebra:
    """Choose the numerical implementation without branching inside the encoder."""
    if name == "hrr":
        return HRR(dimensions=dimensions, seed=seed)
    if name == "map":
        return MAP(dimensions=dimensions, seed=seed)
    raise ValueError(f"unknown algebra {name!r}; expected 'hrr' or 'map'")


__all__ = ["Algebra", "HRR", "MAP", "make_algebra"]
