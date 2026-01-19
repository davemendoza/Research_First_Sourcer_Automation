#!/usr/bin/env python3
"""
EXECUTION_CORE/full_evaluation_runner.py
============================================================
DAY 14 — FULL EVALUATION RUNNER (CORRECTED)

PURPOSE
- Execute Days 6–13 in correct order
- Use per-role density when available
- Produce final evaluated outputs deterministically
"""

from typing import List, Dict

from EXECUTION_CORE.aggregate_signal_views import aggregate_signal_views
from EXECUTION_CORE.csv_density_policy import classify_density, resolve_role_family
from EXECUTION_CORE.evaluation_pipeline import evaluate_row_pipeline
from EXECUTION_CORE.demo_narrative_sequence import sequence_narrative
from EXECUTION_CORE.evaluation_qc_validator import validate_evaluation


def run_full_evaluation(rows: List[Dict[str, object]]) -> List[Dict[str, object]]:
    """
    Execute full evaluation pipeline over rows.
    """
    results = []

    agg = aggregate_signal_views(rows)
    density_global = agg["density_inputs"]["global"]
    density_by_role = agg["density_inputs"].get("by_role", {})

    for row in rows:
        role_type = row.get("Role_Type", "")
        role_family = resolve_role_family(role_type)

        role_density = density_by_role.get(role_type, density_global)

        density_result = classify_density(
            role_family=role_family,
            nonempty_fields_avg=role_density["nonempty_fields_avg"],
            signal_fields_nonempty_avg=role_density["signal_fields_nonempty_avg"],
            evidence_fields_nonempty_avg=role_density["evidence_fields_nonempty_avg"],
        )

        evaluation = evaluate_row_pipeline(
            row=row,
            density_result=density_result,
        )

        narrative = sequence_narrative(
            role_family=role_family,
            evaluation=evaluation,
        )

        validate_evaluation(narrative)
        results.append(narrative)

    return results


__all__ = ["run_full_evaluation"]
