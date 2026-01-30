#!/usr/bin/env python3
# ==============================================================================
# AI TALENT ENGINE – SIGNAL INTELLIGENCE
# Proprietary and Confidential
# © 2025–2026 L. David Mendoza. All Rights Reserved.
# ==============================================================================
#
# This file contains proprietary intellectual property and trade secrets of
# L. David Mendoza and is part of the AI Talent Engine – Signal Intelligence system.
#
# Unauthorized access, use, copying, modification, distribution, disclosure,
# reverse engineering, or derivative use, in whole or in part, is strictly
# prohibited without prior written authorization.
#
# ==============================================================================

# -*- coding: utf-8 -*-
"""
EXECUTION_CORE/people_source_github.py

GitHub people sourcing pass.

Contract compatibility:
- process_csv(input_csv: str, output_csv: str) -> None
- run(input_csv: str, output_csv: str) -> None   (required by run_people_pipeline.py)

Design rules
- Deterministic
- Fail-safe for zero-row inputs
- No network calls
"""

import csv
from pathlib import Path
from typing import Any, Dict, List


def process_csv(input_csv: str, output_csv: str) -> None:
    in_path = Path(input_csv)
    out_path = Path(output_csv)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    rows: List[Dict[str, Any]] = []

    with in_path.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(row)

    # Zero-row safe path: write header-only CSV if headers exist
    if not rows:
        fieldnames = reader.fieldnames if reader.fieldnames else []
        with out_path.open("w", newline="", encoding="utf-8") as f_out:
            writer = csv.DictWriter(f_out, fieldnames=fieldnames)
            if fieldnames:
                writer.writeheader()
        return

    # Normal path: pass-through write
    with out_path.open("w", newline="", encoding="utf-8") as f_out:
        writer = csv.DictWriter(f_out, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def run(input_csv: str, output_csv: str) -> None:
    """
    Backward-compatible alias required by EXECUTION_CORE/run_people_pipeline.py.
    """
    process_csv(input_csv, output_csv)


__all__ = ["process_csv", "run"]
