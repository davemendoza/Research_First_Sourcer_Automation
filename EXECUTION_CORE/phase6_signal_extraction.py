#========================================================================
# AI TALENT ENGINE – SIGNAL INTELLIGENCE
# Proprietary and Confidential
# © 2025–2026 L. David Mendoza. All Rights Reserved.
#========================================================================
# This file contains proprietary intellectual property and trade secrets of
# L. David Mendoza and is part of the AI Talent Engine – Signal Intelligence system.
#
# Unauthorized access, use, copying, modification, distribution, disclosure,
# reverse engineering, or derivative use, in whole or in part, is strictly
# prohibited without prior written authorization.
#========================================================================
from __future__ import annotations

import csv
import json
import re
from pathlib import Path
from typing import Dict, List


REPO_ROOT = Path(__file__).resolve().parents[1]
CONTRACT_PATH = REPO_ROOT / "CONFIG" / "gold_standard_contract.json"

GITHUB_RE = re.compile(r"github\.com/([^/\\s]+)", re.IGNORECASE)
LINKEDIN_RE = re.compile(r"linkedin\.com/[^\\s]+", re.IGNORECASE)


def _load_columns() -> List[str]:
    contract = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
    columns = contract.get("columns")
    if not isinstance(columns, list):
        raise RuntimeError("Gold Standard contract missing columns.")
    return [str(c) for c in columns]


def _extract_github_username(url: str) -> str:
    match = GITHUB_RE.search(url or "")
    if not match:
        return ""
    return match.group(1)


def _extract_linkedin(url: str) -> str:
    match = LINKEDIN_RE.search(url or "")
    if not match:
        return ""
    return match.group(0)


def process_csv(input_csv: str, output_csv: str) -> str:
    in_path = Path(input_csv)
    out_path = Path(output_csv)
    if not in_path.exists():
        raise RuntimeError(f"Phase 6 input missing: {in_path}")

    columns = _load_columns()
    with in_path.open(newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        rows = list(reader)

    for row in rows:
        seed_url = row.get("seed_url") or row.get("Seed_Source_URL") or ""
        gh_user = _extract_github_username(seed_url)
        if gh_user and not row.get("GitHub_Username"):
            row["GitHub_Username"] = gh_user
            row["GitHub_Profile_URL"] = f"https://github.com/{gh_user}"

        linkedin = _extract_linkedin(seed_url)
        if linkedin and not row.get("LinkedIn_URL"):
            row["LinkedIn_URL"] = linkedin

        if seed_url and not row.get("Primary_Source_URL"):
            row["Primary_Source_URL"] = seed_url

        row.setdefault("Row_Validity_Status", "OK")

    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=columns, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            clean = {col: (row.get(col) or "") for col in columns}
            writer.writerow(clean)

    return str(out_path)
