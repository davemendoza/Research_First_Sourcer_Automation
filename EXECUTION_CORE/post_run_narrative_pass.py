#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EXECUTION_CORE/post_run_narrative_pass.py
============================================================
POST-RUN NARRATIVE PASS (DETERMINISTIC, NO FABRICATION)

Maintainer: L. David Mendoza © 2026
Version: v1.1.0

Purpose
- Increase interview-grade row readability without inventing facts.
- Writes only into existing canonical columns (81-column schema).
- Fills only blank targets with deterministic compositions from existing evidence fields.

Targets (fill only if blank)
- GitHub_Repo_Evidence_Why
- Open_Source_Impact_Notes
- Company_XRay_Notes
- Downstream_Adoption_Signal
- Production_vs_Research_Indicator
- GPT_Slim_Rationale (only when eligible)

Rules
- No network calls
- No inference scoring
- No overwrite of non-empty fields
- Deterministic templates only

Validation
python3 -c "from EXECUTION_CORE.post_run_narrative_pass import process_csv; print('ok')"

Git Commands
git add EXECUTION_CORE/post_run_narrative_pass.py
git commit -m "Add deterministic post-run narrative pass (no fabrication, fill blanks only)"
git push
"""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Dict, Any, List


def _norm(x: Any) -> str:
    return str(x or "").strip()


def _nonempty(x: Any) -> bool:
    return _norm(x) != ""


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


def _compose(row: Dict[str, str], fields: List[str]) -> str:
    parts = []
    for f in fields:
        v = _norm(row.get(f))
        if v:
            parts.append(f"{f}={v}")
    return " | ".join(parts)


def process_csv(input_csv: str | Path, output_csv: str | Path) -> None:
    inp = Path(input_csv)
    outp = Path(output_csv)
    if not inp.exists():
        raise FileNotFoundError(f"post_run_narrative_pass: input CSV not found: {inp}")
    outp.parent.mkdir(parents=True, exist_ok=True)

    with inp.open(newline="", encoding="utf-8") as fin:
        reader = csv.DictReader(fin)
        fieldnames = list(reader.fieldnames or [])
        rows: List[Dict[str, str]] = list(reader)

    if not fieldnames:
        raise RuntimeError(f"post_run_narrative_pass: input CSV has no header: {inp}")

    must = [
        "Field_Level_Provenance_JSON",
        "GitHub_Repo_Evidence_Why",
        "Open_Source_Impact_Notes",
        "Company_XRay_Notes",
        "Downstream_Adoption_Signal",
        "Production_vs_Research_Indicator",
        "GPT_Slim_Rationale",
    ]
    for c in must:
        if c not in fieldnames:
            fieldnames.append(c)

    for row in rows:
        prov = _load_prov(row)

        if not _nonempty(row.get("GitHub_Repo_Evidence_Why")):
            v = _compose(row, ["GitHub_URL", "GitHub_Username", "Key_GitHub_AI_Repos", "Repo_Topics_Keywords", "GitHub_Repo_Signal_Type"])
            if v:
                row["GitHub_Repo_Evidence_Why"] = v
                _set_prov(prov, "GitHub_Repo_Evidence_Why", "row_fields", "deterministic_compose")

        if not _nonempty(row.get("Open_Source_Impact_Notes")):
            v = _compose(row, ["Key_GitHub_AI_Repos", "GitHub_Followers", "Repo_Topics_Keywords", "Open_Source_Impact_Notes"])
            v = v.replace("Open_Source_Impact_Notes=", "").strip(" |")
            if v:
                row["Open_Source_Impact_Notes"] = v
                _set_prov(prov, "Open_Source_Impact_Notes", "row_fields", "deterministic_compose")

        if not _nonempty(row.get("Downstream_Adoption_Signal")):
            v = _compose(row, ["Downstream_Adoption_Signal", "Repo_Topics_Keywords", "Inference_Training_Infra_Signals"])
            v = v.replace("Downstream_Adoption_Signal=", "").strip(" |")
            if v:
                row["Downstream_Adoption_Signal"] = v
                _set_prov(prov, "Downstream_Adoption_Signal", "row_fields", "deterministic_compose")

        if not _nonempty(row.get("Production_vs_Research_Indicator")):
            blob = " ".join([
                _norm(row.get("Inference_Training_Infra_Signals")),
                _norm(row.get("RLHF_Alignment_Signals")),
                _norm(row.get("Publication_Count")),
                _norm(row.get("Citation_Count_Raw")),
            ]).lower()
            if any(k in blob for k in ["latency", "throughput", "serving", "deployment", "production"]):
                row["Production_vs_Research_Indicator"] = "Production-leaning (evidence in inference/deployment signals)"
                _set_prov(prov, "Production_vs_Research_Indicator", "row_fields", "deterministic_rule")
            elif any(k in blob for k in ["paper", "pretraining", "architecture", "neurips", "iclr", "icml"]):
                row["Production_vs_Research_Indicator"] = "Research-leaning (evidence in publications/research signals)"
                _set_prov(prov, "Production_vs_Research_Indicator", "row_fields", "deterministic_rule")

        if not _nonempty(row.get("Company_XRay_Notes")):
            v = _compose(row, ["Current_Title", "Current_Company", "Company_XRay_Source_URLs"])
            if v:
                row["Company_XRay_Notes"] = v
                _set_prov(prov, "Company_XRay_Notes", "row_fields", "deterministic_compose")

        if not _nonempty(row.get("GPT_Slim_Rationale")):
            elig = _norm(row.get("GPT_Slim_Input_Eligible")).lower()
            if elig in ("true", "yes", "1"):
                v = _compose(row, ["Primary_Model_Families", "Determinative_Skill_Areas", "Inference_Training_Infra_Signals", "RLHF_Alignment_Signals"])
                if v:
                    row["GPT_Slim_Rationale"] = v
                    _set_prov(prov, "GPT_Slim_Rationale", "row_fields", "deterministic_compose")

        _save_prov(row, prov)

    with outp.open("w", newline="", encoding="utf-8") as fout:
        writer = csv.DictWriter(fout, fieldnames=fieldnames)
        writer.writeheader()
        for r in rows:
            writer.writerow({k: r.get(k, "") for k in fieldnames})


__all__ = ["process_csv"]
