#!/usr/bin/env python3
"""
DAY 17 — COHORT CONTEXT ANALYZER

Compute cohort-level context signals.
"""

from typing import List, Dict


def analyze_cohort(evaluations: List[Dict[str, object]]) -> Dict[str, float]:
    """
    Compute simple cohort statistics.
    """
    scores = [e["final_score"] for e in evaluations]
    if not scores:
        return {"avg_score": 0.0}
    return {"avg_score": sum(scores) / len(scores)}


__all__ = ["analyze_cohort"]
