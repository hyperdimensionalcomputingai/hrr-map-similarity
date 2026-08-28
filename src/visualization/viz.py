"""Small, publication-friendly figures for the teaching experiment."""

from __future__ import annotations

import os
import tempfile
from collections.abc import Sequence
from pathlib import Path

_matplotlib_cache = Path(tempfile.gettempdir()) / "hdc-experiments-matplotlib"
_matplotlib_cache.mkdir(parents=True, exist_ok=True)
os.environ.setdefault("MPLCONFIGDIR", str(_matplotlib_cache))

# Configure a writable cache before importing Matplotlib.
import matplotlib  # noqa: E402

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

BLUE = "#2563EB"
ORANGE = "#EA580C"
INK = "#172033"
MUTED = "#64748B"
GRID = "#D7DEE8"
BACKGROUND = "#F6F8FC"
STYLE = {
    "figure.facecolor": BACKGROUND,
    "axes.facecolor": "#FFFFFF",
    "axes.edgecolor": "#94A3B8",
    "axes.labelcolor": INK,
    "axes.titlecolor": INK,
    "axes.titleweight": "bold",
    "font.family": "sans-serif",
    "font.size": 10.5,
    "grid.color": GRID,
    "grid.linewidth": 0.8,
    "grid.alpha": 0.7,
    "legend.frameon": False,
    "xtick.color": "#475569",
    "ytick.color": "#475569",
}


def plot_similarity(
    pairwise: pl.DataFrame,
    *,
    output_stem: Path,
    dimensions: int,
) -> Path:
    """Show how both representations recover exact source similarity."""
    source = pairwise["source_similarity"].to_numpy()
    hrr = pairwise["hrr_cosine"].to_numpy()
    map_vectors = pairwise["map_cosine"].to_numpy()

    with plt.rc_context(STYLE):
        figure, axis = plt.subplots(figsize=(8.8, 5.6), constrained_layout=True)
        axis.scatter(source, hrr, s=30, alpha=0.55, color=BLUE, label="HRR")
        axis.scatter(
            source,
            map_vectors,
            s=30,
            alpha=0.55,
            color=ORANGE,
            marker="x",
            label="MAP",
        )
        score_min = float(min(source.min(), hrr.min(), map_vectors.min()))
        score_max = float(max(source.max(), hrr.max(), map_vectors.max()))
        axis.plot(
            [score_min, score_max],
            [score_min, score_max],
            color=MUTED,
            linestyle="--",
            linewidth=1.2,
            label="Ideal",
        )
        axis.set(
            title="Same encoder, different algebra",
            xlabel="Exact source similarity",
            ylabel="Hypervector cosine similarity",
        )
        axis.text(
            0.0,
            1.02,
            f"{dimensions:,} dimensions",
            transform=axis.transAxes,
            color=MUTED,
            fontsize=9.5,
        )
        _finish_axis(axis)
        axis.legend(loc="lower right")
        return _save(figure, output_stem)


def plot_dimension_sweep(
    sweep: pl.DataFrame,
    *,
    output_stem: Path,
    dimensions: Sequence[int],
) -> Path:
    """Plot only the two primary source-preservation curves across dimensions."""
    definitions = (
        ("hrr_vs_source", "HRR vs source", BLUE),
        ("map_vs_source", "MAP vs source", ORANGE),
    )
    x_positions = np.arange(len(dimensions), dtype=float)
    panel_values: list[float] = []

    with plt.rc_context(STYLE):
        figure, axis = plt.subplots(figsize=(9.4, 5.8), constrained_layout=True)
        for metric, label, color in definitions:
            means = []
            deviations = []
            for position, dimensions_value in zip(x_positions, dimensions, strict=True):
                values = (
                    sweep.filter(pl.col("dimensions") == dimensions_value)[metric]
                    .drop_nulls()
                    .to_numpy()
                )
                panel_values.extend(float(value) for value in values)
                means.append(float(np.mean(values)))
                deviations.append(
                    float(np.std(values, ddof=1)) if len(values) > 1 else 0.0
                )
                axis.scatter(
                    position + np.linspace(-0.045, 0.045, len(values)),
                    values,
                    s=28,
                    color=color,
                    alpha=0.28,
                    linewidths=0,
                )
            axis.errorbar(
                x_positions,
                means,
                yerr=deviations,
                color=color,
                label=label,
                marker="o",
                markersize=6,
                linewidth=2.2,
                capsize=4,
            )

        padding = max((max(panel_values) - min(panel_values)) * 0.1, 0.005)
        axis.set_ylim(min(panel_values) - padding, max(panel_values) + padding)
        axis.set_xticks(x_positions, [f"{value:,}" for value in dimensions])
        axis.set(
            title="How dimension affects source-geometry preservation",
            xlabel="Hypervector dimensions",
            ylabel="Pearson correlation with source similarity",
        )
        _finish_axis(axis)
        axis.legend(loc="lower right")
        return _save(figure, output_stem)


def _finish_axis(axis: plt.Axes) -> None:
    axis.grid(True)
    axis.set_axisbelow(True)
    axis.spines[["top", "right"]].set_visible(False)


def _save(figure: plt.Figure, output_stem: Path) -> Path:
    output_stem.parent.mkdir(parents=True, exist_ok=True)
    png_path = output_stem.with_suffix(".png")
    figure.savefig(png_path, dpi=200, facecolor=figure.get_facecolor())
    plt.close(figure)
    return png_path
