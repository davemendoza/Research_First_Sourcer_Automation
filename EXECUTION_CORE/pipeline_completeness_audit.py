#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EXECUTION_CORE/pipeline_completeness_audit.py
============================================================
PIPELINE COMPLETENESS & CONTINUITY AUDIT (READ-ONLY)

Maintainer: L. David Mendoza © 2026
Version: v1.0.0

Purpose
- Verify that all required pipeline modules exist
- Verify they are importable
- Verify expected callable entrypoints are present
- Verify run_safe.py references all required stages
- Catch missing / overlooked files early

This file:
- Does NOT mutate data
- Does NOT run the pipeline
- Does NOT require network access
"""

from __future__ import annotations

import importlib
import inspect
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
EXEC = REPO_ROOT / "EXECUTION_CORE"
RUN_SAFE = EXEC / "run_safe.py"

REQUIRED_MODULES = {
    # Core orchestration
    "seed_locator": ["resolve_seed_csv"],
    "output_guard": ["enforce_outputs_root_clean"],
    "output_namer": ["build_paths"],
    "csv_integrity_guard": ["enforce_csv_integrity"],
    "runtime_tracker": ["RuntimeTracker"],
    "completion_notifier": ["notify"],

    # Scenario + anchors
    "people_scenario_resolver": ["resolve_scenario"],
    "anchor_exhaustion_pass": ["process_csv"],

    # PEOPLE LAYER (critical)
    "people_discovery_from_hubs": ["process_csv"],
    "people_projection_from_anchors": ["process_csv"],

    # Identity & enrichment
    "people_source_github": ["process_csv"],
    "name_resolution_pass": ["process_csv"],
    "row_role_materialization_pass": ["process_csv"],
    "canonical_schema_mapper": ["process_csv"],

    # Signal layers
    "phase6_ai_stack_signals": ["process_csv"],
    "phase7_oss_contribution_intel": ["process_csv"],

    # Narrative & density
    "post_run_narrative_pass": ["process_csv"],
    "required_fields_densifier": ["process_csv"],

    # Output
    "canonical_people_writer": ["write_canonical_people_csv"],
}

def fail(msg: str) -> None:
    print(f"❌ {msg}")
    sys.exit(1)

def ok(msg: str) -> None:
    print(f"✔ {msg}")

def audit_imports() -> None:
    ok("Auditing module presence & imports...")
    for mod, funcs in REQUIRED_MODULES.items():
        try:
            m = importlib.import_module(f"EXECUTION_CORE.{mod}")
        except Exception as e:
            fail(f"Missing or non-importable module: {mod} ({e})")

        for fn in funcs:
            if not hasattr(m, fn):
                fail(f"Module {mod} missing required symbol: {fn}")

    ok("All required modules importable with expected symbols")

def audit_run_safe_wiring() -> None:
    ok("Auditing run_safe.py wiring...")
    text = RUN_SAFE.read_text(encoding="utf-8")

    missing = []
    for mod in REQUIRED_MODULES.keys():
        if mod not in text:
            missing.append(mod)

    if missing:
        fail(f"run_safe.py does not reference modules: {', '.join(missing)}")

    ok("run_safe.py references all required pipeline modules")

def audit_file_presence() -> None:
    ok("Auditing file presence on disk...")
    for mod in REQUIRED_MODULES.keys():
        path = EXEC / f"{mod}.py"
        if not path.exists():
            fail(f"Expected file missing: {path}")

    ok("All required files present on disk")

def main() -> None:
    print("\n=== PIPELINE COMPLETENESS AUDIT ===\n")
    audit_file_presence()
    audit_imports()
    audit_run_safe_wiring()
    print("\n🎯 PIPELINE FILE COMPLETENESS: PASS\n")

if __name__ == "__main__":
    main()
