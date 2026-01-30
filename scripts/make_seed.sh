#!/usr/bin/env bash
set -euo pipefail

# ============================================================
# RESEARCH FIRST SOURCER AUTOMATION
# © 2026 L. David Mendoza. All Rights Reserved.
# ============================================================

if [[ "$(pwd)" != "/Users/davemendoza/Desktop/Research_First_Sourcer_Automation" ]]; then
  echo "ERROR: Must run from canonical repo root."
  echo "Expected: /Users/davemendoza/Desktop/Research_First_Sourcer_Automation"
  echo "Actual:   $(pwd)"
  exit 1
fi

ROLE="${1:-}"
INPUT="${2:-}"

if [[ -z "${ROLE}" || -z "${INPUT}" ]]; then
  echo "Usage:"
  echo "  ./scripts/make_seed.sh <role_slug|alias> <input_csv_path>"
  exit 2
fi

python3 EXECUTION_CORE/phase4_seed_builder.py --role "${ROLE}" --input "${INPUT}"
