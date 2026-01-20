#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EXECUTION_CORE/run_safe.py
============================================================
SINGLE AUTHORITATIVE PIPELINE ENTRYPOINT (LOCKED, REWIRED)

Maintainer: L. David Mendoza © 2026
Version: v3.3.0

What this fixes (LOCKED)
- Seeds resolved ONLY via seed_locator.py (no OUTPUTS-root seeds)
- Outputs routed ONLY via output_namer.py (unique timestamped filenames + LATEST.csv)
- OUTPUTS root contract enforced via output_guard.py
- Deterministic post-run narrative densification wired (post_run_narrative_pass.py)
- Fail-closed integrity gate wired (csv_integrity_guard.py)
- Runtime ETA wired (runtime_tracker.py, fail-open)
- Completion notifier wired (completion_notifier.py, fail-open)

Pipeline (deterministic)
seed -> anchors -> github -> name -> role_materialize -> schema81 -> phase6 -> phase7
-> post_run_narrative -> canonical write -> integrity_guard -> notify

Usage
AI_TALENT_MODE=demo|scenario|gpt_slim python3 -m EXECUTION_CORE.run_safe <scenario_key>
"""

from __future__ import annotations


from EXECUTION_CORE.ai_role_registry import list_roles
import os
import sys
import time
import shutil
import csv
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


def _resolve_mode() -> str:
    env_mode = (os.environ.get("AI_TALENT_MODE") or "").strip().lower()
    if env_mode in ("demo", "scenario", "gpt_slim"):
        return env_mode
    return "demo"


def _count_csv_rows(path: Path) -> int:
    try:
        with path.open(newline="", encoding="utf-8") as f:
            r = csv.reader(f)
            _ = next(r, None)  # header
            return sum(1 for _ in r)
    except Exception:
        return -1


# ──────────────────────────────────────────────────────────────
# LOCKED IMPORTS (no guessing)
# ──────────────────────────────────────────────────────────────

from EXECUTION_CORE.output_guard import enforce_outputs_root_clean
from EXECUTION_CORE.output_namer import build_paths
from EXECUTION_CORE.seed_locator import resolve_seed_csv, SeedResolutionError
from EXECUTION_CORE.csv_integrity_guard import enforce_csv_integrity, CSVIntegrityError
from EXECUTION_CORE.runtime_tracker import RuntimeTracker
from EXECUTION_CORE.completion_notifier import notify

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


def main(argv: list[str]) -> None:
    if len(argv) != 2:
        die("Usage: AI_TALENT_MODE=demo|scenario|gpt_slim python3 -m EXECUTION_CORE.run_safe <scenario_key>")

    scenario_key = argv[1].strip()

    if scenario_key == "--list-roles":
        print("\nCanonical AI Role Types:\n")
        for r in list_roles():
            print(f" - {r}")
        sys.exit(0)
    require(bool(scenario_key), "Scenario key must be non-empty")

    mode = _resolve_mode()
    ts_compact = now_timestamp_compact()
    ts_human = now_timestamp_human()

    # OUTPUTS contract enforced BEFORE any writes
    OUTPUTS_ROOT.mkdir(parents=True, exist_ok=True)
    enforce_outputs_root_clean(REPO_ROOT)

    scenario: Dict[str, Any] = resolve_scenario(scenario_key)
    require(isinstance(scenario, dict), "Scenario resolver must return dict")

    for k in ("SCENARIO_PREFIX", "SCENARIO_SEED", "ROLE_CANONICAL"):
        require(k in scenario and isinstance(scenario[k], str) and scenario[k].strip(), f"Missing/invalid scenario key: {k}")

    prefix = scenario["SCENARIO_PREFIX"].strip()
    seed_key = scenario["SCENARIO_SEED"].strip()
    role = scenario["ROLE_CANONICAL"].strip()

    print("✓ Scenario resolved")
    print(f"  PREFIX: {prefix}")
    print(f"  SEED:   {seed_key}")
    print(f"  ROLE:   {role}")
    print(f"  MODE:   {mode}")

    # Scenario role context for deterministic row binding/narrative phrasing (no fabrication)
    os.environ["AI_TALENT_ROLE_CANONICAL"] = role

    WORK_DIR.mkdir(parents=True, exist_ok=True)

    # Seed resolution (LOCKED) - NEVER from OUTPUTS root
    try:
        seed_csv = resolve_seed_csv(repo_root=REPO_ROOT, prefix=seed_key, mode=mode)
    except SeedResolutionError as e:
        die(str(e))

    require(seed_csv.exists(), f"Resolved seed path does not exist: {seed_csv}")
    print(f"  SEED_CSV: {seed_csv}")

    # Runtime tracker (fail-open)
    tracker = None
    try:
        tracker = RuntimeTracker(REPO_ROOT, mode, prefix)
    except Exception:
        tracker = None

    def stage_start(name: str) -> None:
        if tracker:
            try:
                tracker.start(name)
            except Exception:
                pass

    def stage_end(name: str, remaining: list[str]) -> None:
        if not tracker:
            return
        try:
            d = tracker.end(name)
            elapsed = tracker.elapsed()
            rem = tracker.estimate_remaining(remaining)
            print(f"[✓] {name} in {RuntimeTracker.fmt(d)} | elapsed {RuntimeTracker.fmt(elapsed)} | ETA {RuntimeTracker.fmt(rem)}")
        except Exception:
            return

    # Work files
    p1 = WORK_DIR / f"{prefix}__01_anchors.csv"
    p2 = WORK_DIR / f"{prefix}__02_github.csv"
    p3 = WORK_DIR / f"{prefix}__03_named.csv"
    p3b = WORK_DIR / f"{prefix}__03b_role_bound.csv"
    p4 = WORK_DIR / f"{prefix}__04_schema_81.csv"
    p5 = WORK_DIR / f"{prefix}__05_phase6.csv"
    p6 = WORK_DIR / f"{prefix}__06_phase7.csv"
    p7 = WORK_DIR / f"{prefix}__07_post_run_narrative.csv"

    remaining = ["anchors", "github", "name", "role_materialize", "schema81", "phase6", "phase7", "post_run_narrative", "canonical_write", "integrity_guard"]

    # anchors
    stage_start("anchors")
    anchors_process_csv(str(seed_csv), str(p1))
    require(p1.exists(), f"Anchor output missing: {p1}")
    remaining = remaining[1:]
    stage_end("anchors", remaining)

    # github
    stage_start("github")
    github_process_csv(str(p1), str(p2))
    require(p2.exists(), f"GitHub output missing: {p2}")
    remaining = remaining[1:]
    stage_end("github", remaining)

    # name
    stage_start("name")
    name_process_csv(str(p2), str(p3))
    require(p3.exists(), f"Name output missing: {p3}")
    remaining = remaining[1:]
    stage_end("name", remaining)

    # role materialize
    stage_start("role_materialize")
    role_materialize_process_csv(str(p3), str(p3b))
    require(p3b.exists(), f"Role materialization output missing: {p3b}")
    remaining = remaining[1:]
    stage_end("role_materialize", remaining)

    # schema81
    stage_start("schema81")
    schema_map_process_csv(str(p3b), str(p4))
    require(p4.exists(), f"Schema81 output missing: {p4}")
    remaining = remaining[1:]
    stage_end("schema81", remaining)

    # phase6
    stage_start("phase6")
    phase6_process_csv(str(p4), str(p5))
    require(p5.exists(), f"Phase6 output missing: {p5}")
    remaining = remaining[1:]
    stage_end("phase6", remaining)

    # phase7
    stage_start("phase7")
    phase7_process_csv(str(p5), str(p6))
    require(p6.exists(), f"Phase7 output missing: {p6}")
    remaining = remaining[1:]
    stage_end("phase7", remaining)

    # post-run narrative densification (deterministic, fill blanks only)
    stage_start("post_run_narrative")
    post_run_narrative_process_csv(str(p6), str(p7))
    require(p7.exists(), f"Post-run narrative output missing: {p7}")
    remaining = remaining[1:]
    stage_end("post_run_narrative", remaining)

    # output naming (unique per run) + write canonical
    paths = build_paths(prefix=prefix, mode=mode, ts_human=ts_human, repo_root=REPO_ROOT)
    if paths.canonical_csv.exists():
        die(f"Refusing to overwrite existing canonical CSV: {paths.canonical_csv}")

    stage_start("canonical_write")
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
    remaining = remaining[1:]
    stage_end("canonical_write", remaining)

    # Update LATEST.csv (copy, deterministic)
    try:
        shutil.copyfile(str(out_csv), str(paths.latest_csv))
    except Exception as e:
        die(f"Failed to update LATEST.csv: {e}")

    # Integrity guard (fail-closed)
    stage_start("integrity_guard")
    try:
        enforce_csv_integrity(out_csv)
    except CSVIntegrityError as e:
        die(str(e))
    remaining = remaining[1:]
    stage_end("integrity_guard", remaining)

    rows_written = _count_csv_rows(out_csv)
    elapsed = RuntimeTracker.fmt(tracker.elapsed()) if tracker else "??:??"

    print("\n✔ PIPELINE COMPLETE")
    print("✔ Canonical CSV:", out_csv)
    print("✔ Latest CSV:   ", paths.latest_csv)
    print("✔ Rows:", rows_written)
    print("✔ Timestamp:", ts_compact)

    # Preview (fail-open)
    if PREVIEW.exists():
        try:
            import subprocess
            subprocess.run([sys.executable, str(PREVIEW), str(out_csv), mode, paths.role_slug], cwd=str(REPO_ROOT))
        except Exception:
            pass

    # Completion notify (fail-open)
    try:
        notify(mode, prefix, "SUCCESS", str(out_csv), int(rows_written if rows_written >= 0 else 0), elapsed)
    except Exception:
        pass


if __name__ == "__main__":
    main(sys.argv)
