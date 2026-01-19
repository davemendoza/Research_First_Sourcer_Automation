#!/usr/bin/env python3
"""
EXECUTION_CORE/personal_artifact_evidence_summary.py
============================================================
DAY 9 — EVIDENCE NORMALIZATION & SUMMARIZATION

Uses the frozen canonical evidence vocabulary.
"""

from __future__ import annotations
from typing import Any, Dict, List, Mapping
from collections import OrderedDict

from EXECUTION_CORE.evidence_vocabulary import CANONICAL_EVIDENCE


ARTIFACT_FIELDS = {
    "Summary",
    "Experience",
    "Skills",
    "Strengths",
    "Weaknesses",
    "Publications",
    "Projects",
    "Open_Source",
    "Research",
}


def _norm(v: Any) -> str:
    return str(v or "").strip().lower()


def summarize_evidence(
    *,
    row: Mapping[str, Any],
) -> Dict[str, Any]:
    """
    Summarize a single row into canonical evidence categories.
    Only inspects approved artifact fields.
    """
    text_blob_parts: List[str] = []

    for field in ARTIFACT_FIELDS:
        if field in row and isinstance(row[field], (str, int, float)):
            text_blob_parts.append(_norm(row[field]))

    text_blob = " ".join(text_blob_parts)

    canonical_hits: List[str] = []

    for canonical, triggers in CANONICAL_EVIDENCE.items():
        for t in triggers:
            if t in text_blob:
                canonical_hits.append(canonical)
                break

    canonical_hits = sorted(set(canonical_hits))

    return OrderedDict(
        canonical_evidence=canonical_hits,
        evidence_count=len(canonical_hits),
    )


__all__ = [
    "summarize_evidence",
    "ARTIFACT_FIELDS",
]
