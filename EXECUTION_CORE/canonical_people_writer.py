#!/usr/bin/env python3
"""
Canonical 81-column CSV writer
Write-only, schema-agnostic
"""

import csv
from typing import List, Dict

def write(rows: List[Dict[str, str]], output_path: str) -> None:
    if not rows:
        raise ValueError("No rows to write")

    fieldnames = list(rows[0].keys())

    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

# ---------------------------------------------------------------------
# Stable execution-layer compatibility wrapper
# Required by run_safe.py (DO NOT REMOVE)
# ---------------------------------------------------------------------
def write_canonical_people_csv(rows, output_path, *args, **kwargs):
    """
    Stable API expected by execution layer.
    Delegates to canonical people writer implementation.
    """
    return write(rows, output_path)
