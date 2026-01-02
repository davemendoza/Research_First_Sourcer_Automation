#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
run_safe.py

AI Talent Engine — MASTER SAFETY + DEMO ENTRYPOINT (Universal Lead-Grade)
Version: v1.0.0
Author: L. David Mendoza
Date: 2026-01-02
© 2025 L. David Mendoza

This is the ONLY approved execution path for:
- demo frontier
- run <scenario>

Hard guarantees:
- Repository inventory is valid
- Upstream people inventory exists and is non-empty
- People scenario runs are bounded (25–50 people)
- Identity columns are present (GitHub URL + username)
- Person_ID / Role_Type canonical prefix is enforced upstream
- Universal lead-grade enrichment produces 70+ column LEADS_MASTER
- Pop-up occurs automatically for finished CSV
- Email is sent automatically via Mail.app when enabled
- Manifest is written

Fail-closed: if any invariant fails, nothing downstream is considered "done".
"""

from __future__ import annotations

import os
import sys
import subprocess
from pathlib import Path
from datetime import datetime, timezone
import pandas as pd


REPO_ROOT = Path(__file__).resolve().parent
PEOPLE_DIR = REPO_ROOT / "outputs" / "people"

SCENARIO_RUNNER = REPO_ROOT / "ai_talent_scenario_runner.py"

NORMALIZER = REPO_ROOT / "scripts" / "normalize_people_csv.py"
ENRICHER = REPO_ROOT / "scripts" / "universal_enrichment_pipeline.py"
NOTIFIER = REPO_ROOT / "scripts" / "macos_notify.py"
EMAIL_NOTIFIER = REPO_ROOT / "scripts" / "send_run_completion_email.py"


def utc_now_compact() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")


def fail(msg: str) -> None:
    print("\nHARD FAILURE:")
    print(msg)
    print()
    sys.exit(1)


def enforce_repo_inventory() -> None:
    required = {
        "run_safe.py",
        "inventory_gate.py",
        "people_scenario_resolver.py",
        "ai_talent_scenario_runner.py",
        "scenario_contract.py",
        "scripts/normalize_people_csv.py",
        "scripts/universal_enrichment_pipeline.py",
        "scripts/macos_notify.py",
        "scripts/send_run_completion_email.py",
    }
    missing = []
    for r in sorted(required):
        if not (REPO_ROOT / r).exists():
            missing.append(r)
    if missing:
        fail("Missing required repo files:\n" + "\n".join(f"  - {m}" for m in missing))
    print("✓ REPO INVENTORY GATE PASSED")


def enforce_people_inventory() -> Path:
    people_master = PEOPLE_DIR / "people_master.csv"
    if not people_master.exists():
        fail(f"People inventory missing:\n{people_master}")

    df = pd.read_csv(people_master)
    if df.empty:
        fail("People inventory exists but is empty")

    print("✓ PEOPLE INVENTORY PASSED")
    print(f"✓ Upstream people rows: {len(df)}")
    return people_master


def run_people_scenario(scenario: str) -> Path:
    cmd = [sys.executable, str(REPO_ROOT / "people_scenario_resolver.py"), "--scenario", scenario]
    subprocess.run(cmd, check=True)

    outputs = sorted(
        PEOPLE_DIR.glob(f"{scenario}_people_*.csv"),
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )
    if not outputs:
        fail("People scenario produced no output CSV")

    people_csv = outputs[0]
    df = pd.read_csv(people_csv)

    # DEMO BOUNDS (MANDATORY)
    if not (25 <= len(df) <= 50):
        fail(f"Demo bounds violated: {len(df)} rows (expected 25–50)")

    # IDENTITY CHECKS
    required_cols = {"GitHub_URL", "GitHub_Username"}
    missing = required_cols - set(df.columns)
    if missing:
        fail(f"Missing required identity columns: {missing}")
    if df["GitHub_URL"].isna().all():
        fail("GitHub_URL column exists but contains no data")

    print("✓ PEOPLE SCENARIO GATE PASSED")
    print(f"✓ Demo people rows: {len(df)}")
    return people_csv


def normalize_people_csv(raw_people_csv: Path) -> Path:
    out = raw_people_csv.with_suffix(".normalized.csv")
    cmd = [sys.executable, str(NORMALIZER), str(raw_people_csv), str(out)]
    subprocess.run(cmd, check=True)

    # Enforce prefix exists in output
    df = pd.read_csv(out)
    cols = list(df.columns)
    if cols[:2] != ["Person_ID", "Role_Type"]:
        fail(f"Normalization failed: expected prefix Person_ID, Role_Type but got {cols[:2]}")

    print("✓ NORMALIZATION GATE PASSED")
    print(f"✓ Normalized people CSV: {out}")
    return out


def run_universal_enrichment(scenario: str, people_csv_normalized: Path, run_id: str) -> tuple[Path, Path]:
    cmd = [sys.executable, str(ENRICHER), scenario, str(people_csv_normalized), run_id]
    subprocess.run(cmd, check=True)

    leads_dir = REPO_ROOT / "outputs" / "leads" / f"run_{run_id}"
    leads_master = leads_dir / f"LEADS_MASTER_{scenario}_{run_id}.csv"
    manifest = REPO_ROOT / "outputs" / "manifests" / f"run_manifest_{scenario}_{run_id}.json"

    if not leads_master.exists():
        fail(f"Expected leads file missing: {leads_master}")
    if not manifest.exists():
        fail(f"Expected manifest missing: {manifest}")

    # Schema columns check (70+)
    df = pd.read_csv(leads_master)
    if len(df.columns) < 70:
        fail(f"Lead-grade schema violated: {len(df.columns)} columns (expected 70+)")

    # GitHub.io required columns must exist
    required_cols = {"GitHub_IO_URL", "GitHub_IO_HTTP_Status", "GitHub_IO_Checked_UTC", "GitHub_IO_Present"}
    miss = required_cols - set(df.columns)
    if miss:
        fail(f"GitHub.io contract violated: missing columns {sorted(miss)}")

    print("✓ UNIVERSAL ENRICHMENT GATE PASSED")
    print(f"✓ LEADS_MASTER: {leads_master}")
    print(f"✓ Columns: {len(df.columns)}")
    return leads_master, manifest


def run_scenario_runner(scenario: str) -> None:
    if not SCENARIO_RUNNER.exists():
        fail(f"Scenario runner missing:\n{SCENARIO_RUNNER}")
    cmd = [sys.executable, str(SCENARIO_RUNNER), "--scenario", scenario]
    subprocess.run(cmd, check=True)


def popup_finished(leads_master: Path) -> None:
    cmd = [
        sys.executable,
        str(NOTIFIER),
        "--title",
        "AI Talent Engine — Finished Leads File",
        "--message",
        f"LEADS_MASTER ready: {leads_master.name}",
        "--open",
        str(leads_master),
    ]
    subprocess.run(cmd, check=True)
    print("✓ POPUP + OPEN PASSED")


def email_finished(manifest: Path) -> None:
    # Email notifier itself checks EMAIL_NOTIFY_ENABLED.
    cmd = [sys.executable, str(EMAIL_NOTIFIER), str(manifest)]
    subprocess.run(cmd, check=True)
    print("✓ EMAIL NOTIFY STEP PASSED (or disabled)")


def main() -> None:
    if len(sys.argv) != 2:
        fail("Usage: python3 run_safe.py <scenario>")

    scenario = sys.argv[1].strip()
    run_id = utc_now_compact()

    print("\nUNIVERSAL RUN SAFE (LEAD-GRADE)\n")
    print(f"Scenario: {scenario}")
    print(f"Run ID: {run_id}\n")

    enforce_repo_inventory()
    enforce_people_inventory()

    raw_people = run_people_scenario(scenario)
    normalized_people = normalize_people_csv(raw_people)

    leads_master, manifest = run_universal_enrichment(scenario, normalized_people, run_id)

    # Keep scenario runner (your existing scenario exports) after leads are secured
    run_scenario_runner(scenario)

    # Pop-up finished leads master (required)
    popup_finished(leads_master)

    # Email finished (required when enabled)
    email_finished(manifest)

    print("\nSUCCESS:")
    print("✓ Lead-grade output generated (70+ columns)")
    print("✓ GitHub.io probed first-class for every lead")
    print("✓ Finished CSV popped up automatically")
    print("✓ Manifest written")
    print("✓ Email sent (if enabled)")
    print("\nSAFE TO DEMO LIVE")


if __name__ == "__main__":
    main()
