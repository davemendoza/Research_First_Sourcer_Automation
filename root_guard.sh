#!/usr/bin/env bash
set -euo pipefail

EXPECTED="$HOME/Desktop/Research_First_Sourcer_Automation"
CURRENT="$(pwd)"

if [[ "$CURRENT" != "$EXPECTED" ]]; then
  echo ""
  echo "❌ FATAL: WRONG WORKING DIRECTORY"
  echo "Expected: $EXPECTED"
  echo "Actual:   $CURRENT"
  echo "Aborting to prevent corruption."
  echo ""
  exit 1
fi
