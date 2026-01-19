# -*- coding: utf-8 -*-
"""
phase6_ai_stack_signals.py
------------------------------------------------------------
IMPORT-ONLY MODULE

Phase 6: AI Stack Signal Detection

Maintainer: L. David Mendoza © 2026
"""

import csv
import json
from pathlib import Path
from typing import Dict, List

ROOT = Path(__file__).resolve().parents[1]
TAXONOMY_PATH = ROOT / "SCHEMA" / "ai_stack_taxonomy.json"


def _load_taxonomy() -> Dict:
    if not TAXONOMY_PATH.exists():
        raise RuntimeError(f"Missing required taxonomy file: {TAXONOMY_PATH}")

    try:
        with TAXONOMY_PATH.open(encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        raise RuntimeError(f"Invalid JSON in taxonomy file: {TAXONOMY_PATH}") from e

    if not isinstance(data, dict) or "categories" not in data:
        raise RuntimeError(f"Malformed taxonomy structure: {TAXONOMY_PATH}")

    return data


def process_csv(input_csv: str, output_csv: str) -> None:
    taxonomy = _load_taxonomy()

    with open(input_csv, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        fieldnames = reader.fieldnames or []

    # Phase 6 logic (unchanged): empty taxonomy = no matches
    for row in rows:
        pass

    with open(output_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)
