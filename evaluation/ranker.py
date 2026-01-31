# ==============================================================================
# AI TALENT ENGINE – SIGNAL INTELLIGENCE
# Proprietary and Confidential
# © 2025–2026 L. David Mendoza. All Rights Reserved.
# ==============================================================================
#
# This file contains proprietary intellectual property and trade secrets of
# L. David Mendoza and is part of the AI Talent Engine – Signal Intelligence system.
#
# Unauthorized access, use, copying, modification, distribution, disclosure,
# reverse engineering, or derivative use, in whole or in part, is strictly
# prohibited without prior written authorization.
#
# ==============================================================================
#
# FILE: evaluation/ranker.py
# VERSION: v1.0.0
#
# CHANGELOG:
# - v1.0.0 (2026-01-31): Deterministic ranking for evaluation outputs.
#
# VALIDATION:
# - python3 -c "from evaluation.ranker import rank_candidates; print('ok')"
#
# GIT:
# - git add evaluation/ranker.py
# - git commit -m "Add ranking (v1.0.0)"
# - git push
#

from __future__ import annotations

from typing import List

from .schemas import EvaluationResult


_TIER_ORDER = {
    "Tier 1": 2,
    "Tier 2": 1,
    "Indeterminate": 0,
}


def rank_candidates(results: List[EvaluationResult]) -> List[EvaluationResult]:
    """
    Deterministic ranking:
    1) Tier (Tier 1 > Tier 2 > Indeterminate)
    2) EQI score descending
    3) Stable tie-break by person_id
    """
    return sorted(
        results,
        key=lambda r: (-_TIER_ORDER.get(r.tier, 0), -r.eqi_score, r.person_id),
    )