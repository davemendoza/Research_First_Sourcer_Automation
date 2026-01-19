#!/usr/bin/env python3
from __future__ import annotations

"""
EXECUTION_CORE/people_scenario_resolver.py
====================================================
DETERMINISTIC SCENARIO CONTRACT RESOLVER (LOCKED)

Emits a STRICT contract consumed by run_safe.py:

Required keys:
- SCENARIO_PREFIX
- SCENARIO_SEED
- ROLE_CANONICAL
"""

from typing import Dict


def resolve_scenario(key: str) -> Dict[str, str]:
    if not isinstance(key, str) or not key.strip():
        raise ValueError("Scenario key must be a non-empty string")

    key = key.strip().lower()

    # -----------------------------
    # Canonical scenarios
    # -----------------------------
    if key in ("demo", "frontier"):
        return {
            "SCENARIO_PREFIX": "frontier_ai_scientist",
            "SCENARIO_SEED": "frontier_ai_scientist",
            "ROLE_CANONICAL": "Frontier AI Scientist",
        }

    if key in ("gpt_slim", "slim"):
        return {
            "SCENARIO_PREFIX": "gpt_slim_frontier_ai_scientist",
            "SCENARIO_SEED": "frontier_ai_scientist",
            "ROLE_CANONICAL": "Frontier AI Scientist",
        }

    if key in ("ai_infra", "infra"):
        return {
            "SCENARIO_PREFIX": "ai_infra_engineer",
            "SCENARIO_SEED": "ai_infra_engineer",
            "ROLE_CANONICAL": "AI Infrastructure Engineer",
        }

    # -----------------------------
    # Deterministic safe fallback
    # -----------------------------
    safe = key.replace(" ", "_")
    return {
        "SCENARIO_PREFIX": safe,
        "SCENARIO_SEED": safe,
        "ROLE_CANONICAL": "Frontier AI Scientist",
    }


__all__ = ["resolve_scenario"]
