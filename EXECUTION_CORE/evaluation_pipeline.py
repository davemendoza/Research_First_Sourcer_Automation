#!/usr/bin/env python3
"""
EXECUTION_CORE/evaluation_pipeline.py
============================================================
DAY 10.5 — EVALUATION PIPELINE BINDING (AUTHORITATIVE)

This is the single authoritative binding for Day 6 → Day 10 logic.
"""

from __future__ import annotations
from typing import Any, Dict, Mapping, List

from EXECUTION_CORE.personal_artifact_evidence_summary import summarize_evidence
from EXECUTION_CORE.determinant_tier_rules import resolve_determinant_tier
from EXECUTION_CORE.scoring_adapter import compute_score
from EXECUTION_CORE.csv_density_policy import resolve_role_family


def evaluate_row_pipeline(
    *,
    row: Mapping[str, Any],
    density_result: Mapping[str, Any],
) -> Dict[str, Any]:
    """
    Fully evaluate a single row using Day 6–10 logic.
    """

    role_type = row.get("Role_Type", "")
    role_family = resolve_role_family(role_type)

    evidence_summary = summarize_evidence(row=row)
    canonical_evidence: List[str] = evidence_summary["canonical_evidence"]
    evidence_count: int = evidence_summary["evidence_count"]

    determinant_tiers: List[str] = [
        resolve_determinant_tier(
            role_family=role_family,
            evidence_category=evidence,
        )
        for evidence in canonical_evidence
    ]

    score_result = compute_score(
        density_level=density_result["density_level"],
        determinant_tiers=determinant_tiers,
        evidence_count=evidence_count,
    )

    return {
        "role_family": role_family,
        "density_level": density_result["density_level"],
        "canonical_evidence": canonical_evidence,
        "determinant_tiers": determinant_tiers,
        "final_score": score_result["score"],
        "verdict": score_result["verdict"],
        "score_components": score_result["components"],
    }


__all__ = ["evaluate_row_pipeline"]
