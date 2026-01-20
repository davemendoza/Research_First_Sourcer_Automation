#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EXECUTION_CORE/people_discovery_from_hubs.py
============================================================
PEOPLE DISCOVERY FROM HUBS (CANONICAL, OBSERVABLE)

Maintainer: L. David Mendoza © 2026
Version: v1.0.0

Purpose
- Convert hub-level anchors into person-level discovery rows.
- This stage ONLY discovers identities (usernames / profile URLs).
- No enrichment, no scraping of contact info.
- Emits visible progress so long runs are never silent.

Input
- _01_anchors.csv

Output
- _01a_people_discovered.csv

Hard guarantees
- Deterministic
- Observable progress
- Fail-closed if zero people discovered

Adapters supported
- GitHubOrgPeopleAdapter
- GitHubOrgReposAdapter
- HuggingFaceOrgAdapter

Changelog
- 2026-01-20: Canonical rebuild after catastrophic local deletion

Validation
python3 -m py_compile EXECUTION_CORE/people_discovery_from_hubs.py
"""

from __future__ import annotations

import csv
import sys
from pathlib import Path
from typing import Dict, List

# Adapters (import only, no execution side effects)
from EXECUTION_CORE.github_org_people_adapter import GitHubOrgPeopleAdapter
from EXECUTION_CORE.github_org_repo_contributors_adapter import GitHubOrgReposAdapter
from EXECUTION_CORE.huggingface_org_adapter import HuggingFaceOrgAdapter


ADAPTERS = {
    "GitHubOrgPeopleAdapter": GitHubOrgPeopleAdapter,
    "GitHubOrgReposAdapter": GitHubOrgReposAdapter,
    "HuggingFaceOrgAdapter": HuggingFaceOrgAdapter,
}


def die(msg: str) -> None:
    print(f"❌ [PEOPLE_DISCOVERY] {msg}", file=sys.stderr)
    raise SystemExit(1)


def process_csv(input_csv: str, output_csv: str) -> None:
    inp = Path(input_csv)
    outp = Path(output_csv)

    if not inp.exists():
        die(f"Input anchors file not found: {inp}")

    rows: List[Dict[str, str]] = []
    with inp.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        anchors = list(reader)

    if not anchors:
        die("Anchors CSV is empty")

    discovered: List[Dict[str, str]] = []
    total = len(anchors)

    print(f"[PEOPLE_DISCOVERY] Anchors loaded: {total}")

    for idx, row in enumerate(anchors, start=1):
        adapter_name = row.get("Python_Adapter", "").strip()
        hub_url = row.get("Seed_Hub_URL", "").strip()

        if not adapter_name:
            continue

        adapter_cls = ADAPTERS.get(adapter_name)
        if not adapter_cls:
            print(f"[PEOPLE_DISCOVERY] ⚠ Unknown adapter: {adapter_name}")
            continue

        print(
            f"[PEOPLE_DISCOVERY] ({idx}/{total}) "
            f"Running {adapter_name} on {hub_url}"
        )

        adapter = adapter_cls()
        try:
            people = adapter.enumerate_people(row)
        except Exception as e:
            print(f"[PEOPLE_DISCOVERY] ❌ Adapter error: {e}")
            continue

        if not people:
            continue

        for p in people:
            out = dict(row)
            out.update(p)
            discovered.append(out)

        print(
            f"[PEOPLE_DISCOVERY] ✓ {len(people)} people discovered "
            f"(running total: {len(discovered)})"
        )

    if not discovered:
        die(
            "NO candidate people discovered from anchors output.\n"
            "This means adapters returned zero identities.\n"
            "Downstream enrichment must not proceed."
        )

    # Write output
    outp.parent.mkdir(parents=True, exist_ok=True)
    with outp.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=sorted(discovered[0].keys()))
        writer.writeheader()
        for r in discovered:
            writer.writerow(r)

    print(
        f"[PEOPLE_DISCOVERY] COMPLETE — "
        f"{len(discovered)} people written to {outp}"
    )


__all__ = ["process_csv"]
