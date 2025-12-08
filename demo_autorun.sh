#!/usr/bin/env bash
# ======================================================================
# 🚀 AI TALENT ENGINE — DEMO AUTORUN (v4.0 FINAL)
# Research-First Sourcer Automation | End-to-End Talent Intelligence Demo
# ======================================================================

set -euo pipefail

# === GLOBAL FLAGS ====================================================
DEMO_MODE=true   # set false for quiet test runs

# === BASE PATHS ======================================================
BASE_DIR="$HOME/Desktop/Research_First_Sourcer_Automation"
OUTPUT_DIR="$BASE_DIR/output"

VALIDATOR="$BASE_DIR/validate_jsons.py"
SUMMARY_SCRIPT="$BASE_DIR/generate_summary.py"

AUDIT_LOG="$OUTPUT_DIR/_auto_clean_audit.txt"
DEMO_LOG="$OUTPUT_DIR/demo_audit.txt"

# Canonical candidate list (single source of truth)
CANDIDATES=(
  "Shubham_Saboo.json"
  "Patrick_von_Platen.json"
  "Ashudeep_Singh.json"
)

# === TERMINAL CAPABILITY GUARD ======================================
if [[ -t 1 ]] && command -v tput >/dev/null 2>&1; then
  BOLD=$(tput bold)
  RESET=$(tput sgr0)
  BLUE=$(tput setaf 6)
  GREEN=$(tput setaf 2)
  YELLOW=$(tput setaf 3)
  RED=$(tput setaf 1)
else
  BOLD=""; RESET=""; BLUE=""; GREEN=""; YELLOW=""; RED=""
fi

say_if_demo() {
  [[ "$DEMO_MODE" == true ]] && echo -e "$1"
}

# === PREFLIGHT CHECKS ===============================================
fail() {
  echo "${RED}❌ $1${RESET}"
  exit "$2"
}

[[ -d "$BASE_DIR" ]]        || fail "Base directory not found: $BASE_DIR" 3
[[ -d "$OUTPUT_DIR" ]]      || mkdir -p "$OUTPUT_DIR"
command -v python3 >/dev/null 2>&1 || fail "python3 not available on PATH" 3
[[ -f "$VALIDATOR" ]]       || fail "Missing validator: validate_jsons.py" 3
[[ -f "$SUMMARY_SCRIPT" ]]  || fail "Missing summary generator" 3

# === TIMER ===========================================================
START_TIME=$(date +%s)

clear
say_if_demo ""
say_if_demo "${BOLD}${BLUE}🚀 AI Talent Engine · Demo Autorun${RESET}"
say_if_demo "=============================================================="
say_if_demo "📅 Run timestamp   : $(date -u)"
say_if_demo "📂 Output directory: $OUTPUT_DIR"
say_if_demo ""

# === STEP 1 — VALIDATION =============================================
say_if_demo "${YELLOW}🧩 Validating JSON candidate dossiers...${RESET}"

if python3 "$VALIDATOR"; then
  say_if_demo "${GREEN}✅ Validation completed successfully.${RESET}"
else
  fail "Validation failed. Review audit logs." 1
fi

say_if_demo ""

# === STEP 2 — RUN LOGGING ============================================
{
  echo "------------------------------------------------------------"
  echo "Demo Run Timestamp: $(date -u)"
  echo "Validated Candidate Files:"
  for c in "${CANDIDATES[@]}"; do
    [[ -f "$OUTPUT_DIR/$c" ]] && echo "  - $c"
  done
  echo ""
} >> "$DEMO_LOG"

[[ -f "$AUDIT_LOG" ]] && cat "$AUDIT_LOG" >> "$DEMO_LOG"
echo "" >> "$DEMO_LOG"

# === STEP 3 — SUMMARY GENERATION =====================================
say_if_demo "${YELLOW}🧠 Generating Hiring Intelligence Summary...${RESET}"

if python3 "$SUMMARY_SCRIPT"; then
  say_if_demo "${GREEN}✅ Hiring summary generated.${RESET}"
else
  fail "Summary generation failed." 2
fi

say_if_demo ""

# === STEP 4 — OPEN FILES (DETERMINISTIC ORDER) ========================
say_if_demo "${YELLOW}🧾 Opening reports for live review...${RESET}"

open -a "TextEdit" "$OUTPUT_DIR/Hiring_Intelligence_Summary_Report.md" >/dev/null 2>&1 || true
sleep 0.3

open -a "TextEdit" "$DEMO_LOG" >/dev/null 2>&1 || true
open -a "TextEdit" "$AUDIT_LOG" >/dev/null 2>&1 || true

for c in "${CANDIDATES[@]}"; do
  open -a "TextEdit" "$OUTPUT_DIR/$c" >/dev/null 2>&1 || true
done

say_if_demo ""

# === STEP 5 — FINAL METRICS ==========================================
END_TIME=$(date +%s)
ELAPSED=$((END_TIME - START_TIME))

JSON_COUNT=$(ls "$OUTPUT_DIR"/*.json 2>/dev/null | wc -l | tr -d ' ')
VALID_COUNT=$(grep -c '"valid": true' "$AUDIT_LOG" 2>/dev/null || echo 0)

# ====================================================================
# ✨ FINAL DEMO SUMMARY
# ====================================================================

echo "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${RESET}"
echo "${BOLD}${BLUE}✨ AI Talent Engine · Demo Summary${RESET}"
echo "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${RESET}"

echo "${BOLD}📊 Dossier Validation${RESET}"
echo "   🧾 JSON dossiers detected : $JSON_COUNT"
echo "   ✅ Valid dossiers         : ${GREEN}$VALID_COUNT${RESET}"

echo ""
echo "${BOLD}📘 Generated Artifacts${RESET}"
echo "   • Hiring_Intelligence_Summary_Report.md"
echo "   • demo_audit.txt"
echo "   • _auto_clean_audit.txt"

echo ""
echo "${BOLD}⏱  Execution Metrics${RESET}"
echo "   • Total runtime           : ${ELAPSED}s"
echo "   • Output directory        : $OUTPUT_DIR"

echo "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${RESET}"
echo "${GREEN}${BOLD}🏁 Demo complete. All candidate reports and logs are open.${RESET}"
echo ""

exit 0
