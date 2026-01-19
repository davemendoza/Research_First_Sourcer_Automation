# -*- coding: utf-8 -*-
"""
canonical_schema_mapper.py
------------------------------------------------------------
IMPORT-ONLY MODULE (NOT EXECUTABLE)

Maintainer: L. David Mendoza © 2026
Version: v1.1.0

Purpose
- Project any intermediate CSV into the canonical 81-column schema (deterministic order)
- Preserve values for canonical columns, drop non-canonical columns
- No fabrication

Schema Source of Truth
- EXECUTION_CORE/CANONICAL_SCHEMA_81_COLUMNS_MACHINE.txt (one column name per line)

Validation
python3 -c "from EXECUTION_CORE.canonical_schema_mapper import load_canonical_schema; import pathlib; print(len(load_canonical_schema()))"

Git Commands
git add EXECUTION_CORE/canonical_schema_mapper.py
git commit -m "Fix canonical schema mapper: import-only valid python, deterministic 81-column projection"
git push
"""

from __future__ import annotations

import csv
from pathlib import Path
from typing import List


HERE = Path(__file__).resolve().parent
CANONICAL_SCHEMA_PATH = HERE / "CANONICAL_SCHEMA_81_COLUMNS_MACHINE.txt"


def load_canonical_schema(path: Path = CANONICAL_SCHEMA_PATH) -> List[str]:
    if not path.exists():
        raise FileNotFoundError(f"Canonical schema not found: {path}")
    cols: List[str] = []
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        c = line.strip()
        if not c or c.startswith("#"):
            continue
        cols.append(c)
    if not cols:
        raise ValueError(f"Canonical schema file is empty: {path}")
    return cols


def process_csv(input_csv: str | Path, output_csv: str | Path, schema_path: Path = CANONICAL_SCHEMA_PATH) -> None:
    schema = load_canonical_schema(schema_path)

    inp = Path(input_csv)
    outp = Path(output_csv)
    outp.parent.mkdir(parents=True, exist_ok=True)

    with inp.open(newline="", encoding="utf-8") as fin:
        reader = csv.DictReader(fin)
        rows = list(reader)

    with outp.open("w", newline="", encoding="utf-8") as fout:
        writer = csv.DictWriter(fout, fieldnames=schema)
        writer.writeheader()
        for row in rows:
            writer.writerow({k: row.get(k, "") for k in schema})
