#!/usr/bin/env python3
"""Step 4: repeat the source-similarity benchmark across dimensions and seeds."""

from pathlib import Path

import polars as pl

from algebra import make_algebra
from encoding import encode_all, record_terms
from evaluation import pairwise_scores, similarity_metrics
from storage import DATABASE_PATH, ID_COLUMN, load_records
from visualization import plot_dimension_sweep

# Edit these lists directly; the sweep changes no other part of the experiment.
DATABASE = DATABASE_PATH
LIMIT = 20
DIMENSIONS = [512, 1024, 2048, 4096, 8192, 10000]
SEEDS = [2026, 2027, 2028, 2029, 2030]
OUTPUT = Path("artifacts/sweep.parquet")
FIGURE = Path("artifacts/figures/dimension-sweep")


def main() -> None:
    frame = load_records(DATABASE, limit=LIMIT)
    records = frame.to_dicts()
    ids = [str(value) for value in frame[ID_COLUMN].to_list()]
    terms = [record_terms(record) for record in records]
    rows = []

    for dimensions in DIMENSIONS:
        for seed in SEEDS:
            hrr = make_algebra("hrr", dimensions=dimensions, seed=seed)
            map_ = make_algebra("map", dimensions=dimensions, seed=seed)
            hrr_vectors = encode_all(records, hrr)
            map_vectors = encode_all(records, map_)
            pairwise = pairwise_scores(ids, terms, hrr_vectors, map_vectors)
            metrics = similarity_metrics(pairwise)
            rows.append({"dimensions": dimensions, "seed": seed, **metrics})
            print(
                f"D={dimensions:>5}, seed={seed}: "
                f"HRR/source={metrics['hrr_vs_source']:.4f}, "
                f"MAP/source={metrics['map_vs_source']:.4f}"
            )

    sweep = pl.DataFrame(rows).sort(["dimensions", "seed"])
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    sweep.write_parquet(OUTPUT)
    plot_dimension_sweep(sweep, output_stem=FIGURE, dimensions=DIMENSIONS)

    summary = (
        sweep.group_by("dimensions")
        .agg(
            pl.col("hrr_vs_source").mean().alias("mean_hrr_vs_source"),
            pl.col("map_vs_source").mean().alias("mean_map_vs_source"),
        )
        .sort("dimensions")
    )
    print(f"\n{summary}")
    print(f"Wrote {OUTPUT} and {FIGURE.with_suffix('.png')}.")


if __name__ == "__main__":
    main()
