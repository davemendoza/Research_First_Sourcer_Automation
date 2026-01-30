#!/usr/bin/env bash
set -euo pipefail

ROOT="$(pwd)"
EXPECTED_ROOT="/Users/davemendoza/Desktop/Research_First_Sourcer_Automation"

if [[ "$ROOT" != "$EXPECTED_ROOT" ]]; then
  echo "❌ OUTPUTS GUARD FAILED: Not in canonical project root"
  echo "Expected: $EXPECTED_ROOT"
  echo "Actual:   $ROOT"
  exit 1
fi

echo "🔎 Running outputs pre-run guard…"

BAD_PATTERNS=(
  "outputs/people/.+\\.0[1-9].+\\.csv"
  "outputs/demo/.+\\.0[1-9].+\\.csv"
  "outputs/demo/.+stage[0-9_]+.*\\.csv"
  "outputs/scenario/.+/people_stage_.*\\.csv"
  "outputs/scenario/.+_phase[0-6]\\.csv"
)

FOUND_VIOLATION=0

for pattern in "${BAD_PATTERNS[@]}"; do
  MATCHES=$(find -E outputs -type f -regex ".*${pattern}" || true)
  if [[ -n "$MATCHES" ]]; then
    echo "❌ OUTPUTS GUARD VIOLATION:"
    echo "$MATCHES"
    FOUND_VIOLATION=1
  fi
done

if [[ "$FOUND_VIOLATION" -eq 1 ]]; then
  echo ""
  echo "🚫 Execution aborted."
  echo "Reason: Partial / intermediate CSVs detected in active outputs paths."
  echo "Action: Move them to outputs/_ARCHIVE_partial_runs/ before running again."
  exit 1
fi

echo "✅ Outputs guard passed. Environment is clean."
