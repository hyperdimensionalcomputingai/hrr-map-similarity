#!/usr/bin/env python3
"""Step 3: compare both spaces with source similarity and retrieval behavior."""

import json
from pathlib import Path

import numpy as np

from encoding import record_terms
from evaluation import pairwise_scores, retrieval_check, similarity_metrics
from storage import DATABASE_PATH, ENCODED_TABLE, ID_COLUMN, load_records
from visualization import plot_similarity

DATABASE = DATABASE_PATH
LIMIT = 20
TOP_K = 4
QUERY_COUNT = 6
ARTIFACTS = Path("artifacts")
FIGURES = ARTIFACTS / "figures"


def main() -> None:
    frame = load_records(DATABASE, table_name=ENCODED_TABLE, limit=LIMIT)
    records = frame.to_dicts()
    ids = [str(value) for value in frame[ID_COLUMN].to_list()]
    terms = [record_terms(record) for record in records]
    hrr_vectors = np.asarray(frame["hrr_vector"].to_list(), dtype=np.float32)
    map_vectors = np.asarray(frame["map_vector"].to_list(), dtype=np.float32)

    pairwise = pairwise_scores(ids, terms, hrr_vectors, map_vectors)
    similarity = similarity_metrics(pairwise)
    retrieval, disagreements, retrieval_metrics = retrieval_check(
        database_path=DATABASE,
        table_name=ENCODED_TABLE,
        id_column=ID_COLUMN,
        ids=ids,
        terms_by_id=dict(zip(ids, terms, strict=True)),
        hrr_vectors=hrr_vectors,
        map_vectors=map_vectors,
        top_k=TOP_K,
        query_count=QUERY_COUNT,
    )

    ARTIFACTS.mkdir(parents=True, exist_ok=True)
    pairwise.write_parquet(ARTIFACTS / "pairwise.parquet")
    retrieval.write_parquet(ARTIFACTS / "retrieval.parquet")
    disagreements.write_parquet(ARTIFACTS / "retrieval-disagreements.parquet")
    metrics = {
        "records": frame.height,
        "dimensions": hrr_vectors.shape[1],
        "similarity": similarity,
        "retrieval": retrieval_metrics,
    }
    (ARTIFACTS / "metrics.json").write_text(
        json.dumps(metrics, indent=2) + "\n", encoding="utf-8"
    )
    plot_similarity(
        pairwise,
        output_stem=FIGURES / "similarity-comparison",
        dimensions=hrr_vectors.shape[1],
    )

    print(json.dumps(metrics, indent=2))
    print(f"Wrote evaluation tables to {ARTIFACTS} and plots to {FIGURES}.")


if __name__ == "__main__":
    main()
