#!/usr/bin/env python3
"""
EXECUTION_CORE/evaluation_qc_validator.py
============================================================
DAY 13 — EVALUATION QUALITY CONTROL (CORRECTED)

PURPOSE
- Enforce semantic invariants
- Prevent silent degradation
"""

from typing import Dict, List


def validate_evaluation(evaluation: Dict[str, object]) -> None:
    """
    Raise AssertionError if evaluation violates invariants.
    """

    # Required fields
    assert "final_score" in evaluation
    assert "verdict" in evaluation
    assert "density_level" in evaluation

    score = evaluation["final_score"]
    assert isinstance(score, (int, float))
    assert score >= 0

    verdict = evaluation["verdict"]
    assert verdict in {
        "strong_fit",
        "potential_fit",
        "weak_fit",
        "insufficient_signal",
    }

    canonical_evidence = evaluation.get("canonical_evidence", [])
    determinant_tiers = evaluation.get("determinant_tiers", [])

    if canonical_evidence:
        assert determinant_tiers, "Evidence present but no determinant tiers resolved"

    if determinant_tiers:
        assert len(determinant_tiers) == len(canonical_evidence)


__all__ = ["validate_evaluation"]
