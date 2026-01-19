#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
score_reason_generator.py
------------------------------------------------------------
Day 5 – Score Reason Generator

Purpose:
- Provide one-sentence explanation for score
- Prevent "trust me" scoring
- Make rankings defensible in demos

Design Rules:
- Deterministic
- Human-readable
"""

from typing import Dict
from determinant_tier_rules import classify_determinant_tier


def generate_score_reason(row: Dict[str, str]) -> str:
    tier = classify_determinant_tier(row)

    if tier == "Tier 1":
        return "Strong primary technical ownership and high-confidence contribution signals."
    if tier == "Tier 2":
        return "Multiple corroborated supporting signals with meaningful technical depth."
    return "Limited or indirect signals; classified conservatively to avoid overstatement."
