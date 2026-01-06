#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
AI Talent Engine — People Scenario Resolver
File: EXECUTION_CORE/people_scenario_resolver.py

Author: © 2026 L. David Mendoza. All rights reserved.
Version: v1.0.1-resolver-valid-no-phantom-calls
Date: 2026-01-06

ROLE (LOCKED)
- Provide a small, deterministic helper to produce a Phase 1 people dataframe for a given scenario.
- This module does NOT enrich. It does NOT filter. It does NOT fabricate.
- Best practice entrypoint remains EXECUTION_CORE/run_safe.py.

WHY THIS FILE EXISTS
- Some scripts may import a resolver helper.
- Prior versions were invalid (contained literal "..." and called a non-existent function).
- This version is valid, minimal, and consistent with the repo-root Phase 1 runner.

VALIDATION
1) python3 -m py_compile EXECUTION_CORE/people_scenario_resolver.py
2) python3 -c "from EXECUTION_CORE.people_scenario_resolver import resolve_people_inventory_df; print('ok')"

GIT (SSH)
git status
git add EXECUTION_CORE/people_scenario_resolver.py
git commit -m "Fix people_scenario_resolver: valid helper, no phantom calls [v1.0.1]"
git push
"""

from __future__ import annotations

import csv
import subprocess
import sys
from pathlib import Path
from typing import Optional

import pandas as pd


REPO_ROOT_PHASE1_RUNNER = "run_people_pipeline.py"


def resolve_people_inventory_df(
    mode: str,
    scenario: str,
    out_dir: Optional[str] = None,
    detail_lookups: int = 1,
) -> pd.DataFrame:
    """
    Phase 1 only.
    Calls repo-root run_people_pipeline.py to produce people_master.csv, then returns it as a DataFrame.

    mode: demo or scenario
    scenario: scenario name, ex: frontier_ai_scientist
    out_dir: if provided, passed through to runner; otherwise defaults to outputs/people/<scenario>_<MODE>
    """
    mode = (mode or "").strip().lower()
    scenario = (scenario or "").strip()

    if mode not in ("demo", "scenario"):
        raise ValueError("mode must be 'demo' or 'scenario'")
    if not scenario:
        raise ValueError("scenario cannot be empty")

    runner = Path(REPO_ROOT_PHASE1_RUNNER)
    if not runner.is_file():
        raise FileNotFoundError(f"Missing Phase 1 runner at repo root: {REPO_ROOT_PHASE1_RUNNER}")

    if out_dir:
        out_dir_path = Path(out_dir)
    else:
        out_dir_path = Path("outputs") / "people" / f"{scenario}_{mode.upper()}"

    out_dir_path.mkdir(parents=True, exist_ok=True)

    cmd = [
        sys.executable,
        str(runner),
        "--scenario",
        scenario,
        "--detail-lookups",
        str(int(detail_lookups)),
        "--out-dir",
        str(out_dir_path),
    ]

    if mode == "demo":
        cmd.extend(["--min-people", "25", "--hard-cap-total", "50"])

    rc = subprocess.call(cmd)
    if rc != 0:
        raise RuntimeError(f"Phase 1 runner failed with exit code: {rc}")

    master_csv = out_dir_path / "people_master.csv"
    if not master_csv.is_file():
        raise FileNotFoundError(f"Phase 1 did not produce expected CSV: {master_csv}")

    # Load to DataFrame
    with master_csv.open("r", encoding="utf-8", errors="replace", newline="") as f:
        reader = csv.DictReader(f)
        rows = [dict(r) for r in reader]

    df = pd.DataFrame(rows)
    if df.empty:
        raise RuntimeError("Phase 1 produced an empty dataframe (header-only or no rows).")

    return df
