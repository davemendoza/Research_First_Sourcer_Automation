#!/usr/bin/env python3
"""
people_scenario_resolver.py

Resolves scenario_key to a seed CSV.
Deterministic, read-only.
"""

from pathlib import Path
from EXECUTION_CORE.ai_role_registry import assert_valid_role
import shutil

REPO_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = REPO_ROOT / "data"

class ScenarioResolutionError(Exception):
    pass

def resolve_scenario(scenario_key: str) -> Path:
    seed_path = DATA_DIR / f"{scenario_key}.csv"

    if not seed_path.exists():
        raise ScenarioResolutionError(f"Seed CSV not found for scenario: {scenario_key}")

    return seed_path
