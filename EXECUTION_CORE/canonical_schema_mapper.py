#!/usr/bin/env python3
"""
Canonical Schema Mapper
Anchors schema paths relative to this file (execution-safe).
"""

import sys
import csv
from pathlib import Path

HERE = Path(__file__).resolve().parent
CANONICAL_SCHEMA_PATH = HERE / "CANONICAL_SCHEMA_81_COLUMNS_MACHINE.txt"

def load_canonical_schema(path: Path):
    if not path.exists():
        raise FileNotFoundError(f"Canonical schema not found: {path}")
    with open(path, encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip()]

def process_csv(input_csv, output_csv):
    schema = load_canonical_schema(CANONICAL_SCHEMA_PATH)

    with open(input_csv, newline="", encoding="utf-8") as fin:
        reader = csv.DictReader(fin)
        rows = list(reader)

    with open(output_csv, "w", newline="", encoding="utf-8") as fout:
        writer = csv.DictWriter(fout, fieldnames=schema)
        writer.writeheader()
        for row in rows:
            writer.writerow({k: row.get(k, "") for k in schema})

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: canonical_schema_mapper.py <input_csv> <output_csv>", file=sys.stderr)
        sys.exit(1)

    process_csv(sys.argv[1], sys.argv[2])
