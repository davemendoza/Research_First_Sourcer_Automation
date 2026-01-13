#!/usr/bin/env python3
"""
AI Talent Engine – Canonical People CSV Generator
© 2025 L. David Mendoza

RULES:
- Canonical schema comes from data/talent_schema_inventory.csv
- Comma-delimited
- ≥ 90 columns REQUIRED
- Demo generates 25 rows
- Zero inference, zero guessing
"""

import csv
import sys
from pathlib import Path

# ---------------- PATHS ----------------
REPO_ROOT = Path(__file__).resolve().parent
SCHEMA_CSV = REPO_ROOT / "data" / "talent_schema_inventory.csv"
OUTPUT_DIR = REPO_ROOT / "outputs" / "people"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

OUTPUT_CSV = OUTPUT_DIR / "people_frontier_demo.csv"

MIN_COLUMNS = 90
MIN_ROWS = 25

# ---------------- LOAD SCHEMA ----------------
if not SCHEMA_CSV.exists():
    sys.exit(f"❌ Missing schema CSV: {SCHEMA_CSV}")

with SCHEMA_CSV.open(encoding="utf-8", newline="") as f:
    reader = csv.reader(f)
    schema = next(reader)

schema = [c.strip() for c in schema if c.strip()]

if len(schema) < MIN_COLUMNS:
    sys.exit(f"❌ Invalid schema: {len(schema)} columns (expected ≥ {MIN_COLUMNS})")

print(f"✅ Schema loaded: {len(schema)} columns")

# ---------------- GENERATE ROWS ----------------
rows = []
for i in range(MIN_ROWS):
    row = {col: "" for col in schema}
    row["Person_ID"] = f"demo-frontier-{i+1:03d}"
    row["Role_Type"] = "frontier"
    row["Full_Name"] = f"Demo Frontier Candidate {i+1}"
    rows.append(row)

# ---------------- WRITE CSV ----------------
with OUTPUT_CSV.open("w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=schema)
    writer.writeheader()
    writer.writerows(rows)

# ---------------- VALIDATE ----------------
with OUTPUT_CSV.open(encoding="utf-8") as f:
    header = f.readline().strip().split(",")

if header != schema:
    sys.exit("❌ CSV header mismatch — generation aborted")

# ---------------- DONE ----------------
print("✅ CSV GENERATED")
print(f"📄 File: {OUTPUT_CSV}")
print(f"📊 Columns: {len(schema)}")
print(f"👤 Rows: {len(rows)}")
