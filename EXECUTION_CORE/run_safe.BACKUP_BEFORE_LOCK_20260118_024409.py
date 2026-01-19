#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EXECUTION_CORE/run_safe.py
============================================================
SINGLE AUTHORITATIVE PIPELINE ENTRYPOINT (LOCKED)

Maintainer: L. David Mendoza © 2026
Version: v3.2.1

Pipeline (deterministic):
seed -> anchors -> github -> name -> role_materialize -> schema81 -> phase6 -> phase7 -> canonical write

Phase 1 Locks (NEW)
- OUTPUTS root must contain directories only (demo/scenario/gpt_slim/_ARCHIVE_INTERNAL)
- Canonical outputs are unique per run (timestamped filenames)
- Outputs routed to OUTPUTS/<mode>/<role_slug>/
- LATEST.csv maintained per role (copy-based, cross-platform)
- No overwrites, fail closed

Non-negotiable
- All stage process_csv are called with (input_csv, output_csv)
- Canonical writer requires timestamp and returns output path
- Fail closed (no silent defaults)
- No fabrication
"""

from __future__ import annotations

import os
import sys
import time
import shutil
from pathlib import Path
from typing import Dict, Any

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

EXECUTION_DIR = REPO_ROOT / "EXECUTION_CORE"
OUTPUTS_ROOT = REPO_ROOT / "OUTPUTS"
WORK_DIR = REPO_ROOT / "_work"
PREVIEW = EXECUTION_DIR / "talent_intel_preview.py"

PIPELINE_VERSION = "D30_LOCKED_GOLD_FINAL"


def die(msg: str) -> None:
    print(f"❌ {msg}", file=sys.stderr)
    sys.exit(1)


def require(cond: bool, msg: str) -> None:
    if not cond:
        die(msg)


def now_timestamp_compact() -> str:
    return time.strftime("%Y%m%d_%H%M%S")


def now_timestamp_human() -> str:
    return time.strftime("%Y-%m-%d_%H-%M-%S")


from EXECUTION_CORE.output_guard import enforce_outputs_root_clean
from EXECUTION_CORE.output_namer import build_paths
from EXECUTION_CORE.people_scenario_resolver import resolve_scenario
from EXECUTION_CORE.anchor_exhaustion_pass import process_csv as anchors_process_csv
from EXECUTION_CORE.people_source_github import process_csv as github_process_csv
from EXECUTION_CORE.name_resolution_pass import process_csv as name_process_csv
from EXECUTION_CORE.row_role_materialization_pass import process_csv as role_materialize_process_csv
from EXECUTION_CORE.canonical_schema_mapper import process_csv as schema_map_process_csv
from EXECUTION_CORE.phase6_ai_stack_signals import process_csv as phase6_process_csv
from EXECUTION_CORE.phase7_oss_contribution_intel import process_csv as phase7_process_csv
from EXECUTION_CORE.canonical_people_writer import write_canonical_people_csv


def _resolve_mode(argv: list[str]) -> str:
    # Backward-compatible: if you don't pass mode, defaults to demo.
    # Optional: set env AI_TALENT_MODE to demo|scenario|gpt_slim.
    env_mode = (os.environ.get("AI_TALENT_MODE") or "").strip().lower()
    if env_mode in ("demo", "scenario", "gpt_slim"):
        return env_mode
    return "demo"


def main(argv: list[str]) -> None:
    if len(argv) != 2:
        die("Usage: python3 -m EXECUTION_CORE.run_safe <scenario_key>")

    scenario_key = argv[1].strip()
    require(bool(scenario_key), "Scenario key must be non-empty")

    # Enforce OUTPUTS root contract BEFORE any run artifacts are written
    OUTPUTS_ROOT.mkdir(parents=True, exist_ok=True)
    enforce_outputs_root_clean(REPO_ROOT)

    scenario: Dict[str, Any] = resolve_scenario(scenario_key)
    require(isinstance(scenario, dict), "Scenario resolver must return dict")

    for k in ("SCENARIO_PREFIX", "SCENARIO_SEED", "ROLE_CANONICAL"):
        require(k in scenario and isinstance(scenario[k], str) and scenario[k].strip(), f"Missing/invalid scenario key: {k}")

    prefix = scenario["SCENARIO_PREFIX"].strip()
    seed = scenario["SCENARIO_SEED"].strip()
    role = scenario["ROLE_CANONICAL"].strip()

    mode = _resolve_mode(argv)
    ts_compact = now_timestamp_compact()
    ts_human = now_timestamp_human()

    print("✓ Scenario resolved")
    print(f"  PREFIX: {prefix}")
    print(f"  SEED:   {seed}")
    print(f"  ROLE:   {role}")
    print(f"  MODE:   {mode}")

    # Provide role context for deterministic row binding
    os.environ["AI_TALENT_ROLE_CANONICAL"] = role

    WORK_DIR.mkdir(parents=True, exist_ok=True)

    # Seed contract remains unchanged in Phase 1
    seed_csv = OUTPUTS_ROOT / f"{seed}.csv"
    require(seed_csv.exists(), f"Seed CSV not found: {seed_csv}")

    p1 = WORK_DIR / f"{prefix}__01_anchors.csv"
    p2 = WORK_DIR / f"{prefix}__02_github.csv"
    p3 = WORK_DIR / f"{prefix}__03_named.csv"
    p3b = WORK_DIR / f"{prefix}__03b_role_bound.csv"
    p4 = WORK_DIR / f"{prefix}__04_schema_81.csv"
    p5 = WORK_DIR / f"{prefix}__05_phase6.csv"
    p6 = WORK_DIR / f"{prefix}__06_phase7.csv"

    anchors_process_csv(str(seed_csv), str(p1))
    require(p1.exists(), f"Anchor output missing: {p1}")

    github_process_csv(str(p1), str(p2))
    require(p2.exists(), f"GitHub output missing: {p2}")

    name_process_csv(str(p2), str(p3))
    require(p3.exists(), f"Name output missing: {p3}")

    role_materialize_process_csv(str(p3), str(p3b))
    require(p3b.exists(), f"Role materialization output missing: {p3b}")

    schema_map_process_csv(str(p3b), str(p4))
    require(p4.exists(), f"Schema81 output missing: {p4}")

    phase6_process_csv(str(p4), str(p5))
    require(p5.exists(), f"Phase6 output missing: {p5}")

    phase7_process_csv(str(p5), str(p6))
    require(p6.exists(), f"Phase7 output missing: {p6}")

    # Build unique output paths for this run (no overwrite)
    paths = build_paths(prefix=prefix, mode=mode, ts_human=ts_human, repo_root=REPO_ROOT)

    if paths.canonical_csv.exists():
        die(f"Refusing to overwrite existing canonical CSV: {paths.canonical_csv}")

    # Canonical writer writes into OUTPUTS/<mode>/<role_slug>/ with unique filename
    canonical_out = write_canonical_people_csv(
        canonical_csv_path=str(p6),
        output_dir=str(paths.out_dir),
        output_prefix=paths.role_slug,
        timestamp=ts_compact,
        fixed_filename=paths.canonical_csv.name,
        pipeline_version=PIPELINE_VERSION,
        metadata_json_path=str(paths.metadata_json),
    )

    out_csv = Path(canonical_out).resolve()
    require(out_csv.exists(), f"Canonical CSV was not written: {out_csv}")

    # Update LATEST.csv (copy, deterministic)
    try:
        shutil.copyfile(str(out_csv), str(paths.latest_csv))
    except Exception as e:
        die(f"Failed to update LATEST.csv: {e}")

    print("\n✔ PIPELINE COMPLETE")
    print("✔ Canonical CSV:", out_csv)
    print("✔ Latest CSV:   ", paths.latest_csv)
    print("✔ Timestamp:", ts_compact)

    if PREVIEW.exists():
        try:
            import subprocess
            subprocess.run([sys.executable, str(PREVIEW), str(out_csv), mode, paths.role_slug], cwd=str(REPO_ROOT))
        except Exception:
            pass


if __name__ == "__main__":
    main(sys.argv)
