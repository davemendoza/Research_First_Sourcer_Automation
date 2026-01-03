#!/usr/bin/env bash
set -euo pipefail

# ============================================
# AI Talent Engine — Universal Demo Runner
# ============================================
# - Runs any demo scenario (role-agnostic)
# - Enforces all existing gates
# - Automatically opens final results for live demos
# ============================================

if [[ $# -ne 1 ]]; then
  echo "Usage: demo <scenario>"
  exit 1
fi

SCENARIO="$1"

echo
echo "============================================"
echo "RUNNING DEMO SCENARIO: $SCENARIO"
echo "============================================"
echo

# ---- Run the demo pipeline ----
python3 run_demo.py "$SCENARIO"

echo
echo "============================================"
echo "DEMO COMPLETE — LOCATING FINAL ARTIFACT"
echo "============================================"
echo

# ---- Locate most recent FINAL CSV ----
LATEST_FINAL_CSV=$(ls -t outputs/demo/*FINAL*.csv 2>/dev/null | head -n 1 || true)

if [[ -z "$LATEST_FINAL_CSV" ]]; then
  echo "ERROR: No FINAL demo CSV found."
  exit 1
fi

echo "Opening final demo CSV:"
echo "  $LATEST_FINAL_CSV"
open "$LATEST_FINAL_CSV"

# ---- Locate most recent HTML table (optional) ----
LATEST_HTML=$(ls -t outputs/demo/*TABLE*.html 2>/dev/null | head -n 1 || true)

if [[ -n "$LATEST_HTML" ]]; then
  echo "Opening demo HTML table:"
  echo "  $LATEST_HTML"
  open "$LATEST_HTML"
fi

echo
echo "============================================"
echo "DEMO READY FOR PRESENTATION"
echo "============================================"
echo
