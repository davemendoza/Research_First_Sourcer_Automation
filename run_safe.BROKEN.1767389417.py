#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
run_safe.py

AI Talent Engine — MASTER SAFE EXECUTION ENTRYPOINT
© 2025 L. David Mendoza

Hard guarantees:
- Canonical People schema enforced (75–80+ columns)
- Column order locked
- No silent column loss or merge
- Demo-safe, fail-closed behavior
"""

from __future__ import annotations

import sys
import subprocess
from pathlib import Path
from datetime import datetime, timezone
import pandas as pd

# =============================================================================
# REPO PATHS
# =============================================================================

REPO_ROOT = Path(__file__).resolve().parent
PEOPLE_DIR = REPO_ROOT / "outputs" / "people"

SCENARIO_RUNNER = REPO_ROOT / "ai_talent_scenario_runner.py"
NORMALIZER = REPO_ROOT / "scripts" / "normalize_people_csv.py"
ENRICHER = REPO_ROOT / "scripts" / "universal_enrichment_pipeline.py"
NOTIFIER = REPO_ROOT / "scripts" / "macos_notify.py"
EMAIL_NOTIFIER = REPO_ROOT / "scripts" / "send_run_completion_email.py"

# =============================================================================
# CANONICAL SCHEMA CONTRACT
# =============================================================================

from contracts.canonical_people_schema import (
    enforce_canonical,
    CANONICAL_COLUMNS,
    canonical_min_columns,
)

# =============================================================================
# HELPERS
# =============================================================================

def utc_now_compact() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")


def fail(msg: str) -> None:
    print("\nHARD FAILURE")
    print(msg)
    sys.exit(1)

# =============================================================================
# CANONICAL SCHEMA ENFORCEMENT (WRITER OF RECORD)
# =============================================================================

def enforce_schema_on_output(leads_master_path: Path) -> pd.DataFrame:
    df = pd.read_csv(leads_master_path)

    if len(df.columns) < canonical_min_columns():
        raise RuntimeError(
            f"Schema regression: {len(df.columns)} < canonical minimum {canonical_min_columns()}"
        )

    df = enforce_canonical(df)

    expected = CANONICAL_COLUMNS
    actual = list(df.columns[: len(expected)])
    if actual != expected:
        raise RuntimeError("Canonical column order drift detected in people_master.csv")

    df.to_csv(leads_master_path, index=False)
    return df

# =============================================================================
# GATES
# =============================================================================

def enforce_repo_inventory() -> None:
    required = [
        "run_safe.py",
        "people_scenario_resolver.py",
        "ai_talent_scenario_runner.py",
        "contracts/canonical_people_schema.py",
        "scripts/universal_enrichment_pipeline.py",
    ]
    missing = [r for r in required if not (REPO_ROOT / r).exists()]
    if missing:
        fail("Missing required repo files:\n" + "\n".join(missing))
    print("✓ Repo inventory validated")


def enforce_people_inventory() -> Path:
    people_master = PEOPLE_DIR / "people_master.csv"
    if not people_master.exists():
        fail(f"People inventory missing: {people_master}")

    df = pd.read_csv(people_master)
    if df.empty:
        fail("People inventory exists but is empty")

    print(f"✓ People inventory OK ({len(df)} rows)")
    return people_master

# =============================================================================
# PIPELINE STEPS
# =============================================================================

def run_people_scenario(scenario: str) -> Path:
    cmd = [sys.executable, "people_scenario_resolver.py", "--scenario", scenario]
    subprocess.run(cmd, check=True)

    outputs = sorted(
        PEOPLE_DIR.glob(f"{scenario}_people_*.csv"),
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )
    if not outputs:
        fail("People scenario produced no output")

    df = pd.read_csv(outputs[0])
    if not (25 <= len(df) <= 50):
        fail(f"Demo bounds violated: {len(df)} rows (expected 25–50)")

    return outputs[0]


def normalize_people_csv(raw_csv: Path) -> Path:
    out = raw_csv.with_suffix(".normalized.csv")
    subprocess.run(
        [sys.executable, NORMALIZER, raw_csv, out],
        check=True,
    )
    return out


def run_universal_enrichment(scenario: str, normalized_csv: Path, run_id: str) -> Path:
    subprocess.run(
        [sys.executable, ENRICHER, scenario, normalized_csv, run_id],
        check=True,
    )

    leads_dir = REPO_ROOT / "outputs" / "leads" / f"run_{run_id}"
    leads_master = leads_dir / f"people_master.csv_{scenario}_{run_id}.csv"

    if not leads_master.exists():
        fail("people_master.csv not produced")

    return leads_master

# =============================================================================
# UI / NOTIFICATION
# =============================================================================

def popup_finished(csv_path: Path) -> None:
    subprocess.run(
        [
            sys.executable,
            NOTIFIER,
            "--title",
            "AI Talent Engine — Leads Ready",
            "--message",
            csv_path.name,
            "--open",
            csv_path,
        ],
        check=True,
    )


def email_finished(manifest_path: Path) -> None:
    subprocess.run([sys.executable, EMAIL_NOTIFIER, manifest_path], check=True)

# =============================================================================
# MAIN
# =============================================================================

def main() -> None:
    if len(sys.argv) != 2:
        fail("Usage: python3 run_safe.py <scenario>")

    scenario = sys.argv[1].strip()
    run_id = utc_now_compact()

    print("\nAI TALENT ENGINE — SAFE RUN")
    print(f"Scenario: {scenario}")
    print(f"Run ID: {run_id}\n")

    enforce_repo_inventory()
    enforce_people_inventory()

    raw_people = run_people_scenario(scenario)
    promote_people_master_to_leads(scenario, run_id)
    normalized_people = normalize_people_csv(raw_people)

    leads_master = run_universal_enrichment(scenario, normalized_people, run_id)

    # 🔒 CANONICAL SCHEMA ENFORCEMENT (MANDATORY)
    enforce_schema_on_output(leads_master)
    print("✓ Canonical schema enforced (order + count)")

    subprocess.run([sys.executable, SCENARIO_RUNNER, "--scenario", scenario], check=True)

    popup_finished(leads_master)

    print("\nSUCCESS")
    print("✓ Demo-ready CSV")
    print("✓ Canonical schema locked")
    print("✓ Safe to show live")

# =============================================================================

if __name__ == "__main__":
    main()

# ============================================================
# CANONICAL LEADS MASTER PROMOTION (HARD CONTRACT)
# ============================================================

def promote_people_master_to_leads(scenario: str, run_id: str):
    from pathlib import Path
    import shutil

    people_master = Path("outputs/people/people_master.csv")
    if not people_master.exists():
        raise RuntimeError("people_master.csv exists check failed")

    leads_path = Path("outputs/people") / f"LEADS_MASTER_{scenario}_{run_id}.csv"
    shutil.copy(people_master, leads_path)

    print(f"✅ LEADS_MASTER written → {leads_path}")
    return leads_path
