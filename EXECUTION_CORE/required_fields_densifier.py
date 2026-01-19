#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EXECUTION_CORE/required_fields_densifier.py
============================================================
REQUIRED FIELDS DENSIFIER (DETERMINISTIC, NO FABRICATION)

Maintainer: L. David Mendoza © 2026
Version: v1.0.0

THIS FILE IS:
- Import-only module exposing process_csv(input_csv, output_csv)
- Deterministic blank-filler for REQUIRED canonical columns

THIS FILE IS NOT:
- NOT a writer-of-record for canonical CSV
- NOT a scenario runner
- NOT a preview tool
- NOT allowed to call network, subprocess, or external services

Purpose
- Populate required canonical columns when they are blank:
  - Role_Type
  - Signal_Score
  - Strengths
  - Weaknesses
- Fill blanks only, never overwrite non-empty values.
- Compose content only from existing row evidence fields.
- Record provenance in Field_Level_Provenance_JSON for any field it fills.

Signals (no guessing)
- Signal_Score is categorized as High, Medium, Low using deterministic gates:
  - High: strong multi-source evidence present
  - Medium: some corroborated evidence present
  - Low: minimal public evidence present

Strengths and Weaknesses (no fabrication)
- Strengths: describes what is present in row evidence
- Weaknesses: describes what is missing in row evidence (public evidence gaps)
- Never asserts negative traits about a person

Changelog
- v1.0.0 (2026-01-18): Initial required-fields densifier (fill blanks only)

Validation
python3 -c "from EXECUTION_CORE.required_fields_densifier import process_csv; print('ok')"

