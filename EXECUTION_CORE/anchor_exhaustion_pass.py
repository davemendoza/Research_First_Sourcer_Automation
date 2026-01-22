#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Anchor exhaustion pass.
Expands navigation anchors into initial people rows.
Fail-safe for zero-row outcomes.
"""

import csv
from pathlib import Path
from typing import List, Dict, Any


def process_csv(input_csv: str, output_csv: str) -> None:
    in_path = Path(input_csv)
    out_path = Path(output_csv)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    rows: List[Dict[str, Any]] = []

    # Read input (navigation-only seeds may be empty by design)
    with in_path.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(row)

    # If no rows, write a valid empty CSV with headers only
    if not rows:
        # Preserve header intent if present, otherwise write empty file
        fieldnames = reader.fieldnames if reader.fieldnames else []
        with out_path.open("w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            if fieldnames:
                writer.writeheader()
        return

    # Normal path
    with out_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)
