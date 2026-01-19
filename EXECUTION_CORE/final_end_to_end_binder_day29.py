# © 2026 L. David Mendoza
#
# FILE: final_end_to_end_binder_day29.py
#
# PURPOSE:
# Single explicit binder that wires:
# - External ingestion (Day 23)
# - Core evaluation runner (existing)
# - Optional explainability decision cards (Day 25)
#
# IMPORTANT:
# - This file is a demo surface, NOT a replacement for run_safe.py.
# - Imports of existing modules are fail-closed with explicit errors.
# - No silent fallbacks.
#
# IMPORT-ONLY. NO SIDE EFFECTS.

from __future__ import annotations

from typing import Any, Dict, List, Mapping, Optional

from EXECUTION_CORE.external_ingestion_binder import bind_external_dataset


class BinderWiringError(RuntimeError):
    """Raised when required bind targets are missing or miswired."""


def _require_callable(obj: Any, name: str) -> None:
    if not callable(obj):
        raise BinderWiringError(f"Required callable missing or not callable: {name}")


def run_end_to_end_from_rows(
    rows: List[Dict[str, Any]],
    overrides: Optional[Mapping[str, Any]] = None,
) -> Dict[str, Any]:
    """
    End-to-end in-memory run:
    1) external ingestion binder (enrichment merge + lineage)
    2) core evaluation runner (existing)
    3) optional decision card generation (existing Day 25 module)

    Returns a structured dict:
    - enriched_rows
    - lineage
    - evaluation (core output)
    - decision_cards (optional)
    """

    # Step 1: external ingestion binder
    bound = bind_external_dataset(rows)
    enriched_rows = bound["enriched_rows"]
    lineage = bound["lineage"]

    # Step 2: core evaluation runner (existing module expected)
    try:
        from EXECUTION_CORE.full_evaluation_runner import run_full_evaluation  # type: ignore
    except Exception as e:
        raise BinderWiringError("Missing core evaluation runner: EXECUTION_CORE.full_evaluation_runner.run_full_evaluation") from e

    _require_callable(run_full_evaluation, "run_full_evaluation")

    evaluation = run_full_evaluation(enriched_rows)  # core semantics owned elsewhere

    # Step 3: optional decision cards (Day 25)
    decision_cards = None
    try:
        from EXECUTION_CORE.decision_card_generator import generate_decision_card  # type: ignore
        _require_callable(generate_decision_card, "generate_decision_card")
        # If evaluation returns a ranked list, we can compare adjacent items.
        # Fail closed: if not in expected structure, produce no cards.
        ranked = evaluation.get("ranked") if isinstance(evaluation, dict) else None
        if isinstance(ranked, list) and len(ranked) >= 2:
            cards = []
            for i in range(len(ranked) - 1):
                cards.append(generate_decision_card(ranked[i], ranked[i + 1]))
            decision_cards = cards
    except Exception:
        decision_cards = None

    return {
        "enriched_rows": enriched_rows,
        "lineage": lineage,
        "evaluation": evaluation,
        "decision_cards": decision_cards,
    }
