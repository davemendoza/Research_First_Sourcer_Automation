#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
People CSV Normalizer (Canonical Prefix + Order)
Version: v2.0.0
Author: L. David Mendoza
Date: 2026-01-02
© 2025–2026 L. David Mendoza. All rights reserved.

Purpose:
- Create canonical columns required by the universal pipeline
- Enforce deterministic prefix and ordering
- Preserve all original columns after canonical prefix
- Fail closed if key identity sources are missing

Canonical prefix (MANDATORY ORDER):
  Person_ID, Role_Type, Email, Phone, LinkedIn_URL, GitHub_URL, GitHub_Username

Derivation rules:
- Person_ID  <- GitHub_Username (required, non-empty)
- Role_Type  <- Scenario if present else Source_Scenario if present else input arg fallback (not used here)
- Email      <- existing Email column if present else blank
- Phone      <- existing Phone column if present else blank
- LinkedIn_URL <- existing LinkedIn_URL if present else blank
- GitHub_URL <- required (must exist as column; may be blank in rows but not all blank)
- GitHub_Username <- required

Usage:
  python3 scripts/normalize_people_csv.py <input_csv> <output_csv>
"""

import csv
import sys
from pathlib import Path
from datetime import datetime

CANON_PREFIX = ["Person_ID","Role_Type","Email","Phone","LinkedIn_URL","GitHub_URL","GitHub_Username"]

if len(sys.argv) != 3:
    print("USAGE: normalize_people_csv.py <input_csv> <output_csv>")
    sys.exit(2)

input_csv = Path(sys.argv[1]).resolve()
output_csv = Path(sys.argv[2]).resolve()

if not input_csv.exists():
    print(f"ERROR: Input CSV not found: {input_csv}")
    sys.exit(2)

with input_csv.open(newline="", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    rows = list(reader)
    fieldnames = reader.fieldnames or []

required_source_cols = ["GitHub_Username"]
missing = [c for c in required_source_cols if c not in fieldnames]
if missing:
    print("ERROR: Missing required source columns: " + ", ".join(missing))
    sys.exit(3)

# GitHub_URL strongly required as a column
if "GitHub_URL" not in fieldnames:
    print("ERROR: Missing required source column: GitHub_URL")
    sys.exit(3)

# Ensure optional columns exist (create blanks if missing)
optional_cols = ["Scenario", "Source_Scenario", "Email", "Phone", "LinkedIn_URL"]
for c in optional_cols:
    if c not in fieldnames:
        fieldnames.append(c)
        for r in rows:
            r[c] = ""

# Build output fieldnames: canonical prefix + everything else not in prefix (preserve existing order)
rest = [c for c in fieldnames if c not in CANON_PREFIX]
out_fields = CANON_PREFIX + rest

# Row-level sanity checks
if not rows:
    print("ERROR: Input CSV has no rows")
    sys.exit(4)

# Validate GitHub_URL not entirely empty
all_blank_gh = True
for r in rows:
    if (r.get("GitHub_URL") or "").strip():
        all_blank_gh = False
        break
if all_blank_gh:
    print("ERROR: GitHub_URL column exists but all rows are blank")
    sys.exit(4)

output_csv.parent.mkdir(parents=True, exist_ok=True)

with output_csv.open("w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=out_fields)
    w.writeheader()

    for r in rows:
        gh_user = (r.get("GitHub_Username") or "").strip()
        if not gh_user:
            print("ERROR: Empty GitHub_Username encountered; cannot derive Person_ID")
            sys.exit(5)

        role_type = (r.get("Scenario") or "").strip() or (r.get("Source_Scenario") or "").strip()
        if not role_type:
            # fail closed: Role_Type is required to preserve downstream contracts
            print("ERROR: Missing Scenario/Source_Scenario; cannot derive Role_Type")
            sys.exit(5)

        normalized = dict(r)
        normalized["Person_ID"] = gh_user
        normalized["Role_Type"] = role_type
        normalized["Email"] = (r.get("Email") or "").strip()
        normalized["Phone"] = (r.get("Phone") or "").strip()
        normalized["LinkedIn_URL"] = (r.get("LinkedIn_URL") or "").strip()
        normalized["GitHub_URL"] = (r.get("GitHub_URL") or "").strip()
        normalized["GitHub_Username"] = gh_user

        # Emit in canonical order
        out_row = {k: normalized.get(k, "") for k in out_fields}
        w.writerow(out_row)

print(f"OK: Normalized CSV written: {output_csv}")
print(f"Rows processed: {len(rows)}")
print(f"Timestamp UTC: {datetime.utcnow().isoformat()}")
