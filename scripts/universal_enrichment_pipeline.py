#!/usr/bin/env python3
"""
UNIVERSAL ENRICHMENT PIPELINE — AUTHORITATIVE

This script MUST write:
LEADS_MASTER_<scenario>_<run_id>.csv

If it does not, the run is invalid.
"""

import sys
import pandas as pd
from pathlib import Path
from datetime import datetime

if len(sys.argv) != 5:
    print("USAGE: universal_enrichment_pipeline.py <scenario> <normalized_people_csv> <leads_out_dir> <run_id>")
    sys.exit(2)

scenario = sys.argv[1]
people_csv = Path(sys.argv[2])
leads_out_dir = Path(sys.argv[3])
run_id = sys.argv[4]

leads_out_dir.mkdir(parents=True, exist_ok=True)

if not people_csv.exists():
    print(f"ERROR: normalized people CSV missing: {people_csv}")
    sys.exit(3)

df = pd.read_csv(people_csv)

# ------------------------------------------------------------
# WORLD-CLASS ENRICHMENT (baseline, extensible)
# ------------------------------------------------------------

df["Run_ID"] = run_id
df["Scenario"] = scenario
df["Enriched_At_UTC"] = datetime.utcnow().isoformat()

# Contact normalization (realistic baseline)
df["Primary_Email"] = df.get("Email", "")
df["Primary_Phone"] = df.get("Phone", "")
df["Has_Email"] = df["Primary_Email"].astype(bool)
df["Has_Phone"] = df["Primary_Phone"].astype(bool)

# Identity spine reinforcement
df["Identity_Strength"] = (
    df["GitHub_Username"].astype(bool).astype(int) +
    df["GitHub_URL"].astype(bool).astype(int) +
    df["LinkedIn_URL"].astype(bool).astype(int)
)

# Scoring placeholder (real math comes next phase)
df["Lead_Grade"] = df["Identity_Strength"].map({3: "A", 2: "B", 1: "C"}).fillna("D")

# ------------------------------------------------------------
# WRITE AUTHORITATIVE LEADS FILE
# ------------------------------------------------------------

leads_master = leads_out_dir / f"LEADS_MASTER_{scenario}_{run_id}.csv"
df.to_csv(leads_master, index=False)

print(f"LEADS MASTER WRITTEN: {leads_master}")
print(f"Columns: {len(df.columns)}")
print(f"Rows: {len(df)}")
