#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
frontier_runner.py

Permanent, contract-compliant runner for the 'frontier' scenario.

Responsibilities:
- Enforce upstream people inventory gate
- Invoke the canonical AI Talent Engine scenario runner
- Pass the scenario name deterministically
- Locate and return the generated CSV path

Non-responsibilities:
- No scenario validation
- No post-processing or slicing
- No stdout scraping
- No path guessing outside the known output directory
"""

from __future__ import annotations

import sys
import subprocess
import time
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent
OUTPUT_DIR = REPO_ROOT / "output"
INVENTORY_GATE = REPO_ROOT / "inventory_gate.py"
SCENARIO_RUNNER = REPO_ROOT / "ai_talent_scenario_runner.py"


def _enforce_inventory_gate() -> None:
    """
    Hard-stop execution if upstream people inventory is missing or empty.
    This is non-negotiable and prevents silent empty demos.
    """
    subprocess.run(
        [sys.executable, str(INVENTORY_GATE)],
        check=True,
    )


def _latest_frontier_csv() -> Path:
    candidates = sorted(
        OUTPUT_DIR.glob("results_frontier_*.csv"),
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )
    if not candidates:
        raise RuntimeError(
            "No results_frontier_*.csv found in output/ after frontier execution."
        )
    return candidates[0]


def run_frontier(mode: str = "demo") -> str:
    # Enforce invariant BEFORE any frontier execution
    _enforce_inventory_gate()

    cmd = [
        sys.executable,
        str(SCENARIO_RUNNER),
        "--scenario",
        "frontier",
    ]

    subprocess.run(cmd, check=True)

    time.sleep(0.5)

    csv_path = _latest_frontier_csv()
    return str(csv_path)


if __name__ == "__main__":
    print(run_frontier("demo"))


"""
Changelog
- v1.0.2-frontier-runner-path-fix (2026-01-01)
  - Corrected scenario runner target to ai_talent_scenario_runner.py
  - Retained unconditional inventory gate enforcement
  - No change to outputs or invocation semantics

Validation Steps
1) With valid people inventory:
   python3 frontier_runner.py
   → Gate passes, scenario runs, CSV path printed.

2) Without people inventory:
   mv outputs/people/people_master.csv /tmp/people_master.csv.bak
   python3 frontier_runner.py
   → Hard-fails via inventory_gate.py
   mv /tmp/people_master.csv.bak outputs/people/people_master.csv

Git Commands (SSH preferred)
git status
git add frontier_runner.py
git commit -m "Fix: frontier runner invoke canonical scenario runner"
git push
"""
