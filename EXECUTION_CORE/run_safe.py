#!/usr/bin/env python3
# ==============================================================================
# AI TALENT ENGINE – SIGNAL INTELLIGENCE
# Proprietary and Confidential
# © 2025–2026 L. David Mendoza. All Rights Reserved.
# ==============================================================================
#
# This file contains proprietary intellectual property and trade secrets of
# L. David Mendoza and is part of the AI Talent Engine – Signal Intelligence system.
#
# Unauthorized access, use, copying, modification, distribution, disclosure,
# reverse engineering, or derivative use, in whole or in part, is strictly
# prohibited without prior written authorization.
#
# ==============================================================================

# -*- coding: utf-8 -*-
"""
EXECUTION_CORE/run_safe.py
============================================================
GOLD STANDARD RUNNER — PHASES 4 → 5 → 6 → 7 (EXPLICIT, AUDITABLE)

Version: v7.0.0-runner-provisional-tier-lifecycle
Maintainer: Dave Mendoza © 2026

CONTRACT (LOCKED)
- Phase 4 tiers are PROVISIONAL seed-time indicators.
- Determinant strength is constructed downstream (Phases 6–7).
- DEMO is bounded and must never be blocked by Tier 1–2 scarcity.
- SCENARIO is strict and may fail closed if Tier 1–2 are absent.

OUTPUTS
OUTPUTS/<mode>/<role_slug>/<timestamp>/
  PHASE_04/
  PHASE_05/
  PHASE_06/
  PHASE_07/

CHANGELOG
- v7.0.0
  - Prints determinant lifecycle banner.
  - Enforces phase-by-phase row invariants.
  - Calls Phase 4 with seed_hub_path=None (Phase 4 resolves the correct hub).
  - Preserves explicit wiring 4→5→6→7.

GIT (SSH)
  git add EXECUTION_CORE/run_safe.py
  git commit -m "Runner: explicit 4-7 wiring + determinant lifecycle banner + invariants"
  git push
"""

from __future__ import annotations

import csv
import sys
import time
from datetime import datetime
from pathlib import Path

from EXECUTION_CORE.phase4_seed_materializer import (
    DEFAULT_SEED_HUB,
    materialize_seed_csv,
    SeedMaterializationError,
)
from EXECUTION_CORE.phase5_passthrough import process_csv as phase5_process
from EXECUTION_CORE.phase6_ai_stack_signals import process_csv as phase6_process
from EXECUTION_CORE.phase7_oss_contribution_intel import process_csv as phase7_process


REPO_ROOT = Path(__file__).resolve().parents[1]
OUTPUTS_ROOT = REPO_ROOT / "OUTPUTS"

MODE_DEMO = "demo"
MODE_SCENARIO = "scenario"

ROLE_ALIASES = {
    "frontier": "frontier_ai_research_scientist",
}

ROLE_CANONICAL = {
    "frontier_ai_research_scientist": "Frontier AI Research Scientist",
}


def _fail(msg: str) -> None:
    raise RuntimeError(msg)


def _assert_root() -> None:
    if Path.cwd().resolve() != REPO_ROOT:
        _fail(f"Must run from repository root: {REPO_ROOT}")


def _parse(argv: list[str]) -> tuple[str, str]:
    if len(argv) < 3:
        _fail("Usage: python3 -m EXECUTION_CORE.run_safe demo|scenario <role>")
    mode = argv[1].strip()
    role = argv[2].strip()
    if mode not in (MODE_DEMO, MODE_SCENARIO):
        _fail("First argument must be 'demo' or 'scenario'")
    return mode, role


def _count_rows(csv_path: Path) -> int:
    if not csv_path.exists():
        _fail(f"Missing output CSV: {csv_path}")
    with csv_path.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return sum(1 for _ in reader)


def main(argv: list[str]) -> None:
    _assert_root()
    mode, raw_role = _parse(argv)

    role_slug = ROLE_ALIASES.get(raw_role, raw_role)
    if role_slug not in ROLE_CANONICAL:
        _fail(f"Unknown role: {role_slug}")
    role_name = ROLE_CANONICAL[role_slug]

    print("\n[RUNNER CONTRACT]")
    print("Phase 4 tiers are PROVISIONAL. Determinant strength is constructed in Phases 6–7.")
    print("DEMO is bounded and must not be blocked by Tier scarcity.")
    print("SCENARIO is strict Tier 1–2 and may fail closed.\n")

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    run_dir = OUTPUTS_ROOT / mode / role_slug / ts
    p4_dir = run_dir / "PHASE_04"
    p5_dir = run_dir / "PHASE_05"
    p6_dir = run_dir / "PHASE_06"
    p7_dir = run_dir / "PHASE_07"

    for d in (p4_dir, p5_dir, p6_dir, p7_dir):
        d.mkdir(parents=True, exist_ok=True)

    t0 = time.time()

    # ---------------- PHASE 4 ----------------
    try:
        p4 = materialize_seed_csv(
            role=role_name,
            mode=mode,
            seed_hub_path=None,
            output_dir=p4_dir,
        )
    except SeedMaterializationError as e:
        _fail(str(e))

    print("[PHASE 4]")
    print(f"Seed hub resolved: {DEFAULT_SEED_HUB}")
    print(f"Rows written: {p4.rows_written}")
    print(f"All-tier distribution (usable rows): {p4.all_tier_distribution}")
    print(f"Used-tier distribution (emitted CSV): {p4.tier_distribution}")
    print(f"Policy note: {p4.note}")

    if p4.rows_written == 0:
        _fail("Phase 4 produced zero rows (unexpected).")

    p4_csv = Path(p4.output_csv)

    # ---------------- PHASE 5 ----------------
    p5_csv = p5_dir / f"{role_slug}_05.csv"
    phase5_process(str(p4_csv), str(p5_csv))
    p5_rows = _count_rows(p5_csv)

    print("\n[PHASE 5]")
    print(f"Rows in: {p4.rows_written} -> Rows out: {p5_rows}")
    if p5_rows == 0:
        _fail("Phase 5 dropped all rows.")

    # ---------------- PHASE 6 ----------------
    p6_csv = p6_dir / f"{role_slug}_06.csv"
    phase6_process(str(p5_csv), str(p6_csv))
    p6_rows = _count_rows(p6_csv)

    print("\n[PHASE 6]")
    print(f"Rows in: {p5_rows} -> Rows out: {p6_rows}")
    if p6_rows == 0:
        _fail("Phase 6 dropped all rows.")

    # ---------------- PHASE 7 ----------------
    p7_csv = p7_dir / f"{role_slug}_07.csv"
    phase7_process(str(p6_csv), str(p7_csv))
    p7_rows = _count_rows(p7_csv)

    print("\n[PHASE 7]")
    print(f"Rows in: {p6_rows} -> Rows out: {p7_rows}")
    if p7_rows == 0:
        _fail("Phase 7 dropped all rows.")

    mins = (time.time() - t0) / 60.0
    print("\n[SUCCESS]")
    print(f"Final output: {p7_csv}")
    print(f"Final rows: {p7_rows}")
    print(f"Elapsed minutes: {mins:.2f}")


if __name__ == "__main__":
    main(sys.argv)
