#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EXECUTION_CORE/run_safe.py
============================================================
SINGLE AUTHORITATIVE PIPELINE ENTRYPOINT (LOCKED, REWIRED)
"""
from __future__ import annotations

import csv
import os
import shutil
import sys
import threading
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

EXECUTION_DIR = REPO_ROOT / "EXECUTION_CORE"
OUTPUTS_ROOT = REPO_ROOT / "OUTPUTS"
WORK_DIR = REPO_ROOT / "_work"
PREVIEW_SCRIPT = EXECUTION_DIR / "talent_intel_preview.py"

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


def _resolve_mode() -> str:
    env_mode = (os.environ.get("AI_TALENT_MODE") or "").strip().lower()
    if env_mode in ("demo", "scenario", "gpt_slim"):
        return env_mode
    return "demo"


def _count_csv_rows(path: Path) -> int:
    try:
        with path.open(newline="", encoding="utf-8") as f:
            r = csv.reader(f)
            _ = next(r, None)
            return sum(1 for _ in r)
    except Exception:
        return -1


from EXECUTION_CORE.ai_role_registry import list_roles
from EXECUTION_CORE.output_guard import enforce_outputs_root_clean
from EXECUTION_CORE.output_namer import build_paths
from EXECUTION_CORE.seed_locator import resolve_seed_csv, SeedResolutionError
from EXECUTION_CORE.csv_integrity_guard import enforce_csv_integrity, CSVIntegrityError

from EXECUTION_CORE.runtime_tracker import RuntimeTracker
from EXECUTION_CORE.progress_heartbeat import ProgressHeartbeat
from EXECUTION_CORE.enrichment_counters import EnrichmentCounters
from EXECUTION_CORE.talent_intel_preview import TalentIntelPreview
from EXECUTION_CORE.completion_notifier import notify_completion

from EXECUTION_CORE.people_scenario_resolver import resolve_scenario
from EXECUTION_CORE.anchor_exhaustion_pass import process_csv as anchors_process_csv
from EXECUTION_CORE.people_source_github import process_csv as github_process_csv
from EXECUTION_CORE.name_resolution_pass import process_csv as name_process_csv
from EXECUTION_CORE.row_role_materialization_pass import process_csv as role_materialize_process_csv
from EXECUTION_CORE.canonical_schema_mapper import process_csv as schema_map_process_csv
from EXECUTION_CORE.phase6_ai_stack_signals import process_csv as phase6_process_csv
from EXECUTION_CORE.phase7_oss_contribution_intel import process_csv as phase7_process_csv
from EXECUTION_CORE.post_run_narrative_pass import process_csv as post_run_narrative_process_csv
from EXECUTION_CORE.canonical_people_writer import write_canonical_people_csv


def main(argv: List[str]) -> None:
    if len(argv) != 2:
        die("Usage: AI_TALENT_MODE=demo|scenario|gpt_slim python3 -m EXECUTION_CORE.run_safe <scenario_key>")

    scenario_key = argv[1].strip()

    if scenario_key == "--list-roles":
        for r in list_roles():
            print(f" - {r}")
        sys.exit(0)

    mode = _resolve_mode()
    ts_compact = now_timestamp_compact()
    ts_human = now_timestamp_human()

    OUTPUTS_ROOT.mkdir(parents=True, exist_ok=True)
    enforce_outputs_root_clean(REPO_ROOT)

    scenario: Dict[str, Any] = resolve_scenario(scenario_key)
    prefix = scenario["SCENARIO_PREFIX"].strip()
    seed_key = scenario["SCENARIO_SEED"].strip()
    role = scenario["ROLE_CANONICAL"].strip()

    os.environ["AI_TALENT_ROLE_CANONICAL"] = role

    WORK_DIR.mkdir(parents=True, exist_ok=True)

    try:
        seed_csv = resolve_seed_csv(repo_root=REPO_ROOT, prefix=seed_key, mode=mode)
    except SeedResolutionError as e:
        die(str(e))

    # ──────────────────────────────────────────────────────────
    # PHASE 1 FIX: OUTPUT PATHS + OVERWRITE GUARD (HARD)
    # Must occur BEFORE any writer is created or invoked
    # ──────────────────────────────────────────────────────────
    paths = build_paths(prefix=prefix, mode=mode, ts_human=ts_human, repo_root=REPO_ROOT)

    require(not paths.out_dir.exists(),
            f"Refusing to reuse existing output directory: {paths.out_dir}")

    require(not paths.canonical_csv.exists(),
            f"Refusing to overwrite existing canonical CSV: {paths.canonical_csv}")

    require(not paths.metadata_json.exists(),
            f"Refusing to overwrite existing metadata JSON: {paths.metadata_json}")

    # ──────────────────────────────────────────────────────────
    # Pipeline execution (unchanged)
    # ──────────────────────────────────────────────────────────

    p1 = WORK_DIR / f"{prefix}__01_anchors.csv"
    p2 = WORK_DIR / f"{prefix}__02_github.csv"
    p3 = WORK_DIR / f"{prefix}__03_named.csv"
    p3b = WORK_DIR / f"{prefix}__03b_role_bound.csv"
    p4 = WORK_DIR / f"{prefix}__04_schema_81.csv"
    p5 = WORK_DIR / f"{prefix}__05_phase6.csv"
    p6 = WORK_DIR / f"{prefix}__06_phase7.csv"
    p7 = WORK_DIR / f"{prefix}__07_post_run_narrative.csv"

    anchors_process_csv(str(seed_csv), str(p1))
    github_process_csv(str(p1), str(p2))
    name_process_csv(str(p2), str(p3))
    role_materialize_process_csv(str(p3), str(p3b))
    schema_map_process_csv(str(p3b), str(p4))
    phase6_process_csv(str(p4), str(p5))
    phase7_process_csv(str(p5), str(p6))
    post_run_narrative_process_csv(str(p6), str(p7))

    canonical_out = write_canonical_people_csv(
        canonical_csv_path=str(p7),
        output_dir=str(paths.out_dir),
        output_prefix=paths.role_slug,
        timestamp=ts_compact,
        fixed_filename=paths.canonical_csv.name,
        pipeline_version=PIPELINE_VERSION,
        metadata_json_path=str(paths.metadata_json),
    )

    out_csv = Path(canonical_out).resolve()
    require(out_csv.exists(), f"Canonical CSV was not written: {out_csv}")

    shutil.copyfile(str(out_csv), str(paths.latest_csv))

    try:
        enforce_csv_integrity(out_csv)
    except CSVIntegrityError as e:
        die(str(e))

    print("\n✔ PIPELINE COMPLETE")
    print("✔ Canonical CSV:", out_csv)
    print("✔ Rows:", _count_csv_rows(out_csv))
    print("✔ Timestamp:", ts_compact)


if __name__ == "__main__":
    main(sys.argv)
