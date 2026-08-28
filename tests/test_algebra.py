from __future__ import annotations

import pytest
import torch

from algebra import make_algebra


def test_atoms_are_deterministic_and_distinct() -> None:
    for name in ("hrr", "map"):
        first = make_algebra(name, dimensions=512, seed=7)
        second = make_algebra(name, dimensions=512, seed=7)
        assert torch.equal(first.atom("tea"), second.atom("tea"))
        assert not torch.equal(first.atom("tea"), first.atom("coffee"))


def test_both_algebras_expose_the_same_shapes() -> None:
    for name in ("hrr", "map"):
        algebra = make_algebra(name, dimensions=512, seed=7)
        left = algebra.atom("left")
        right = algebra.atom("right")
        bound = algebra.bind(left, right)
        bundled = algebra.bundle([bound, algebra.atom("third")])
        normalized = algebra.normalize(bundled)
        assert bound.shape == bundled.shape == normalized.shape == (512,)
        assert torch.linalg.vector_norm(normalized).item() == pytest.approx(1.0)
