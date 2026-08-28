"""MAP operations: bipolar atoms and element-wise binding."""

from __future__ import annotations

from collections.abc import Sequence

import torch
import torch.nn.functional as torch_functional
import torchhd

from .base import symbol_seed


class MAP:
    """MAP algebra with multiplication binding and additive bundling."""

    def __init__(self, *, dimensions: int, seed: int) -> None:
        if dimensions < 2:
            raise ValueError("dimensions must be at least 2")
        self.dimensions = dimensions
        self.seed = seed

    def atom(self, key: str) -> torch.Tensor:
        generator = torch.Generator(device="cpu").manual_seed(
            symbol_seed("map", self.dimensions, self.seed, key)
        )
        return torchhd.random(
            1,
            self.dimensions,
            vsa="MAP",
            generator=generator,
            dtype=torch.float32,
        )[0]

    def bind(self, left: torch.Tensor, right: torch.Tensor) -> torch.Tensor:
        return left * right

    def bundle(self, vectors: Sequence[torch.Tensor]) -> torch.Tensor:
        if not vectors:
            raise ValueError("cannot bundle an empty collection")
        return torch.stack(tuple(vectors)).sum(dim=0)

    def normalize(self, vector: torch.Tensor) -> torch.Tensor:
        return torch_functional.normalize(vector, dim=0)
