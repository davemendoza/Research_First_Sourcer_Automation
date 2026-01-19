#!/usr/bin/env python3
"""
DAY 19 — EXPLANATION ARTIFACT BUILDER

Build interview-grade explanation objects.
"""

from typing import Dict


def build_explanation(evaluation: Dict[str, object]) -> Dict[str, object]:
    """
    Return structured explanation artifact.
    """
    return {
        "verdict": evaluation["verdict"],
        "why": {
            "evidence": evaluation.get("canonical_evidence", []),
            "tiers": evaluation.get("determinant_tiers", []),
            "density": evaluation.get("density_level"),
        },
    }


__all__ = ["build_explanation"]
