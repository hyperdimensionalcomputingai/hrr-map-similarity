#!/usr/bin/env python3
"""Step 2: run the same encoder once with HRR and once with MAP."""

from pathlib import Path

from algebra import make_algebra
from encoding import encode_all
from storage import DATABASE_PATH, load_records, write_encoded_vectors

# Both representations use the same dimension and seed for a fair comparison.
DATABASE = DATABASE_PATH
LIMIT = 20
DIMENSIONS = 4096
SEED = 2026
OUTPUT = Path("artifacts/encoded.parquet")


def main() -> None:
    frame = load_records(DATABASE, limit=LIMIT)
    records = frame.to_dicts()

    hrr = make_algebra("hrr", dimensions=DIMENSIONS, seed=SEED)
    map_ = make_algebra("map", dimensions=DIMENSIONS, seed=SEED)

    # These two calls differ only in the algebra object passed to the encoder.
    hrr_vectors = encode_all(records, hrr)
    map_vectors = encode_all(records, map_)

    encoded = write_encoded_vectors(frame, hrr_vectors, map_vectors, DATABASE)
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    encoded.write_parquet(OUTPUT)
    print(
        f"Encoded {frame.height} records at D={DIMENSIONS:,}; "
        f"wrote {OUTPUT} and the LanceDB vector table."
    )


if __name__ == "__main__":
    main()
