#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
signal_score_calculator.py
------------------------------------------------------------
Day 5 – Overall Signal Score Calculator

Purpose:
- Compute a stable numeric score per row
- Tie score to determinant tier
- Avoid fragile per-column weighting

Design Rules:
- Deterministic
- Explainable
- No ML
"""

from typing import Dict
from determinant_tier_rules import DETERMINANT_TIERS, classify_determinant_tier


def compute_overall_signal_score(row: Dict[str, str]) -> int:
    """
    Returns an integer score [0–100].
    """
    tier = classify_determinant_tier(row)
    base = DETERMINANT_TIERS[tier]["base_score"]

    # Light bonus for density (not content guessing)
    populated = sum(1 for v in row.values() if str(v).strip())
    density_bonus = min(10, populated // 15)

    return min(100, base + density_bonus)
