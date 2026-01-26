#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Scenario resolver for people pipelines.
Fail-closed, explicit mapping only.
"""

from pathlib import Path
from typing import Dict, Any

REPO_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = REPO_ROOT / "data"


class ScenarioResolutionError(Exception):
    pass


def _die(msg: str) -> None:
    raise ScenarioResolutionError(msg)


# ──────────────────────────────────────────────────────────
# EXPLICIT SCENARIO → SEED MAPPING (AUTHORITATIVE)
# NOTE: SCENARIO_SEED is a PREFIX, not a filename.
# No inference. No fallbacks. No guessing.
# ──────────────────────────────────────────────────────────
SCENARIO_MAP: Dict[str, Dict[str, str]] = {
    "Frontier AI Research Scientist": {
        "SCENARIO_PREFIX": "Frontier_AI_Research_Scientist",
        "SCENARIO_SEED": "frontier_ai_seed",  # ← FIXED (no .csv)
        "ROLE_CANONICAL": "Frontier AI Research Scientist",
    },
}


def resolve_scenario(scenario_key: str) -> Dict[str, Any]:
    key = scenario_key.strip()
    if key not in SCENARIO_MAP:
        _die(f"Unknown scenario key: {key}")

    entry = SCENARIO_MAP[key].copy()
    seed_prefix = entry["SCENARIO_SEED"]

    # Do NOT append .csv here — seed_locator owns that logic
    entry["SEED_PREFIX"] = seed_prefix
    return entry
