#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EXECUTION_CORE/row_role_materialization_pass.py
============================================================
ROW ROLE MATERIALIZATION PASS (DETERMINISTIC, EVIDENCE-SAFE)

Maintainer: L. David Mendoza © 2026
Version: v1.0.0

Purpose
- Materialize scenario role context into each row deterministically.
- Required to avoid semantically empty runs where headers exist but AI_Role_Type is blank.

Design Rules (LOCKED)
- No fabrication
- No inference scoring
- No network calls
- Strict non-overwrite for AI_Role_Type unless explicitly blank
- Provenance recorded to Field_Level_Provenance_JSON where possible

Environment Contract (required)
- AI_TALENT_ROLE_CANONICAL: non-empty string, provided by run_safe.py

Interfaces (LOCKED)
- process_csv(input_csv, output_csv) -> None

Changelog
- v1.0.0: Initial role materialization pass (row-level binding)

Validation
python3 -c "from EXECUTION_CORE.row_role_materialization_pass import process_csv; print('ok')"

Git Commands
git add EXECUTION_CORE/row_role_materialization_pass.py
git commit -m "Add row role materialization pass (deterministic AI_Role_Type binding)"
git push
"""

from __future__ import annotations

import csv
import json
import os
from pathlib import Path
from typing import Dict, Any, List


def _norm(x: Any) -> str:
    return str(x or "").strip()


def _load_prov(row: Dict[str, str]) -> Dict[str, Any]:
    raw = _norm(row.get("Field_Level_Provenance_JSON"))
    if not raw:
        return {}
    try:
        obj = json.loads(raw)
        return obj if isinstance(obj, dict) else {}
    except Exception:
        return {}


def _save_prov(row: Dict[str, str], prov: Dict[str, Any]) -> None:
    row["Field_Level_Provenance_JSON"] = json.dumps(prov, sort_keys=True)


def _set_prov(prov: Dict[str, Any], field: str, source: str, method: str) -> None:
    prov[field] = {"source": source, "method": method}


def process_csv(input_csv: str, output_csv: str) -> None:
    role = _norm(os.environ.get("AI_TALENT_ROLE_CANONICAL"))
    if not role:
        raise RuntimeError("row_role_materialization_pass: missing env AI_TALENT_ROLE_CANONICAL (set by run_safe.py)")

    inp = Path(input_csv)
    outp = Path(output_csv)
    if not inp.exists():
        raise FileNotFoundError(f"row_role_materialization_pass: input CSV not found: {inp}")

    outp.parent.mkdir(parents=True, exist_ok=True)

    with inp.open(newline="", encoding="utf-8") as fin:
        reader = csv.DictReader(fin)
        fieldnames = list(reader.fieldnames or [])
        rows: List[Dict[str, str]] = list(reader)

    if not fieldnames:
        raise RuntimeError(f"row_role_materialization_pass: input CSV has no header: {inp}")

    if "AI_Role_Type" not in fieldnames:
        fieldnames.append("AI_Role_Type")
    if "Field_Level_Provenance_JSON" not in fieldnames:
        fieldnames.append("Field_Level_Provenance_JSON")

    for row in rows:
        prov = _load_prov(row)

        if not _norm(row.get("AI_Role_Type")):
            row["AI_Role_Type"] = role
            _set_prov(prov, "AI_Role_Type", "scenario_context", "role_materialization_pass")

        _save_prov(row, prov)

    with outp.open("w", newline="", encoding="utf-8") as fout:
        writer = csv.DictWriter(fout, fieldnames=fieldnames)
        writer.writeheader()
        for r in rows:
            writer.writerow({k: r.get(k, "") for k in fieldnames})


__all__ = ["process_csv"]
