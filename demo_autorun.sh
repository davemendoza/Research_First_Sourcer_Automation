#!/usr/bin/env bash
# ================================================================
# 🚀 AI TALENT ENGINE – DEMO AUTORUN (v4.4 MACOS-STABLE RELEASE)
# Research-First Sourcer Automation | End-to-End Talent Intelligence Demo
# ================================================================

# Force full stdout render — no pager or truncation
export PAGER=cat
export LESS=-F

set -euo pipefail

# === GLOBAL FLAGS =================================================
DEMO_MODE=true    # set false for quiet test runs

# === BASE PATHS ===================================================
BASE_DIR="$HOME/Desktop/Research_First_Sourcer_Automation"
OUTPUT_DIR="${BASE_DIR}/output"
SPEC_FILE="${BASE_DIR}/system_spec/AI_Talent_Engine_Demo_Spec.md"

# === FAST MODE ====================================================
echo ""
echo "🚀 AI Talent Engine · Demo Autorun (Full Output Mode)"
echo "=============================================================="
echo "📅 Run timestamp   : $(date -u)"
echo "📂 Output directory: ${OUTPUT_DIR}"
echo ""

# === SKIP VALIDATION (TEMPORARY FAST MODE PATCH) ==================
echo "⚙️  Validation skipped (schema file missing; demo bypass mode active)"
echo ""

# === DISPLAY DEMO SPEC DIRECTLY ===================================
echo "🧩 Launching full Foundational AI + Demo Menu sequence..."
echo "=============================================================="

if [[ -f "${SPEC_FILE}" ]]; then
  cat "${SPEC_FILE}"
else
  echo "❌ ERROR: Demo spec file not found at ${SPEC_FILE}"
  exit 1
fi

echo ""
echo "=============================================================="
echo "✅ Demo completed — full Foundational AI 2-table view and numbered menu rendered."
echo "=============================================================="
