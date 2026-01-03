#!/usr/bin/env bash
set -euo pipefail

# GPT-Slim Dry-Run (Universal, Design-Only)
# Version: v1.0.4-gptslim-dryrun-universal
# Owner: L. David Mendoza
# Date: 2026-01-02
#
# FINAL DESIGN VERSION
# - NO model calls
# - NO People Pipeline mutation
# - Design-only planning artifacts
# - Explicit, conservative alias resolution only

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OUT_DIR="${ROOT_DIR}/outputs/gpt_slim"
SCENARIO="${1:-frontier}"

mkdir -p "${OUT_DIR}"

LATEST_CSV="$(ls -t "${ROOT_DIR}/outputs/people/${SCENARIO}_people_"*.csv 2>/dev/null | head -n 1 || true)"

if [[ -z "${LATEST_CSV}" ]]; then
  echo "ERROR: No scenario CSV found for scenario '${SCENARIO}'."
  exit 2
fi

RUN_ID="$(basename "${LATEST_CSV}" .csv | sed "s/^${SCENARIO}_people_//")"
PLAN_JSON="${OUT_DIR}/${SCENARIO}_gpt_slim_plan_${RUN_ID}.json"
EVAL_CSV="${OUT_DIR}/${SCENARIO}_gpt_slim_eval_${RUN_ID}.csv"

export LATEST_CSV
export PLAN_JSON
export EVAL_CSV
export SCENARIO
export RUN_ID

python3 - <<'PY'
import csv
import json
import os
from datetime import datetime, timezone

latest_csv = os.environ["LATEST_CSV"]
plan_json = os.environ["PLAN_JSON"]
eval_csv = os.environ["EVAL_CSV"]
scenario = os.environ["SCENARIO"]
run_id = os.environ["RUN_ID"]

# Canonical requirements with EXPLICIT, LOW-RISK aliases (READ-ONLY)
REQUIRED_COLUMNS = {
    "Person_ID": [
        "Person_ID",
        "person_id",
        "PersonID",
        "personId",
        "ID",
    ],
    "Role_Type": [
        "Role_Type",
        "Role",
        "Primary_Role",
        "Primary_Role_Type",
        "Role_Family",
    ],
    "Public_Email": [
        "Public_Email",
        "Email",
        "Work_Email",
        "Primary_Email",
    ],
    "Public_Phone": [
        "Public_Phone",
        "Phone",
        "Phone_Number",
        "Mobile_Phone",
        "Mobile",
        "Cell_Phone",
        "Cell",
    ],
}

with open(latest_csv, newline="", encoding="utf-8") as f:
    header = next(csv.reader(f))

present = set(header)

resolved = {}
missing = []

for canonical, aliases in REQUIRED_COLUMNS.items():
    found = next((a for a in aliases if a in present), None)
    if found:
        resolved[canonical] = found
    else:
        missing.append(canonical)

plan = {
    "version": "v1.0.4-gptslim-dryrun-universal",
    "status": "design_only_no_model_calls",
    "scenario": scenario,
    "run_id": run_id,
    "input_csv": latest_csv,
    "timestamp_utc": datetime.now(timezone.utc).isoformat(),
    "required_columns": REQUIRED_COLUMNS,
    "resolved_column_map": resolved,
    "missing_required_canonical_columns": missing,
    "notes": [
        "Alias resolution is explicit and read-only.",
        "No columns are renamed or modified.",
        "No fuzzy matching is permitted.",
        "Wiring is blocked if any canonical requirement is unmet."
    ],
}

os.makedirs(os.path.dirname(plan_json), exist_ok=True)
with open(plan_json, "w", encoding="utf-8") as f:
    json.dump(plan, f, indent=2, sort_keys=True)

eval_header = [
    "Person_ID",
    "GPT_Slim_Input_Eligible",
    "GPT_Slim_Reason_Excluded",
    "GPT_Slim_Evaluation_Status",
    "GPT_Slim_Confidence_Score",
    "GPT_Slim_Rationale",
    "GPT_Slim_Risk_Flags",
    "GPT_Slim_Model_Version",
    "GPT_Slim_Timestamp",
]

with open(eval_csv, "w", newline="", encoding="utf-8") as f:
    csv.writer(f).writerow(eval_header)

print("OK: Dry-run plan written:", plan_json)
print("OK: Eval CSV template written:", eval_csv)

if missing:
    print("WARN: Missing required canonical columns:", ", ".join(missing))
    raise SystemExit(3)
else:
    print("OK: All required canonical columns resolved via explicit aliases")
PY
