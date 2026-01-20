#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EXECUTION_CORE/canonical_people_writer.py
============================================================
CANONICAL PEOPLE WRITER (INTERVIEW-SAFE, DETERMINISTIC)

Maintainer: L. David Mendoza © 2026
Version: v1.0.0

Purpose
- Write the final canonical People CSV artifact for a run.
- Enforce canonical column order using canonical_schema_mapper.
- Write a metadata JSON artifact for audit and replay.
- Never overwrite an existing canonical output file.

Non-negotiable rules
- Deterministic output file naming (caller supplies fixed_filename and timestamp)
- Deterministic column ordering via canonical_schema_mapper
- No enrichment, no inference, no scraping
- Fail-closed on missing inputs, empty headers, or attempted overwrite

Contract
- write_canonical_people_csv(
    canonical_csv_path: str,
    output_dir: str,
    output_prefix: str,
    timestamp: str,
    fixed_filename: str,
    pipeline_version: str,
    metadata_json_path: str
  ) -> str

Changelog
- 2026-01-20: Initial canonical writer with schema mapping + metadata.

Validation
python3 -m py_compile EXECUTION_CORE/canonical_people_writer.py

Git (SSH)
git add EXECUTION_CORE/canonical_people_writer.py
git commit -m "Add canonical people writer (schema-ordered CSV + metadata, no overwrite)"
git push
"""

from __future__ import annotations

import csv
import hashlib
import json
import sys
from pathlib import Path
from typing import Dict, Any, List, Tuple

from EXECUTION_CORE.canonical_schema_mapper import process_csv as map_to_canonical_schema


def die(msg: str) -> None:
    print(f"❌ [CANONICAL_WRITER] {msg}", file=sys.stderr)
    raise SystemExit(1)


def _sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def _count_rows(path: Path) -> int:
    try:
        with path.open(newline="", encoding="utf-8") as f:
            r = csv.reader(f)
            _ = next(r, None)
            return sum(1 for _ in r)
    except Exception:
        return -1


def write_canonical_people_csv(
    *,
    canonical_csv_path: str,
    output_dir: str,
    output_prefix: str,
    timestamp: str,
    fixed_filename: str,
    pipeline_version: str,
    metadata_json_path: str,
) -> str:
    inp = Path(canonical_csv_path)
    out_dir = Path(output_dir)
    out_csv = out_dir / fixed_filename
    meta_path = Path(metadata_json_path)

    if not inp.exists():
        die(f"Input CSV not found: {inp}")

    out_dir.mkdir(parents=True, exist_ok=True)
    meta_path.parent.mkdir(parents=True, exist_ok=True)

    if out_csv.exists():
        die(f"Refusing to overwrite existing canonical CSV: {out_csv}")

    # First map to canonical schema into a temp file in the same output dir
    tmp = out_dir / f".tmp_{output_prefix}_{timestamp}_schema_mapped.csv"
    if tmp.exists():
        try:
            tmp.unlink()
        except Exception:
            die(f"Temp file exists and cannot be removed: {tmp}")

    map_to_canonical_schema(str(inp), str(tmp))

    if not tmp.exists():
        die(f"Schema-mapped temp CSV not created: {tmp}")

    # Move temp into final canonical filename (atomic on same filesystem)
    try:
        tmp.replace(out_csv)
    except Exception as e:
        die(f"Failed to finalize canonical CSV: {e}")

    rows = _count_rows(out_csv)
    sha = _sha256_file(out_csv)

    metadata: Dict[str, Any] = {
        "artifact_type": "canonical_people_csv",
        "pipeline_version": pipeline_version,
        "timestamp": timestamp,
        "output_prefix": output_prefix,
        "canonical_csv_path": str(out_csv),
        "rows": rows,
        "sha256": sha,
    }

    meta_path.write_text(json.dumps(metadata, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    return str(out_csv)


__all__ = ["write_canonical_people_csv"]
