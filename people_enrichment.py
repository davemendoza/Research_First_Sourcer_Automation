#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI Talent Engine | Phase-1 People Enrichment Output Normalizer (AUTHORITATIVE)

File: people_enrichment.py
Author: © 2026 L. David Mendoza. All rights reserved.
Version: v1.0.0-phase1-schema-parity-import-txt
Date: 2026-01-07

LOCKED PURPOSE
This module enforces Phase-1 output header parity with the locked canonical schema.

WHY THIS EXISTS
Canonical writer (EXECUTION_CORE/canonical_people_writer.py) must fail-closed if Phase-1 output
does not contain ALL required canonical headers. Historically, Phase-1 output drifted and omitted
headers, causing correct downstream aborts.

This file fixes that permanently by:
- Importing the canonical schema from EXECUTION_CORE/CANONICAL_SCHEMA_81_COLUMNS_MACHINE.txt
- Emitting all 81 canonical headers (even if values are blank)
- Preserving all existing row data
- Preserving any extra/non-canonical columns by appending them after canonical headers

IMPORTANT CONSTRAINTS
- This file does NOT perform enrichment logic. It normalizes the output contract only.
- It does NOT guess schemas. It fail-closes if the schema TXT is missing or invalid.

I/O CONTRACT
Input:  a CSV produced by upstream Phase-1/Track E enrichment (may contain partial headers)
Output: people_enriched.csv with:
  - canonical 81 headers present and ordered exactly as schema TXT
  - any extra input headers appended after canonical headers
  - per-row values preserved; missing canonical keys set to ""

Default paths:
- Input:  outputs/track_e/people_enriched.csv (if exists), else outputs/people/people_enriched.csv
- Output: outputs/track_e/people_enriched.csv
- Copy:   outputs/people/people_enriched.csv

CLI
python3 people_enrichment.py

Optional overrides:
python3 people_enrichment.py --input outputs/track_e/people_enriched.csv
python3 people_enrichment.py --outdir outputs/track_e

Changelog
- v1.0.0: First authoritative Phase-1 schema parity normalizer (TXT-imported canonical headers).

Validation
python3 -m py_compile people_enrichment.py
python3 people_enrichment.py --help

Git
git status
git add people_enrichment.py
git commit -m "Fix(phase1): enforce canonical 81-column header parity via TXT schema import"
git push
"""

from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path
from typing import List, Dict, Tuple


def _die(msg: str) -> None:
    print(f"ABORT: {msg}", file=sys.stderr)
    raise SystemExit(1)


def _load_schema_columns_txt(schema_path: Path, expected_count: int) -> List[str]:
    if not schema_path.exists():
        _die(f"Missing canonical schema TXT: {schema_path}")

    cols: List[str] = []
    for raw in schema_path.read_text(encoding="utf-8").splitlines():
        s = raw.strip()
        if not s or s.startswith("#"):
            continue
        cols.append(s)

    if len(cols) != expected_count:
        _die(
            f"Canonical schema TXT column count mismatch for {schema_path.name}: "
            f"expected {expected_count}, found {len(cols)}"
        )

    seen = set()
    dups = []
    for c in cols:
        if c in seen:
            dups.append(c)
        seen.add(c)
    if dups:
        _die(f"Duplicate columns in canonical schema TXT: {sorted(set(dups))}")

    return cols


def _pick_default_input() -> Path:
    # Prefer Track E output if present, otherwise fall back to outputs/people.
    p1 = Path("outputs/track_e/people_enriched.csv")
    p2 = Path("outputs/people/people_enriched.csv")
    if p1.exists():
        return p1
    if p2.exists():
        return p2
    _die("Could not find default input CSV. Expected outputs/track_e/people_enriched.csv or outputs/people/people_enriched.csv")


def _read_csv(path: Path) -> Tuple[List[str], List[Dict[str, str]]]:
    if not path.exists():
        _die(f"Input CSV missing: {path}")

    with path.open("r", encoding="utf-8", errors="replace", newline="") as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames or []
        rows = list(reader)

    if not fieldnames:
        _die(f"Input CSV has no header row: {path}")

    # Normalize header strings (strip only; do not rename)
    fieldnames = [h.strip() for h in fieldnames]
    return fieldnames, rows


def _write_csv(path: Path, headers: List[str], rows: List[Dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        for r in rows:
            # Preserve existing values; blank-fill missing keys deterministically.
            out = {h: (r.get(h, "") if r.get(h, "") is not None else "") for h in headers}
            writer.writerow(out)


def normalize_people_enriched_csv(input_csv: Path, outdir: Path) -> Tuple[Path, Path, int, int]:
    """
    Returns:
      (track_e_output_path, outputs_people_copy_path, rows_written, columns_written)
    """
    schema_txt = Path("EXECUTION_CORE/CANONICAL_SCHEMA_81_COLUMNS_MACHINE.txt")
    canonical = _load_schema_columns_txt(schema_txt, expected_count=81)

    in_headers, rows = _read_csv(input_csv)

    # Append any non-canonical headers after the canonical 81, preserving order.
    extras = [h for h in in_headers if h and (h not in canonical)]
    final_headers = canonical + extras

    # Ensure all rows expose canonical keys even if upstream never produced them.
    # (We do not mutate row dicts in-place, we blank-fill at write time.)

    out_track_e = outdir / "people_enriched.csv"
    out_people = Path("outputs/people/people_enriched.csv")

    _write_csv(out_track_e, final_headers, rows)
    _write_csv(out_people, final_headers, rows)

    return out_track_e, out_people, len(rows), len(final_headers)


def _build_argparser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description="Phase-1 schema parity normalizer: enforces canonical 81-column header presence via TXT schema import."
    )
    p.add_argument(
        "--input",
        dest="input_csv",
        default="",
        help="Input CSV path. Defaults to outputs/track_e/people_enriched.csv if present, else outputs/people/people_enriched.csv",
    )
    p.add_argument(
        "--outdir",
        dest="outdir",
        default="outputs/track_e",
        help="Output directory for Track E canonicalized people_enriched.csv (default outputs/track_e)",
    )
    return p


def main() -> None:
    args = _build_argparser().parse_args()

    input_csv = Path(args.input_csv).expanduser() if args.input_csv.strip() else _pick_default_input()
    outdir = Path(args.outdir).expanduser()

    out_track_e, out_people, rows_written, cols_written = normalize_people_enriched_csv(input_csv, outdir)

    print("OK: Phase-1 schema parity normalization complete")
    print(f" - Input:  {input_csv}")
    print(f" - Output: {out_track_e}")
    print(f" - Copy:   {out_people}")
    print(f" - Rows:   {rows_written}")
    print(f" - Cols:   {cols_written} (canonical 81 + extras if any)")


if __name__ == "__main__":
    main()
