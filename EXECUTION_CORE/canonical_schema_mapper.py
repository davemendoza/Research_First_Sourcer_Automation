#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EXECUTION_CORE/canonical_schema_mapper.py
============================================================
CANONICAL SCHEMA MAPPER (81-COLUMN CONTRACT, DETERMINISTIC)

Maintainer: L. David Mendoza © 2026
Version: v1.0.0

Purpose
- Map an intermediate CSV into the canonical People schema format.
- This module does not enrich, scrape, or infer.
- It enforces a canonical column order and ensures all canonical columns exist.

Non-negotiable rules
- Deterministic: stable ordering, stable outputs.
- No guessing: never fabricate missing content.
- Fill missing canonical columns with empty strings only.
- Never drop existing columns. Non-canonical columns may be preserved after canonical columns.

Canonical schema source of truth
- Preferred: EXECUTION_CORE/CANONICAL_SCHEMA_81_COLUMNS_MACHINE.txt
  One column name per line.
- If absent: fail-closed with a clear message.

Contract
- process_csv(input_csv, output_csv) -> None

Changelog
- 2026-01-20: Initial canonical schema mapper with strict schema list file requirement.

Validation
python3 -m py_compile EXECUTION_CORE/canonical_schema_mapper.py
python3 -c "from EXECUTION_CORE.canonical_schema_mapper import load_canonical_schema_columns; print(len(load_canonical_schema_columns()))"

Git (SSH)
git add EXECUTION_CORE/canonical_schema_mapper.py
git commit -m "Add canonical schema mapper (deterministic 81-col order, fill-missing-only)"
git push
"""

from __future__ import annotations

import csv
import sys
from pathlib import Path
from typing import List, Dict, Tuple


REPO_ROOT = Path(__file__).resolve().parents[1]
EXEC_DIR = REPO_ROOT / "EXECUTION_CORE"
SCHEMA_LIST_PATH = EXEC_DIR / "CANONICAL_SCHEMA_81_COLUMNS_MACHINE.txt"


def die(msg: str) -> None:
    print(f"❌ [SCHEMA_MAPPER] {msg}", file=sys.stderr)
    raise SystemExit(1)


def load_canonical_schema_columns() -> List[str]:
    if not SCHEMA_LIST_PATH.exists():
        die(
            "Missing canonical schema list file:\n"
            f"  {SCHEMA_LIST_PATH}\n"
            "This file must contain one canonical column name per line."
        )

    cols: List[str] = []
    for raw in SCHEMA_LIST_PATH.read_text(encoding="utf-8").splitlines():
        s = raw.strip()
        if not s:
            continue
        if s.startswith("#"):
            continue
        cols.append(s)

    # Deterministic de-dupe preserving order
    seen = set()
    out: List[str] = []
    for c in cols:
        k = c.strip()
        lk = k.lower()
        if not k or lk in seen:
            continue
        seen.add(lk)
        out.append(k)

    if not out:
        die(f"Canonical schema list file is empty after parsing: {SCHEMA_LIST_PATH}")

    return out


def _read_csv(path: Path) -> Tuple[List[str], List[Dict[str, str]]]:
    with path.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        fieldnames = list(reader.fieldnames or [])
        rows = list(reader)
    if not fieldnames:
        die(f"Input CSV has no header: {path}")
    return fieldnames, rows


def _write_csv(path: Path, fieldnames: List[str], rows: List[Dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for r in rows:
            w.writerow({k: r.get(k, "") for k in fieldnames})


def process_csv(input_csv: str, output_csv: str) -> None:
    inp = Path(input_csv)
    outp = Path(output_csv)

    if not inp.exists():
        die(f"Input CSV not found: {inp}")

    canonical_cols = load_canonical_schema_columns()
    in_cols, rows = _read_csv(inp)

    in_cols_set = {c.lower(): c for c in in_cols}

    # Build canonical-ordered output columns
    out_cols: List[str] = []
    for c in canonical_cols:
        # If input has same name with different case, preserve canonical name (not input casing)
        out_cols.append(c)

    # Preserve any non-canonical input columns after canonical block, deterministic
    canon_lower = {c.lower() for c in canonical_cols}
    extras = [c for c in in_cols if c.lower() not in canon_lower]
    # Keep existing order from input (deterministic relative to input)
    out_cols.extend(extras)

    # Ensure every row has all canonical columns (fill blanks only)
    for r in rows:
        for c in canonical_cols:
            if c not in r or r.get(c) is None:
                r[c] = ""
        # Preserve extra columns as-is

    _write_csv(outp, out_cols, rows)


__all__ = ["process_csv", "load_canonical_schema_columns"]
