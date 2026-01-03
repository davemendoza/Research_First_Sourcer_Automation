#!/usr/bin/env python3
"""
AI Talent Engine – Preflight Contract Enforcement
© 2025 L. David Mendoza

Purpose:
- Enforce Transitional Reset Prompt
- Prevent phantom output paths
- Block schema collapse
- Guarantee demo safety BEFORE enrichment
"""

import os
import sys
import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent
RESET_PROMPT = REPO_ROOT / "docs" / "TRANSITIONAL_RESET_PROMPT.md"

def fail(msg: str):
    print(f"\n❌ PREFLIGHT FAILURE\n{msg}\n")
    sys.exit(1)

def info(msg: str):
    print(f"ℹ️  {msg}")

def enforce_reset_prompt_exists():
    if not RESET_PROMPT.exists():
        fail("Missing docs/TRANSITIONAL_RESET_PROMPT.md (contract not found)")
    info("Transitional reset prompt present")

def load_schema_floor():
    schema_file = REPO_ROOT / "schema" / "people_schema.json"
    if not schema_file.exists():
        fail("Canonical People schema file missing")

    with open(schema_file, "r", encoding="utf-8") as f:
        schema = json.load(f)

    if "columns" not in schema or not schema["columns"]:
        fail("Canonical People schema has no columns defined")

    info(f"Canonical schema column count: {len(schema['columns'])}")
    return schema["columns"]

def enforce_scenario_registry(scenario_name: str):
    registry = REPO_ROOT / "scenario_registry.json"
    if not registry.exists():
        fail("Scenario registry missing")

    with open(registry, "r", encoding="utf-8") as f:
        data = json.load(f)

    if scenario_name not in data:
        fail(f"Scenario '{scenario_name}' not registered")

    spec = data[scenario_name]

    for key in ["writer_of_record", "primary_artifact", "min_rows", "max_rows"]:
        if key not in spec:
            fail(f"Scenario '{scenario_name}' missing required key: {key}")

    info(f"Scenario: {scenario_name}")
    info(f"Writer-of-record: {spec['writer_of_record']}")
    info(f"Primary artifact: {spec['primary_artifact']}")
    info(f"Row bounds: {spec['min_rows']}–{spec['max_rows']}")

    return spec

def enforce_writer_of_record(spec):
    wor = spec["writer_of_record"]
    wor_path = REPO_ROOT / wor
    if not wor_path.exists():
        fail(f"Writer-of-record script not found: {wor}")
    info("Writer-of-record verified")

def enforce_demo_bounds(spec):
    if spec["min_rows"] < 25 or spec["max_rows"] > 50:
        fail("Invalid demo row bounds (must be 25–50)")
    info("Demo bounds valid")

def run_preflight(scenario_name: str):
    print("\n🚦 PREFLIGHT CONTRACT CHECK\n" + "-" * 50)
    enforce_reset_prompt_exists()
    load_schema_floor()
    spec = enforce_scenario_registry(scenario_name)
    enforce_writer_of_record(spec)
    enforce_demo_bounds(spec)
    print("\n✅ PREFLIGHT PASSED — SAFE TO ENRICH\n")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        fail("Usage: python3 preflight_contract.py <scenario_name>")
    run_preflight(sys.argv[1])
