#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EXECUTION_CORE/organization_discovery_from_hubs.py
============================================================
ORGANIZATION DISCOVERY FROM HUBS (CANONICAL)

Purpose
- Discover organizations from hub anchors
- Emit one row per organization
- No people discovery
- No contact enrichment

Input
- _01_anchors.csv

Output
- _01a_organizations_discovered.csv
"""

from __future__ import annotations

import csv
import sys
from pathlib import Path
from typing import Dict


ORG_HUB_TYPES = {
    "GitHub Org People",
    "GitHub Org Repos",
    "Hugging Face Org",
    "Models / Hugging Face",
    "Research Lab",
}


def die(msg: str) -> None:
    print(f"❌ [ORG_DISCOVERY] {msg}", file=sys.stderr)
    raise SystemExit(1)


def process_csv(input_csv: str, output_csv: str) -> None:
    inp = Path(input_csv)
    outp = Path(output_csv)

    if not inp.exists():
        die(f"Input anchors file not found: {inp}")

    with inp.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        anchors = list(reader)

    if not anchors:
        die("Anchors CSV is empty")

    orgs: Dict[str, Dict[str, str]] = {}

    for row in anchors:
        hub_type = row.get("Seed_Hub_Type", "").strip()
        org_name = row.get("Organization", "").strip()

        if hub_type not in ORG_HUB_TYPES:
            continue
        if not org_name:
            continue
        if org_name in orgs:
            continue

        orgs[org_name] = {
            "Organization": org_name,
            "Seed_Hub_Type": hub_type,
            "Seed_Hub_URL": row.get("Seed_Hub_URL", ""),
            "Category": row.get("Category", ""),
            "Tier": row.get("Tier", ""),
            "Source": row.get("Source", ""),
        }

        print(f"[ORG_DISCOVERY] ✓ {org_name}")

    if not orgs:
        die("No organizations discovered from anchors")

    outp.parent.mkdir(parents=True, exist_ok=True)
    with outp.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=sorted(next(iter(orgs.values())).keys())
        )
        writer.writeheader()
        for r in orgs.values():
            writer.writerow(r)

    print(
        f"[ORG_DISCOVERY] COMPLETE — "
        f"{len(orgs)} organizations written to {outp}"
    )


__all__ = ["process_csv"]
