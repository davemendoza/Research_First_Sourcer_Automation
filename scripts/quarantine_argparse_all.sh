#!/usr/bin/env bash
set -euo pipefail
# Research_First_Sourcer_Automation
# scripts/quarantine_argparse_all.sh
# Version: v1.0.0 (2026-01-23)
# Copyright (c) 2025-2026 L. David Mendoza. All rights reserved.
#
# Purpose:
#   One-command quarantine of any import-time execution inside EXECUTION_CORE,
#   including argparse poisoning. Writes .bak backups and a JSON report.
#
# Validation:
#   chmod +x scripts/quarantine_argparse_all.sh
#   bash scripts/quarantine_argparse_all.sh
#
# Git:
#   git add tools/argparse_quarantine_autofix.py scripts/quarantine_argparse_all.sh
#   git commit -m "Guardrail: quarantine argparse/import-time execution across EXECUTION_CORE"
#   git push

ROOT="$(cd "$(dirname "$0")/.." && pwd)"

python3 -m py_compile "$ROOT/tools/argparse_quarantine_autofix.py"

REPORT="$ROOT/INVENTORY_AUDIT/argparse_quarantine_report.json"
mkdir -p "$(dirname "$REPORT")"

python3 "$ROOT/tools/argparse_quarantine_autofix.py" \
  --root "$ROOT/EXECUTION_CORE" \
  --inplace \
  --report "$REPORT" \
  --fail-on-error

echo "✅ quarantine complete"
echo "report: $REPORT"
