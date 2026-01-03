#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations
import json
import importlib
from pathlib import Path

REGISTRY_PATH = Path(__file__).parent / "scenarios" / "SCENARIO_REGISTRY.json"

FORBIDDEN_PLACEHOLDER_FRAGMENTS = [
    "example.com",
    "email@example",
    "555-",
    "cv available",
    "lorem ipsum"
]


class ScenarioContractViolation(RuntimeError):
    pass


def load_registry() -> dict:
    if not REGISTRY_PATH.exists():
        raise ScenarioContractViolation("Scenario registry missing.")
    return json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))


def get_scenario_spec(scenario: str) -> dict:
    """
    Pure accessor.
    No imports.
    No execution.
    No validation side effects.
    """
    registry = load_registry()

    if scenario not in registry:
        raise ScenarioContractViolation(
            f"Scenario '{scenario}' is not registered."
        )

    return registry[scenario]


def validate_scenario_contract(*, scenario: str, mode: str) -> dict:
    registry = load_registry()

    if scenario not in registry:
        raise ScenarioContractViolation(
            f"Scenario '{scenario}' is not registered. Execution blocked."
        )

    spec = registry[scenario]

    if not spec.get("enabled", False):
        raise ScenarioContractViolation(
            f"Scenario '{scenario}' is disabled."
        )

    allowed = spec.get("allowed_modes", [])
    if mode not in allowed:
        raise ScenarioContractViolation(
            f"Scenario '{scenario}' is not allowed in mode '{mode}'."
        )

    runner_path = spec["runner"]
    module_name, func_name = runner_path.rsplit(".", 1)

    try:
        module = importlib.import_module(module_name)
    except Exception as e:
        raise ScenarioContractViolation(
            f"Runner module '{module_name}' cannot be imported."
        ) from e

    if not hasattr(module, func_name):
        raise ScenarioContractViolation(
            f"Runner function '{func_name}' not found in {module_name}."
        )

    return spec
