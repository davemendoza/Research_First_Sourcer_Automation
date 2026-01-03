#!/usr/bin/env python3
"""
AI Talent Engine — Safety Preflight Gate
Version: Day4-v1.0
Date: 2025-12-30
Author: L. David Mendoza
© 2025 L. David Mendoza. All Rights Reserved.

Purpose
-------
Centralized, mandatory safety validation layer.
This module performs NO execution and NO mutation.
It validates intent, state, and invariants before any run.
"""

import sys
import argparse
from pathlib import Path

PROJECT_ROOT_NAME = "Research_First_Sourcer_Automation"
REQUIRED_FILES = [
    "run_all.py",
    "AI_Talent_Schema_Rules.md",
    ".schema_hash",
]
DEMO_BLACKLIST_FILE = ".demo_file_blacklist"


def fail(reason: str) -> None:
    print(f"\n❌ SAFETY PREFLIGHT FAILED\nReason: {reason}\n")
    sys.exit(2)


def info(msg: str) -> None:
    print(f"ℹ️  {msg}")


def confirm_project_root() -> None:
    cwd = Path.cwd()
    if cwd.name != PROJECT_ROOT_NAME:
        fail(f"Wrong working directory: {cwd}\nExpected repo root: {PROJECT_ROOT_NAME}")
    info("Project root verified.")


def confirm_required_files() -> None:
    for f in REQUIRED_FILES:
        if not Path(f).exists():
            fail(f"Required file missing: {f}")
    info("Required core files present.")


def confirm_schema_hash() -> None:
    hash_file = Path(".schema_hash")
    if hash_file.stat().st_size == 0:
        fail(".schema_hash exists but is empty")
    info("Schema hash present and non-empty.")


def enforce_demo_blacklist(target: str) -> None:
    bl = Path(DEMO_BLACKLIST_FILE)
    if not bl.exists():
        return
    blocked = [line.strip() for line in bl.read_text().splitlines() if line.strip()]
    if target in blocked:
        fail(f"Execution target '{target}' is explicitly blacklisted")
    info("Demo blacklist check passed.")


def confirm_intent(args) -> None:
    if args.live_run and not args.confirm:
        fail("Live run requested without --confirm flag")
    if args.live_run:
        info("LIVE RUN confirmed by user.")
    else:
        info("Dry-run mode enforced.")


def parse_args():
    parser = argparse.ArgumentParser(
        description="Safety preflight gate (no execution occurs here)."
    )
    parser.add_argument("--target", required=True)
    parser.add_argument("--live-run", action="store_true")
    parser.add_argument("--confirm", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    confirm_project_root()
    confirm_required_files()
    confirm_schema_hash()
    enforce_demo_blacklist(args.target)
    confirm_intent(args)
    info("Safety preflight PASSED. Execution may proceed.\n")


if __name__ == "__main__":
    main()