Git Commands (SSH)
git add EXECUTION_CORE/required_fields_densifier.py
git commit -m "Add deterministic required-fields densifier (Role_Type, Signal_Score, Strengths, Weaknesses)"
git push
"""

from __future__ import annotations

import csv
import json
import os
from pathlib import Path
from typing import Any, Dict, List, Tuple


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


def _get_first_present(row: Dict[str, str], keys: List[str]) -> str:
    for k in keys:
        v = _norm(row.get(k))
        if v:
            return v
    return ""


def _split_tokens_preserve_order(text: str) -> List[str]:
    if not text:
        return []
    parts = []
    for raw in text.replace("|", ",").replace(";", ",").split(","):
        v = raw.strip()
        if v:
            parts.append(v)
    return parts


def _extract_ordered_keywords(text: str, keywords: List[str]) -> List[str]:
    """
    Deterministic containment scan preserving the keyword list order.
    """
    blob = (text or "").lower()
    out: List[str] = []
    for k in keywords:
        if k.lower() in blob:
            out.append(k)
    return out


def _evidence_flags(row: Dict[str, str]) -> Dict[str, bool]:
    """
    Evidence-only flags based on presence of existing fields.
    """
    return {
        "has_github": _nonempty(_get_first_present(row, ["GitHub_URL", "GitHub_Username", "Key_GitHub_AI_Repos"])),
        "has_repos": _nonempty(row.get("Key_GitHub_AI_Repos")) or _nonempty(row.get("Repo_Topics_Keywords")),
        "has_models": _nonempty(row.get("Primary_Model_Families")) or _nonempty(row.get("Determinative_Skill_Areas")),
        "has_infra": _nonempty(row.get("Inference_Training_Infra_Signals")),
        "has_rlhf": _nonempty(row.get("RLHF_Alignment_Signals")),
        "has_pubs": _nonempty(row.get("Publication_Count")) or _nonempty(row.get("Citation_Count_Raw")),
        "has_company": _nonempty(_get_first_present(row, ["Current_Company", "Company_XRay_Source_URLs"])),
        "has_identity": _nonempty(row.get("Full_Name")) or _nonempty(row.get("LinkedIn_Public_URL")),
    }


def _classify_signal_score(flags: Dict[str, bool]) -> str:
    """
    Deterministic categorization.
    """
    strong = 0
    strong += 1 if flags.get("has_github") else 0
    strong += 1 if flags.get("has_repos") else 0
    strong += 1 if flags.get("has_models") else 0
    strong += 1 if flags.get("has_infra") else 0
    strong += 1 if flags.get("has_rlhf") else 0
    strong += 1 if flags.get("has_pubs") else 0
    strong += 1 if flags.get("has_company") else 0
    strong += 1 if flags.get("has_identity") else 0

    if strong >= 5:
        return "High"
    if strong >= 3:
        return "Medium"
    return "Low"


def _compose_strengths(row: Dict[str, str], flags: Dict[str, bool]) -> str:
    """
    Compose an evidence-only strengths sentence using existing fields.
    Ordered to match your preferred signal order where possible:
    models first, then vector DB, RAG, LangChain family, inference engines.
    """
    model_src = _get_first_present(row, ["Primary_Model_Families", "Determinative_Skill_Areas"])
    repo_topics = _get_first_present(row, ["Repo_Topics_Keywords", "Key_GitHub_AI_Repos"])
    infra = _norm(row.get("Inference_Training_Infra_Signals"))
    rlhf = _norm(row.get("RLHF_Alignment_Signals"))

    text_blob = " ".join([model_src, repo_topics, infra, rlhf])

    model_fams = _split_tokens_preserve_order(model_src)[:6]

    vector_keywords = ["Weaviate", "Pinecone", "FAISS", "Milvus", "Qdrant", "Chroma", "pgvector"]
    rag_keywords = ["Retrieval-Augmented Generation", "RAG"]
    lang_keywords = ["LangChain", "LangGraph", "LlamaIndex"]
    infer_keywords = ["TensorRT", "TensorRT-LLM", "vLLM", "TGI", "ONNX", "Triton", "llama.cpp"]

    vectors = _extract_ordered_keywords(text_blob, vector_keywords)
    rags = _extract_ordered_keywords(text_blob, rag_keywords)
    langs = _extract_ordered_keywords(text_blob, lang_keywords)
    infers = _extract_ordered_keywords(text_blob, infer_keywords)

    parts: List[str] = []

    if model_fams:
        parts.append("Model families: " + ", ".join(model_fams))
    elif flags.get("has_models"):
        parts.append("Model family or determinant skill evidence present in row fields")

    if vectors:
        parts.append("Vector databases: " + ", ".join(vectors))

    if rags:
        # Ensure spelled out once if possible
        if "Retrieval-Augmented Generation" in rags:
            parts.append("Retrieval-Augmented Generation (RAG) signals present")
        else:
            parts.append("RAG signals present")

    if langs:
        parts.append("RAG tooling: " + ", ".join(langs))

    if infers:
        parts.append("Inference stack: " + ", ".join(infers))
    elif flags.get("has_infra"):
        parts.append("Inference and infrastructure signals present in row fields")

    if flags.get("has_rlhf") and rlhf:
        parts.append("RLHF or alignment signals present")

    if flags.get("has_github"):
        gh = _get_first_present(row, ["GitHub_URL", "GitHub_Username"])
        if gh:
            parts.append(f"GitHub evidence present ({gh})")
        else:
            parts.append("GitHub evidence present")

    if flags.get("has_pubs"):
        pc = _norm(row.get("Publication_Count"))
        cc = _norm(row.get("Citation_Count_Raw"))
        if pc or cc:
            parts.append("Research impact signals present (publications or citations)")
        else:
            parts.append("Research impact signals present")

    if not parts:
        return "Insufficient corroborated technical evidence available in current row fields to summarize deterministically."

    return " | ".join(parts)


def _compose_weaknesses(row: Dict[str, str], flags: Dict[str, bool]) -> str:
    """
    Weaknesses are framed as evidence gaps only.
    """
    gaps: List[str] = []

    if not flags.get("has_identity"):
        gaps.append("Missing reliable identity signals (name or public profile URL) in current row fields")
    if not flags.get("has_github"):
        gaps.append("No GitHub profile or repository evidence present in current row fields")
    if not flags.get("has_models"):
        gaps.append("No explicit model family or determinant skill evidence present in current row fields")
    if not flags.get("has_infra") and not flags.get("has_rlhf"):
        gaps.append("No infra, serving, or alignment signals present in current row fields")
    if not flags.get("has_pubs"):
        gaps.append("No publication or citation evidence present in current row fields")
    if not flags.get("has_company"):
        gaps.append("No company affiliation evidence present in current row fields")

    if not gaps:
        return "No major public-evidence gaps detected in the current row fields for this role context."

    return " | ".join(gaps)


def _resolve_role_type(row: Dict[str, str]) -> str:
    """
    Deterministic Role_Type fill.
    Priority:
    1) existing Role_Type (no overwrite, handled by caller)
    2) AI_Role_Type (materialized earlier)
    3) env AI_TALENT_ROLE_CANONICAL (scenario context)
    """
    v = _norm(row.get("AI_Role_Type"))
    if v:
        return v

    env = _norm(os.environ.get("AI_TALENT_ROLE_CANONICAL"))
    if env:
        return env

    return ""


def process_csv(input_csv: str | Path, output_csv: str | Path) -> None:
    inp = Path(input_csv)
    outp = Path(output_csv)

    if not inp.exists():
        raise FileNotFoundError(f"required_fields_densifier: input CSV not found: {inp}")

    outp.parent.mkdir(parents=True, exist_ok=True)

    with inp.open(newline="", encoding="utf-8") as fin:
        reader = csv.DictReader(fin)
        fieldnames = list(reader.fieldnames or [])
        rows: List[Dict[str, str]] = list(reader)

    if not fieldnames:
        raise RuntimeError(f"required_fields_densifier: input CSV has no header: {inp}")

    must_cols = ["Field_Level_Provenance_JSON", "Role_Type", "Signal_Score", "Strengths", "Weaknesses"]
    for c in must_cols:
        if c not in fieldnames:
            fieldnames.append(c)

    for row in rows:
        prov = _load_prov(row)

        # Role_Type (fill only if blank)
        if not _nonempty(row.get("Role_Type")):
            rt = _resolve_role_type(row)
            if rt:
                row["Role_Type"] = rt
                _set_prov(prov, "Role_Type", "scenario_context", "required_fields_densifier_fill_blank")

        flags = _evidence_flags(row)

        # Signal_Score (fill only if blank)
        if not _nonempty(row.get("Signal_Score")):
            sc = _classify_signal_score(flags)
            row["Signal_Score"] = sc
            _set_prov(prov, "Signal_Score", "row_fields", "deterministic_gate_classification")

        # Strengths (fill only if blank)
        if not _nonempty(row.get("Strengths")):
            s = _compose_strengths(row, flags)
            if s:
                row["Strengths"] = s
                _set_prov(prov, "Strengths", "row_fields", "deterministic_compose_from_evidence")

        # Weaknesses (fill only if blank)
        if not _nonempty(row.get("Weaknesses")):
            w = _compose_weaknesses(row, flags)
            if w:
                row["Weaknesses"] = w
                _set_prov(prov, "Weaknesses", "row_fields", "deterministic_gap_summary")

        _save_prov(row, prov)

    with outp.open("w", newline="", encoding="utf-8") as fout:
        writer = csv.DictWriter(fout, fieldnames=fieldnames)
        writer.writeheader()
        for r in rows:
            writer.writerow({k: r.get(k, "") for k in fieldnames})


__all__ = ["process_csv"]
