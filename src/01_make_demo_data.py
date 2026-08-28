#!/usr/bin/env python3
"""Step 1: copy the inspectable JSON fixture into LanceDB."""

from storage import DATABASE_PATH, RAW_DATA_PATH, SOURCE_TABLE, create_demo_dataset

# Edit these values when replacing the demo dataset.
RAW_JSON = RAW_DATA_PATH
DATABASE = DATABASE_PATH
LIMIT = 20


def main() -> None:
    row_count = create_demo_dataset(DATABASE, raw_path=RAW_JSON, n=LIMIT)
    print(f"Wrote {row_count} records to {DATABASE} in table {SOURCE_TABLE!r}.")


if __name__ == "__main__":
    main()
