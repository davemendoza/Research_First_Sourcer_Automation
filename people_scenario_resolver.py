#!/usr/bin/env python3
"""
AI Talent Engine — People Scenario Resolver (Real People, Schema-First)
© 2025 L. David Mendoza
Version: v1.0.0-real-people

Guarantees:
- Real GitHub identities only; no placeholder people
- Always emits ALL 82 canonical columns in correct order
- GitHub.io emphasized for public email/phone/resume link extraction
"""

from __future__ import annotations

import json
import os
import uuid
from typing import Dict, List, Tuple

import pandas as pd

from tools.schema_loader import canonical_column_names
from people_source_github import build_people, GitHubUser, CrawlSignals

CANON_COLS = canonical_column_names()
REGISTRY_PATH = "scenario_registry.json"

def _new_run_id() -> str:
    return uuid.uuid4().hex[:12]

def _load_registry() -> Dict[str, Dict]:
    if not os.path.exists(REGISTRY_PATH):
        raise RuntimeError(f"Missing scenario registry: {REGISTRY_PATH}")
    with open(REGISTRY_PATH, "r", encoding="utf-8") as f:
        d = json.load(f)
    return d.get("scenarios", {})

def _set_if_exists(row: Dict[str, str], col: str, val: str) -> None:
    if col in row and val is not None:
        row[col] = str(val).strip()

def _apply_identity(row: Dict[str, str], scenario: str, idx: int, u: GitHubUser, c: CrawlSignals) -> Dict[str, str]:
    # Fill only if the 82 schema has the column.
    _set_if_exists(row, "Person_ID", f"{scenario}_{idx:04d}")
    _set_if_exists(row, "Role_Type", scenario)

    # Common identity columns (best-effort; only fill if present)
    _set_if_exists(row, "Full_Name", u.name or u.login)
    _set_if_exists(row, "GitHub_Username", u.login)
    _set_if_exists(row, "GitHub_URL", u.html_url)

    # Public contact signals (GitHub profile email if public, then github.io/blog crawl)
    email = u.email or c.public_email
    phone = c.public_phone
    resume = c.resume_link
    ghio = c.github_io_url

    _set_if_exists(row, "Email", email)
    _set_if_exists(row, "Phone", phone)
    _set_if_exists(row, "Resume_Link", resume)
    _set_if_exists(row, "GitHub_IO_URL", ghio)

    _set_if_exists(row, "Current_Company", u.company)
    _set_if_exists(row, "Location", u.location)
    _set_if_exists(row, "Website", u.blog)
    _set_if_exists(row, "Bio", u.bio)

    return row

def generate_people_for_scenario(scenario: str, mode: str, min_rows: int, max_rows: int) -> pd.DataFrame:
    scenarios = _load_registry()
    if scenario not in scenarios:
        raise RuntimeError(f"Unknown scenario '{scenario}'. Add it to scenario_registry.json")
    queries = scenarios[scenario].get("queries") or []
    if not queries:
        raise RuntimeError(f"Scenario '{scenario}' has no queries in scenario_registry.json")

    if mode == "demo":
        min_n = max(25, min_rows)
        max_n = min(50, max_rows)
    else:
        min_n = max(25, min_rows)
        max_n = max_rows

    users, crawls = build_people(scenario=scenario, queries=queries, min_n=min_n, max_n=max_n)

    rows: List[Dict[str, str]] = []
    for i, u in enumerate(users, start=1):
        row = {c: "" for c in CANON_COLS}
        c = crawls.get(u.login) or CrawlSignals()
        row = _apply_identity(row, scenario, i, u, c)
        rows.append(row)

    df = pd.DataFrame(rows, columns=CANON_COLS)

    if list(df.columns) != CANON_COLS:
        raise RuntimeError("Schema violation: people dataframe columns differ from canonical 82 spine.")
    if len(df) < min_n:
        raise RuntimeError(f"Demo/scenario bounds violated: got {len(df)}, required at least {min_n}")
    if mode == "demo" and len(df) > 50:
        raise RuntimeError(f"Demo max violated: got {len(df)}, max 50")

    return df

def write_people_master(df: pd.DataFrame, out_path: str) -> None:
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    df.to_csv(out_path, index=False)

def run_people(scenario: str, mode: str, outdir: str, min_rows: int, max_rows: int) -> str:
    df = generate_people_for_scenario(scenario=scenario, mode=mode, min_rows=min_rows, max_rows=max_rows)
    out_path = os.path.join(outdir, "people_master.csv")
    write_people_master(df, out_path)
    return out_path
