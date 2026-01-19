#!/usr/bin/env python3
"""
EXECUTION_CORE/scoring_adapter.py
============================================================
DAY 10 — SCORING ADAPTER (CORRECTED)

PURPOSE
- Combine density, determinant tiers, and evidence into final scores
- Enforce determinant dominance (Tier > Evidence)
- Produce deterministic, explainable outcomes

THIS FILE:
- IS import-only
- IS deterministic
- IS in-memory only

THIS FILE IS NOT:
- NOT a preview
- NOT a CSV reader
- NOT a CLI
"""

from __future__ import annotations
from typing import Dict, List
from collections import OrderedDict


# ---------------------------------------------------------------------
# Determinant Tier Weights (Dominant)
# ---------------------------------------------------------------------

TIER_WEIGHTS: Dict[str, int] = {
    "tier_1": 5,
    "tier_2": 3,
    "tier_3": 1,
    "tier_4": 0,
}


# ---------------------------------------------------------------------
# Density Multipliers (Modulating, not dominating)
# ---------------------------------------------------------------------

DENSITY_MULTIPLIER: Dict[str, float] = {
    "strong": 1.0,
    "adequate": 0.85,
    "weak": 0.6,
    "deficient": 0.3,
}


# ---------------------------------------------------------------------
# Evidence Contribution (CAPPED)
# ---------------------------------------------------------------------

MAX_EVIDENCE_BONUS = 3  # Evidence may support, never dominate


def compute_score(
    *,
    density_level: str,
    determinant_tiers: List[str],
    evidence_count: int,
) -> Dict[str, object]:
    """
    Compute final score.

    Rules:
    - Determinant tiers dominate
    - Density modulates determinant strength
    - Evidence provides limited additive support only
    """
    tier_score = sum(TIER_WEIGHTS.get(t, 0) for t in determinant_tiers)
    density_factor = DENSITY_MULTIPLIER.get(density_level, 0.0)

    dominant_component = tier_score * density_factor
    evidence_bonus = min(evidence_count, MAX_EVIDENCE_BONUS)

    final_score = round(dominant_component + evidence_bonus, 2)

    if final_score >= 14:
        verdict = "strong_fit"
    elif final_score >= 9:
        verdict = "potential_fit"
    elif final_score >= 4:
        verdict = "weak_fit"
    else:
        verdict = "insufficient_signal"

    return OrderedDict(
        score=final_score,
        verdict=verdict,
        components=OrderedDict(
            tier_score=tier_score,
            density_factor=density_factor,
            evidence_bonus=evidence_bonus,
        ),
    )


__all__ = ["compute_score"]
