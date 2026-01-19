#!/usr/bin/env python3
"""
EXECUTION_CORE/demo_narrative_sequence.py
============================================================
DAY 11 — NARRATIVE SEQUENCING (LOGIC ONLY)

PURPOSE
- Define the canonical explanation order for evaluated candidates
- Ensure role-aware, deterministic narrative structure
- Produce explanation blocks, not formatted output

THIS FILE:
- IS import-only
- IS deterministic
- IS logic-only

THIS FILE IS NOT:
- NOT a renderer
- NOT a preview
- NOT a CLI
"""

from typing import Dict, List
from collections import OrderedDict


ROLE_NARRATIVE_ORDER: Dict[str, List[str]] = {
    "frontier": [
        "determinant_tiers",
        "canonical_evidence",
        "density_level",
        "final_score",
        "verdict",
    ],
    "infra": [
        "canonical_evidence",
        "determinant_tiers",
        "density_level",
        "final_score",
        "verdict",
    ],
    "applied": [
        "canonical_evidence",
        "density_level",
        "determinant_tiers",
        "final_score",
        "verdict",
    ],
    "solutions": [
        "canonical_evidence",
        "density_level",
        "final_score",
        "verdict",
    ],
    "evangelism": [
        "canonical_evidence",
        "final_score",
        "verdict",
    ],
    "gtm": [
        "canonical_evidence",
        "final_score",
        "verdict",
    ],
}


def sequence_narrative(
    *,
    role_family: str,
    evaluation: Dict[str, object],
) -> Dict[str, object]:
    """
    Return evaluation reordered into a narrative-friendly structure.
    """
    order = ROLE_NARRATIVE_ORDER.get(role_family, ROLE_NARRATIVE_ORDER["applied"])

    ordered = OrderedDict()
    for key in order:
        if key in evaluation:
            ordered[key] = evaluation[key]

    return ordered


__all__ = ["sequence_narrative"]
