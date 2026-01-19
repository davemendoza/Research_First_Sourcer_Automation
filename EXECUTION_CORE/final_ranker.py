#!/usr/bin/env python3
"""
DAY 18 — FINAL RANKER

Stable, deterministic ranking.
"""

from typing import List, Dict


def rank_candidates(evaluations: List[Dict[str, object]]) -> List[Dict[str, object]]:
    """
    Rank candidates by final_score descending.
    """
    return sorted(
        evaluations,
        key=lambda e: e["final_score"],
        reverse=True,
    )


__all__ = ["rank_candidates"]
