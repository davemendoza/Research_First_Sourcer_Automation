#!/usr/bin/env python3
"""
AI Talent Engine – Inventory Gate (Hard Stop: People Inventory Required)
© 2025 L. David Mendoza

Version: v1.0.0-inventory-gate-hardstop
Last Updated: 2026-01-01

Purpose
- Enforce a permanent, non-negotiable invariant:
  Downstream scenario runners and demos MUST NOT proceed if upstream people inventory is missing or empty.
- Specifically, this gate validates that:
  outputs/people/people_master.csv exists AND contains at least 1 data row (header excluded).

Why this exists (root-cause fix)
- You experienced "successful" pipeline runs that produced EMPTY people CSVs, which then caused all demos/scenarios
  to quietly produce empty downstream artifacts.
- This gate prevents silent failure propagation by hard-failing early with explicit, actionable output.

Non-negotiables enforced here
- HARD FAIL if people inventory is missing or empty.
- Clear, explicit console output explaining exactly what failed and how to fix it.
- NO placeholders, NO demo stubs, NO silent continuation.

Compatibility / Safety
- This script is intentionally tolerant of unknown CLI arguments to avoid breaking existing wrappers.
  It will parse known flags if present and ignore the rest (permanent safety feature).
- It does NOT introduce required flags. It can be run with zero args.

Exit Codes
- 0: Gate passed (people inventory exists and is non-empty).
- 2: Gate failed (missing/empty/unreadable inventory).
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import sys
import time
from pathlib import Path
from typing import Optional, Tuple


DEFAULT_RELATIVE_PEOPLE_MASTER = Path("outputs") / "people" / "people_master.csv"
DEFAULT_MIN_ROWS = 1  # header excluded


def eprint(msg: str) -> None:
    print(msg, file=sys.stderr)


def find_repo_root(start: Path) -> Path:
    """
    Find repo root without assumptions about current working directory.
    Strategy:
    - Walk upward from 'start' and look for .git directory.
    - If not found, fall back to 'start'.
    """
    cur = start.resolve()
    for _ in range(15):
        if (cur / ".git").exists():
            return cur
        parent = cur.parent
        if parent == cur:
            break
        cur = parent
    return start.resolve()


def resolve_people_master_path(repo_root: Path, cli_path: Optional[str]) -> Path:
    """
    Resolution order:
    1) --people-csv (if provided)
    2) PEOPLE_MASTER_CSV env var (if set)
    3) repo_root/outputs/people/people_master.csv (default)
    """
    if cli_path:
        return Path(cli_path).expanduser().resolve()

    env_path = os.environ.get("PEOPLE_MASTER_CSV", "").strip()
    if env_path:
        return Path(env_path).expanduser().resolve()

    return (repo_root / DEFAULT_RELATIVE_PEOPLE_MASTER).resolve()


def count_csv_data_rows(csv_path: Path) -> Tuple[int, int]:
    """
    Returns (data_rows, total_lines_best_effort).
    data_rows excludes header.
    """
    data_rows = 0
    total_lines = 0

    with csv_path.open("r", encoding="utf-8", newline="") as f:
        reader = csv.reader(f)
        for i, row in enumerate(reader):
            total_lines += 1
            if i == 0:
                # header
                continue
            if row and any(cell.strip() for cell in row):
                data_rows += 1

    return data_rows, total_lines


def write_gate_log(repo_root: Path, payload: dict) -> None:
    """
    Best-effort logging to logs/preflight_gate.jsonl (append).
    Never blocks the gate decision if logging fails.
    """
    try:
        logs_dir = repo_root / "logs"
        logs_dir.mkdir(parents=True, exist_ok=True)
        path = logs_dir / "preflight_gate.jsonl"
        payload = dict(payload)
        payload["ts_unix"] = int(time.time())
        with path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(payload, ensure_ascii=False) + "\n")
    except Exception:
        pass


def main() -> int:
    parser = argparse.ArgumentParser(
        description="AI Talent Engine: Inventory gate (hard-fail if people_master.csv missing/empty).",
        add_help=True,
    )
    parser.add_argument(
        "--people-csv",
        default=None,
        help="Path to people_master.csv (optional). If omitted, uses PEOPLE_MASTER_CSV env var or repo default.",
    )
    parser.add_argument(
        "--min-rows",
        type=int,
        default=int(os.environ.get("PEOPLE_MIN_ROWS", str(DEFAULT_MIN_ROWS))),
        help="Minimum required data rows (header excluded). Default 1. Can also set PEOPLE_MIN_ROWS env var.",
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Reduce console output (still hard-fails with errors).",
    )

    # Tolerate unknown args to avoid breaking existing wrappers.
    args, unknown = parser.parse_known_args()

    script_dir = Path(__file__).resolve().parent
    repo_root = find_repo_root(script_dir)
    people_csv = resolve_people_master_path(repo_root, args.people_csv)

    min_rows = args.min_rows
    if min_rows < 1:
        min_rows = 1

    if not args.quiet:
        print("Inventory Gate: People inventory must exist and be non-empty.")
        print(f"Repo root: {repo_root}")
        print(f"People CSV: {people_csv}")
        if unknown:
            print(f"Note: ignoring unknown args to preserve wrapper compatibility: {' '.join(unknown)}")

    # Existence check
    if not people_csv.exists():
        msg = (
            "HARD FAILURE: Upstream people inventory is missing.\n"
            f"Expected people CSV at:\n  {people_csv}\n\n"
            "This gate prevents downstream demos/scenarios from generating empty outputs.\n\n"
            "Fix:\n"
            "1) Run upstream enumeration:\n"
            "   python3 run_people_pipeline.py --scenario frontier\n"
            "2) Verify the file exists and is non-empty:\n"
            f"   wc -l {people_csv}\n"
            f"   head -n 5 {people_csv}\n"
        )
        eprint(msg)
        write_gate_log(repo_root, {"gate": "people_inventory", "status": "fail_missing", "path": str(people_csv)})
        return 2

    # Readability + row-count check
    try:
        data_rows, total_lines = count_csv_data_rows(people_csv)
    except Exception as ex:
        msg = (
            "HARD FAILURE: Upstream people inventory exists but cannot be read.\n"
            f"Path:\n  {people_csv}\n\n"
            f"Error: {type(ex).__name__}: {ex}\n\n"
            "Fix:\n"
            "1) Re-run enumeration:\n"
            "   python3 run_people_pipeline.py --scenario frontier\n"
            "2) Confirm the CSV is readable:\n"
            f"   head -n 5 {people_csv}\n"
        )
        eprint(msg)
        write_gate_log(repo_root, {"gate": "people_inventory", "status": "fail_unreadable", "path": str(people_csv)})
        return 2

    if data_rows < min_rows:
        msg = (
            "HARD FAILURE: Upstream people inventory is EMPTY (or below minimum).\n"
            f"Path:\n  {people_csv}\n"
            f"CSV total lines (best effort): {total_lines}\n"
            f"CSV data rows (header excluded): {data_rows}\n"
            f"Minimum required data rows: {min_rows}\n\n"
            "This is not acceptable because downstream scenario/demo CSVs would contain no people.\n\n"
            "Fix:\n"
            "1) Run upstream enumeration (real data):\n"
            "   python3 run_people_pipeline.py --scenario frontier\n"
            "2) Verify non-empty output:\n"
            f"   wc -l {people_csv}\n"
            f"   head -n 5 {people_csv}\n"
        )
        eprint(msg)
        write_gate_log(
            repo_root,
            {
                "gate": "people_inventory",
                "status": "fail_empty",
                "path": str(people_csv),
                "data_rows": data_rows,
                "min_rows": min_rows,
            },
        )
        return 2

    if not args.quiet:
        print("GATE PASS: Upstream people inventory exists and is non-empty.")
        print(f"Data rows (header excluded): {data_rows}")
        print("Downstream scenario runners may proceed.")

    write_gate_log(
        repo_root,
        {"gate": "people_inventory", "status": "pass", "path": str(people_csv), "data_rows": data_rows, "min_rows": min_rows},
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


"""
Changelog
- v1.0.0-inventory-gate-hardstop (2026-01-01)
  - New permanent gate: hard-fail if outputs/people/people_master.csv missing or empty.
  - Adds explicit, actionable error messaging to prevent silent demo/scenario failures.
  - Tolerates unknown CLI args to avoid breaking existing wrappers (parse_known_args).

