#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
run_safe.py — Universal Safe Runner (Lead-grade finished outputs)
Version: v3.0.0
Author: L. David Mendoza
Date: 2026-01-02
© 2025–2026 L. David Mendoza. All rights reserved.

Single command produces:
- People CSV (bounded demo rules enforced by resolver contract)
- Normalized people CSV (canonical prefix and order enforced)
- Lead-grade finished CSV (40–70+ columns) in outputs/leads/run_<id>/
- Scenario scoring outputs (existing scenario runner)
- Manifest JSON
- macOS popup + email on completion (hard required unless disabled)

Usage:
  python3 run_safe.py <scenario>

Env (recommended defaults):
  EMAIL_NOTIFY_ENABLED=1
  POPUP_NOTIFY_ENABLED=1
  AUTO_OPEN_LEADS=1
  PIPELINE_NOTIFY_TO=LDaveMendoza@gmail.com
  GITHUB_TOKEN=...  (optional, improves GitHub rate limits)

Hard fail conditions:
- No normalized canonical prefix
- Leads CSV has < 40 columns
- Popup fails (when POPUP_NOTIFY_ENABLED=1)
- Email fails (when EMAIL_NOTIFY_ENABLED=1)
"""

from __future__ import annotations

import json
import os
import sys
import subprocess
from pathlib import Path
from datetime import datetime, timezone

import pandas as pd

REPO_ROOT = Path(__file__).resolve().parent
PEOPLE_DIR = REPO_ROOT / "outputs" / "people"
LEADS_ROOT = REPO_ROOT / "outputs" / "leads"
MANIFEST_DIR = REPO_ROOT / "outputs" / "manifests"

NORMALIZER = REPO_ROOT / "scripts" / "normalize_people_csv.py"
ENRICHER = REPO_ROOT / "scripts" / "universal_enrichment_pipeline.py"
POPUP = REPO_ROOT / "scripts" / "macos_notify.py"
EMAIL = REPO_ROOT / "scripts" / "send_run_completion_email.py"

SCENARIO_RUNNER = REPO_ROOT / "ai_talent_scenario_runner.py"
PEOPLE_RESOLVER = REPO_ROOT / "people_scenario_resolver.py"

CANON_PREFIX = ["Person_ID","Role_Type","Email","Phone","LinkedIn_URL","GitHub_URL","GitHub_Username"]

def fail(msg: str) -> None:
    print("\nHARD FAILURE:")
    print(msg)
    print()
    sys.exit(1)

def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()

def ensure_file(p: Path) -> None:
    if not p.exists():
        fail(f"Missing required file: {p}")

def run_cmd(cmd: list[str], hard: bool = True) -> None:
    r = subprocess.run(cmd)
    if hard and r.returncode != 0:
        fail(f"Command failed ({r.returncode}): " + " ".join(cmd))

def enforce_repo_inventory() -> None:
    required = [
        PEOPLE_RESOLVER,
        SCENARIO_RUNNER,
        NORMALIZER,
        ENRICHER,
        POPUP,
        EMAIL,
    ]
    for p in required:
        ensure_file(p)
    print("✓ REPO INVENTORY GATE PASSED")

def run_people_scenario(scenario: str) -> Path:
    run_cmd([sys.executable, str(PEOPLE_RESOLVER), "--scenario", scenario], hard=True)

    outputs = sorted(
        PEOPLE_DIR.glob(f"{scenario}_people_*.csv"),
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )
    if not outputs:
        fail("People scenario produced no output CSV")
    people_csv = outputs[0]
    df = pd.read_csv(people_csv)

    if not (25 <= len(df) <= 50):
        fail(f"Demo bounds violated: {len(df)} rows (expected 25–50)")

    req = {"GitHub_URL","GitHub_Username"}
    missing = req - set(df.columns)
    if missing:
        fail("Missing required identity columns: " + ", ".join(sorted(missing)))

    if df["GitHub_URL"].isna().all():
        fail("GitHub_URL column exists but contains no data")

    print("✓ PEOPLE SCENARIO GATE PASSED")
    print(f"✓ People CSV: {people_csv}")
    print(f"✓ Rows: {len(df)}")
    return people_csv

def normalize_people(people_csv: Path) -> Path:
    out = Path(str(people_csv).replace(".csv", ".normalized.csv"))
    run_cmd([sys.executable, str(NORMALIZER), str(people_csv), str(out)], hard=True)

    df = pd.read_csv(out)
    if list(df.columns[:len(CANON_PREFIX)]) != CANON_PREFIX:
        fail("Normalization failed canonical prefix/order check")

    print("✓ NORMALIZATION GATE PASSED")
    print(f"✓ Normalized CSV: {out}")
    return out

def run_leads_enrichment(scenario: str, normalized_csv: Path) -> Path:
    run_id = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    out_dir = LEADS_ROOT / f"run_{run_id}"
    out_dir.mkdir(parents=True, exist_ok=True)

    run_cmd([sys.executable, str(ENRICHER), scenario, str(normalized_csv), str(out_dir), run_id], hard=True)

    leads_master = out_dir / f"LEADS_MASTER_{scenario}_{run_id}.csv"
    if not leads_master.exists():
        fail(f"Expected leads file missing: {leads_master}")

    df = pd.read_csv(leads_master)
    if df.empty:
        fail("Leads CSV is empty")
    if len(df.columns) < 40:
        fail(f"Leads CSV not wide enough (<40 columns). Found: {len(df.columns)}")

    print("✓ LEADS ENRICHMENT GATE PASSED")
    print(f"✓ Leads master: {leads_master}")
    print(f"✓ Columns: {len(df.columns)}")
    return leads_master

def run_scenario_scoring(scenario: str) -> None:
    run_cmd([sys.executable, str(SCENARIO_RUNNER), "--scenario", scenario], hard=True)
    print("✓ SCENARIO SCORING COMPLETE")

def write_manifest(scenario: str, people_csv: Path, normalized_csv: Path, leads_csv: Path) -> Path:
    MANIFEST_DIR.mkdir(parents=True, exist_ok=True)
    run_id = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")

    manifest = {
        "run_id": run_id,
        "completed_utc": utc_now_iso(),
        "scenario": scenario,
        "people_csv_raw": str(people_csv),
        "people_csv_normalized": str(normalized_csv),
        "leads_master_csv": str(leads_csv),
        "status": "success",
    }
    path = MANIFEST_DIR / f"run_manifest_{scenario}_{run_id}.json"
    path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(f"✓ MANIFEST WRITTEN: {path}")
    return path

def notify_popup(leads_csv: Path) -> None:
    if os.getenv("POPUP_NOTIFY_ENABLED","1").strip() != "1":
        print("POPUP_NOTIFY: disabled")
        return
    run_cmd([sys.executable, str(POPUP), "Pipeline Complete", f"Finished leads file ready: {leads_csv.name}"], hard=True)

def notify_email(manifest: Path) -> None:
    if os.getenv("EMAIL_NOTIFY_ENABLED","1").strip() != "1":
        print("EMAIL_NOTIFY: disabled")
        return
    run_cmd([sys.executable, str(EMAIL), str(manifest)], hard=True)

def maybe_open(leads_csv: Path) -> None:
    if os.getenv("AUTO_OPEN_LEADS","1").strip() != "1":
        return
    subprocess.run(["open", str(leads_csv)], check=False)

def main() -> None:
    if len(sys.argv) != 2:
        fail("Usage: python3 run_safe.py <scenario>")

    scenario = sys.argv[1].strip()

    print("============================================================")
    print("UNIVERSAL RUN SAFE (LEAD-GRADE)")
    print("============================================================")
    print(f"Scenario: {scenario}")
    print()

    enforce_repo_inventory()

    people_csv = run_people_scenario(scenario)
    normalized_csv = normalize_people(people_csv)

    leads_csv = run_leads_enrichment(scenario, normalized_csv)
    run_scenario_scoring(scenario)

    manifest = write_manifest(scenario, people_csv, normalized_csv, leads_csv)

    # Completion signals (hard required unless disabled)
    notify_popup(leads_csv)
    notify_email(manifest)
    maybe_open(leads_csv)

    print()
    print("SUCCESS — FINISHED LEADS OUTPUT WRITTEN")
    print(f"Leads: {leads_csv}")
    print(f"Manifest: {manifest}")
    print("============================================================")

if __name__ == "__main__":
    main()
