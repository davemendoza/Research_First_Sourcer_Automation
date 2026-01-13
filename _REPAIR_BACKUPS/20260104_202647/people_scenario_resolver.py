#!/usr/bin/env python3
"""
AI Talent Engine — People Scenario Resolver
© 2025 L. David Mendoza

Contract-safe resolver.
Matches run_safe.py EXACTLY.
"""

from typing import Dict
import pandas as pd

from people_source_github import build_people


def _set_if_exists(row: dict, key: str, value):
    if value:
        row[key] = value


def _first_or_none(values):
    if not values:
        return None
    if isinstance(values, list):
        return values[0]
    return values


def _apply_identity(row: dict, scenario: str, idx: int, u, c):
    row["Person_ID"] = f"{scenario}_{idx:04d}"

    login = getattr(u, "login", None)

    _set_if_exists(row, "Full_Name", login)
    _set_if_exists(row, "GitHub_Username", login)
    _set_if_exists(row, "GitHub_URL", f"https://github.com/{login}" if login else None)
    _set_if_exists(row, "GitHub_IO_URL", f"https://{login}.github.io" if login else None)

    _set_if_exists(row, "Primary_Email", _first_or_none(getattr(c, "emails", None)))
    _set_if_exists(row, "Primary_Phone", _first_or_none(getattr(c, "phones", None)))
    _set_if_exists(row, "Resume_URL", _first_or_none(getattr(c, "resume_urls", None)))

    return row


def generate_people_for_scenario(
    scenario: str,
    mode: str,
    min_rows: int,
    max_rows: int
) -> pd.DataFrame:

    demo_mode = mode == "demo"

    users, crawls = build_people(
        scenario=scenario,
        queries=[],
        min_n=min_rows,
        max_n=max_rows,
        demo_mode=demo_mode
    )

    rows = []
    for i, u in enumerate(users):
        c = crawls.get(u.login)
        row = {}
        row = _apply_identity(row, scenario, i, u, c)
        rows.append(row)

    return pd.DataFrame(rows)


def run_people(
    scenario: str,
    mode: str,
    min_rows: int,
    max_rows: int,
    outdir: str = None
) -> pd.DataFrame:
    """
    outdir accepted for contract compatibility with run_safe.py
    """
    return generate_people_for_scenario(
        scenario=scenario,
        mode=mode,
        min_rows=min_rows,
        max_rows=max_rows
    )
