#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GitHub people sourcing pass.
Fail-safe for zero-row inputs.

Pipeline contract:
- Must expose run(context, **kwargs)
- Must be import-safe
- No argparse at import time
"""

import csv
from pathlib import Path
from typing import List, Dict, Any


def process_csv(input_csv: str, output_csv: str) -> None:
    in_path = Path(input_csv)
    out_path = Path(output_csv)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    rows: List[Dict[str, Any]] = []

    with in_path.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(row)

    # Zero-row safe path
    if not rows:
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


# -------------------------------------------------------------------
# Pipeline adapter (REQUIRED)
# -------------------------------------------------------------------

def run(context: Dict[str, Any], **kwargs) -> Dict[str, Any]:
    """
    Pipeline entrypoint.

    Expects context to contain:
      - input_csv
      - output_csv

    Returns context unchanged for pipeline chaining.
    """
    input_csv = context.get("input_csv")
    output_csv = context.get("output_csv")

    if not input_csv or not output_csv:
        raise ValueError("people_source_github requires 'input_csv' and 'output_csv' in context")

    process_csv(input_csv=input_csv, output_csv=output_csv)

    return context
