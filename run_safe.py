#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
run_safe.py

UNIVERSAL SAFE ENTRYPOINT — LEAD-GRADE

This is the ONLY approved way to generate finished leads.
If LEADS_MASTER is not produced, the run FAILS.
"""

from pathlib import Path
import sys
import subprocess
import time
import pandas as pd

REPO_ROOT = Path(__file__).resolve().parent
OUTPUTS = REPO_ROOT / "outputs"
PEOPLE_DIR = OUTPUTS / "people"
LEADS_DIR = OUTPUTS / "leads"
SCRIPTS = REPO_ROOT / "scripts"

def fail(msg):
    print("\nHARD FAILURE:")
    print(msg)
    sys.exit(3)

def main():
    if len(sys.argv) != 2:
        fail("Usage: python3 run_safe.py <scenario>")

    scenario = sys.argv[1]
    run_id = time.strftime("%Y%m%d_%H%M%S")

    print("\nUNIVERSAL RUN SAFE — LEAD GRADE\n")
    print(f"Scenario: {scenario}")
    print(f"Run ID: {run_id}\n")

    # --------------------------------------------------
    # 1. PEOPLE SCENARIO
    # --------------------------------------------------
    subprocess.run(
        [sys.executable, "people_scenario_resolver.py", "--scenario", scenario],
        check=True,
    )

    people_csv = max(
        PEOPLE_DIR.glob(f"{scenario}_people_*.csv"),
        key=lambda p: p.stat().st_mtime,
    )

    df = pd.read_csv(people_csv)
    if not (25 <= len(df) <= 50):
        fail("Demo bounds violated")

    # --------------------------------------------------
    # 2. NORMALIZATION
    # --------------------------------------------------
    normalized_csv = people_csv.with_suffix(".normalized.csv")
    subprocess.run(
        [
            sys.executable,
            str(SCRIPTS / "normalize_people_csv.py"),
            str(people_csv),
            str(normalized_csv),
        ],
        check=True,
    )

    if not normalized_csv.exists():
        fail("Normalization did not produce output")

    # --------------------------------------------------
    # 3. UNIVERSAL ENRICHMENT (MANDATORY)
    # --------------------------------------------------
    leads_run_dir = LEADS_DIR / f"run_{run_id}"
    leads_run_dir.mkdir(parents=True, exist_ok=True)

    subprocess.run(
        [
            sys.executable,
            str(SCRIPTS / "universal_enrichment_pipeline.py"),
            scenario,
            str(normalized_csv),
            str(leads_run_dir),
            run_id,
        ],
        check=True,
    )

    leads_master = leads_run_dir / f"LEADS_MASTER_{scenario}_{run_id}.csv"
    if not leads_master.exists():
        fail(f"LEADS_MASTER not created: {leads_master}")

    # --------------------------------------------------
    # 4. POPUP + EMAIL
    # --------------------------------------------------
    subprocess.run(["open", str(leads_master)], check=False)
    subprocess.run(
        [sys.executable, str(SCRIPTS / "send_run_completion_email.py"), str(leads_master)],
        check=False,
    )

    print("\nSUCCESS:")
    print(f"✓ LEADS MASTER CREATED: {leads_master}")
    print("✓ Safe for demo")
    print("✓ World-class run complete")

if __name__ == "__main__":
    main()
