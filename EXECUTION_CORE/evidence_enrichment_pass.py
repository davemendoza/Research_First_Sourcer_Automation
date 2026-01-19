#!/usr/bin/env python3
"""
EXECUTION_CORE/evidence_enrichment_pass.py
============================================================
DAY 16 — EVIDENCE ENRICHMENT PASS (CANONICAL, NON-SCORING)

PURPOSE
- Expand canonical evidence categories using extended artifact fields
- Output ONLY canonical evidence strings (compatible with Day 8 strict matching)
- No scoring, no tiering, no density, no IO

THIS FILE:
- IS import-only
- IS deterministic
- IS in-memory only

THIS FILE IS NOT:
- NOT a scorer
- NOT a tier resolver
- NOT a CSV reader
- NOT a writer
"""

from __future__ import annotations
from typing import Any, Dict, List, Mapping

from EXECUTION_CORE.evidence_vocabulary import CANONICAL_EVIDENCE


# Extended fields beyond Day 9's ARTIFACT_FIELDS that may contain relevant evidence text.
EXTENDED_EVIDENCE_FIELDS = {
    "GitHub_URL",
    "GitHub_IO_URL",
    "Portfolio_URL",
    "Personal_Website_URL",
    "Resume_Link",
    "Patents",
    "Blogs",
    "Talks",
    "Conference_Talks",
    "Open_Source",
    "Projects",
    "Publications",
    "Research",
}


def _norm(v: Any) -> str:
    return str(v or "").strip().lower()


def enrich_canonical_evidence(
    *,
    row: Mapping[str, Any],
) -> List[str]:
    """
    Return additional canonical evidence categories derived from extended fields.

    Output: list of canonical evidence category strings (sorted, unique)
    """
    parts: List[str] = []
    for field in EXTENDED_EVIDENCE_FIELDS:
        if field in row and isinstance(row[field], (str, int, float)):
            parts.append(_norm(row[field]))

    text_blob = " ".join(parts)

    hits: List[str] = []
    for canonical, triggers in CANONICAL_EVIDENCE.items():
        for trig in triggers:
            if trig in text_blob:
                hits.append(canonical)
                break

    return sorted(set(hits))


__all__ = ["EXTENDED_EVIDENCE_FIELDS", "enrich_canonical_evidence"]
