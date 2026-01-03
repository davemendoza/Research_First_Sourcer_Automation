#!/usr/bin/env python3
"""
AI Talent Engine — Universal Demo Generator (All AI Role Types)
© 2025 L. David Mendoza

Version: v1.0.0 (2026-01-01)
Changelog:
- v1.0.0: Universal, scenario-agnostic generator:
  * Finds latest outputs/people/<scenario>_people_*.csv
  * Writes outputs/demo/OPENAI_DEMO_FINAL.csv (canonical ordering, contact after Role_Type)
  * Runs deep_artifact_harvester.py to enrich URLs + contact + research + Hugging Face
  * Generates outputs/demo/OPENAI_DEMO_GPT_SLIM.csv (token-safe subset)
  * Opens final CSV automatically

Non-negotiables:
- No placeholders
- No fabrication
- Public-only harvesting
"""

from __future__ import annotations

import argparse
import csv
import glob
import os
import subprocess
from pathlib import Path
from typing import Dict, List

REPO_ROOT = Path(".")
OUT_DEMO_DIR = Path("outputs/demo")
OUT_DEMO_FINAL = OUT_DEMO_DIR / "OPENAI_DEMO_FINAL.csv"
OUT_GPT_SLIM = OUT_DEMO_DIR / "OPENAI_DEMO_GPT_SLIM.csv"

# Canonical front columns: Role_Type then contact immediately after (as you demanded)
FRONT_COLUMNS = [
    "Person_ID",
    "Full_Name",
    "Role_Type",
    "Public_Email_Found",
    "Public_Phone_Found",
    "LinkedIn_URL",
    "GitHub_URL",
    "GitHub_Username",
    "GitHub_IO_URL",
    "HuggingFace_Profile_URLs",
    "HuggingFace_Model_URLs",
    "arXiv_URLs",
    "OpenReview_URLs",
    "Semantic_Scholar_URLs",
    "Google_Scholar_Profile_URLs",
    "Patent_URLs",
    "Conference_Presentation_URLs",
    "Resume_URLs",
    "Portfolio_URLs",
    "X_Twitter_URLs",
]

# Additional harvester columns we always preserve
HARVESTER_COLUMNS = [
    "Additional_Public_Emails",
    "Additional_Public_Phones",
    "LinkedIn_Public_URLs",
    "All_Public_URLs_Found",
    "Contact_Provenance_URLs",
    "Research_Provenance_URLs",
    "Harvest_Provenance",
    "HuggingFace_Space_URLs",
    "HuggingFace_Org_URLs",
]

def find_latest_people_csv(scenario: str) -> Path:
    pats = [
        f"outputs/people/{scenario}_people_*.csv",
        f"outputs/people/{scenario}*_people_*.csv",
        f"outputs/people/*{scenario}*people_*.csv",
    ]
    candidates: List[str] = []
    for p in pats:
        candidates.extend(glob.glob(p))
    candidates = sorted(set(candidates))
    if not candidates:
        raise FileNotFoundError(f"No people CSV found for scenario '{scenario}' under outputs/people/")
    candidates.sort(key=lambda x: os.path.getmtime(x), reverse=True)
    return Path(candidates[0])

def read_csv(p: Path) -> List[Dict[str, str]]:
    with p.open("r", encoding="utf-8", newline="") as f:
        r = csv.DictReader(f)
        return list(r)

def write_csv(p: Path, rows: List[Dict[str, str]], fieldnames: List[str]) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for row in rows:
            w.writerow({k: row.get(k, "") for k in fieldnames})

def ensure_cols(rows: List[Dict[str, str]], cols: List[str]) -> None:
    for row in rows:
        for c in cols:
            if c not in row:
                row[c] = ""

def canonicalize_headers(rows: List[Dict[str, str]]) -> List[str]:
    # Union of all headers
    all_cols = set()
    for r in rows:
        all_cols.update(r.keys())

    # Make sure these exist
    ensure_cols(rows, FRONT_COLUMNS + HARVESTER_COLUMNS)

    # Prefer front columns, then harvester, then the rest stable-sorted
    rest = sorted([c for c in all_cols if c not in set(FRONT_COLUMNS + HARVESTER_COLUMNS)])
    return FRONT_COLUMNS + HARVESTER_COLUMNS + rest

def build_gpt_slim(rows: List[Dict[str, str]]) -> None:
    slim_cols = [
        "Person_ID",
        "Full_Name",
        "Role_Type",
        "Public_Email_Found",
        "Public_Phone_Found",
        "LinkedIn_URL",
        "GitHub_URL",
        "GitHub_IO_URL",
        "HuggingFace_Profile_URLs",
        "HuggingFace_Model_URLs",
        "arXiv_URLs",
        "OpenReview_URLs",
        "Semantic_Scholar_URLs",
        "Google_Scholar_Profile_URLs",
        "Patent_URLs",
        "Conference_Presentation_URLs",
        "Resume_URLs",
        "Portfolio_URLs",
    ]
    OUT_DEMO_DIR.mkdir(parents=True, exist_ok=True)
    write_csv(OUT_GPT_SLIM, rows, slim_cols)

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--scenario", required=True, help="Role scenario (frontier, ai_infra, mlops, inference, devrel, applied_ml, etc.)")
    ap.add_argument("--open", action="store_true", help="Auto-open the final CSV")
    ap.add_argument("--max-depth", type=int, default=2, help="Harvester crawl depth")
    ap.add_argument("--max-pages", type=int, default=18, help="Harvester max pages/person")
    args = ap.parse_args()

    src = find_latest_people_csv(args.scenario.strip().lower())
    rows = read_csv(src)
    if not rows:
        raise RuntimeError(f"Source CSV is empty: {src}")

    # Canonicalize and write initial demo artifact
    header = canonicalize_headers(rows)
    write_csv(OUT_DEMO_FINAL, rows, header)

    # Run harvester on demo artifact (this is the contract execution)
    cmd = [
        "python3",
        "deep_artifact_harvester.py",
        "--input",
        str(OUT_DEMO_FINAL),
        "--max-depth",
        str(args.max_depth),
        "--max-pages",
        str(args.max_pages),
    ]
    if args.open:
        cmd.append("--open")

    subprocess.run(cmd, check=True)

    # Re-read enriched output and generate GPT slim
    enriched = read_csv(OUT_DEMO_FINAL)
    build_gpt_slim(enriched)

    if args.open:
        try:
            os.system(f'open "{OUT_GPT_SLIM}" >/dev/null 2>&1')
        except Exception:
            pass

    print(f"SUCCESS: {OUT_DEMO_FINAL}")
    print(f"SUCCESS: {OUT_GPT_SLIM}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