Validation Steps (run from repo root)
1) Gate should PASS after enumeration:
   python3 run_people_pipeline.py --scenario frontier
   python3 inventory_gate.py

2) Gate should FAIL if CSV is missing:
   mv outputs/people/people_master.csv /tmp/people_master.csv.bak
   python3 inventory_gate.py ; echo $?
   mv /tmp/people_master.csv.bak outputs/people/people_master.csv

3) Gate should FAIL if CSV is empty (simulate by writing header-only):
   python3 - <<'PY'
from pathlib import Path
p = Path("outputs/people/people_master.csv")
bak = Path("outputs/people/people_master.csv.bak")
bak.write_bytes(p.read_bytes())
lines = p.read_text(encoding="utf-8").splitlines()
p.write_text(lines[0] + "\n", encoding="utf-8")
PY
   python3 inventory_gate.py ; echo $?
   python3 - <<'PY'
from pathlib import Path
p = Path("outputs/people/people_master.csv")
bak = Path("outputs/people/people_master.csv.bak")
p.write_bytes(bak.read_bytes())
bak.unlink(missing_ok=True)
PY

Git Commands (SSH preferred)
git status
git add inventory_gate.py
git commit -m "Add: inventory gate hard-stop for missing/empty people_master.csv"
git push
"""
