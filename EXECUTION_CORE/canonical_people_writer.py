#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EXECUTION_CORE/canonical_people_writer.py
============================================================
WRITER-OF-RECORD (SINGLE OUTPUT, DETERMINISTIC, PROVENANCE)

Maintainer: L. David Mendoza © 2026
Version: v3.0.1 (EOF sanitation + stable contract)

Contract (LOCKED)
- Requires timestamp (string) for provenance
- Writes exactly one canonical CSV per run
- Returns absolute output CSV path (string)
- Atomic write (tmp -> replace)
- Emits metadata JSON

Never:
- fabricate data
- guess output paths outside caller's output_dir
"""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Optional, Dict, Any


def _atomic_write_csv(rows: list[dict], fieldnames: list[str], out_path: Path) -> None:
    tmp = out_path.with_suffix(out_path.suffix + ".tmp")
    with tmp.open("w", newline="", encoding="utf-8") as fout:
        writer = csv.DictWriter(fout, fieldnames=fieldnames)
        writer.writeheader()
        for r in rows:
            writer.writerow({k: r.get(k, "") for k in fieldnames})
    tmp.replace(out_path)


def write_canonical_people_csv(
    *,
    canonical_csv_path: str | Path,
    output_dir: str | Path,
    output_prefix: str,
    timestamp: str,
    fixed_filename: Optional[str] = None,
    pipeline_version: str = "D30_LOCKED_GOLD_FINAL",
    metadata_json_path: Optional[str | Path] = None,
) -> str:
    if not isinstance(timestamp, str) or not timestamp.strip():
        raise RuntimeError("write_canonical_people_csv: 'timestamp' is required and must be a non-empty string")
    if not isinstance(output_prefix, str) or not output_prefix.strip():
        raise RuntimeError("write_canonical_people_csv: 'output_prefix' is required and must be a non-empty string")

    inp = Path(canonical_csv_path)
    if not inp.exists():
        raise FileNotFoundError(f"write_canonical_people_csv: input CSV not found: {inp}")

    out_dir = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    filename = fixed_filename.strip() if isinstance(fixed_filename, str) and fixed_filename.strip() else f"{output_prefix}_CANONICAL_81.csv"
    out_path = (out_dir / filename).resolve()

    with inp.open(newline="", encoding="utf-8") as fin:
        reader = csv.DictReader(fin)
        fieldnames = list(reader.fieldnames or [])
        rows = list(reader)

    if not fieldnames:
        raise RuntimeError(f"write_canonical_people_csv: input CSV has no header: {inp}")

    _atomic_write_csv(rows, fieldnames, out_path)

    meta: Dict[str, Any] = {
        "output_prefix": output_prefix,
        "pipeline_version": pipeline_version,
        "timestamp": timestamp,
        "input_csv": str(inp.resolve()),
        "output_csv": str(out_path),
        "row_count": len(rows),
        "column_count": len(fieldnames),
    }

    if metadata_json_path is None:
        metadata_json_path = out_dir / f"{output_prefix}_CANONICAL_81.metadata.json"

    mp = Path(metadata_json_path).resolve()
    mp.parent.mkdir(parents=True, exist_ok=True)
    mp.write_text(json.dumps(meta, indent=2, sort_keys=True), encoding="utf-8")

    if not out_path.exists():
        raise RuntimeError(f"write_canonical_people_csv: output CSV missing after write: {out_path}")

    return str(out_path)


__all__ = ["write_canonical_people_csv"]
