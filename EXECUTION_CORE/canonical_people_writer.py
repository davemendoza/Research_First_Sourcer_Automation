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
