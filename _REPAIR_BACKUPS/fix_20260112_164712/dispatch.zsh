# ============================================================
# Research First Sourcer Automation — Canonical Dispatch Layer
# Child-proof role resolution + post-run Talent Intelligence preview
# ============================================================

_rfs_normalize() {
  echo "$*" \
    | tr '[:upper:]' '[:lower:]' \
    | sed -E 's/[^a-z0-9]+/ /g' \
    | xargs
}

_rfs_map_role() {
  # input: raw normalized role text
  # output: "scenario|Display Role"
  local raw="$1"
  local scenario=""
  local display=""

  case "$raw" in
    frontier*|frontier\ ai*|ai\ scientist*|frontier\ scientist*)
      scenario="frontier_ai_scientist"
      display="Frontier AI Scientist"
      ;;
    machine\ learning*|ml\ engineer*|machine\ learning\ engineer*)
      scenario="ml_engineer"
      display="Machine Learning Engineer"
      ;;
    rlhf*|reinforcement*|rl\ engineer*)
      scenario="rlhf_engineer"
      display="RLHF Engineer"
      ;;
    infra*|infrastructure*|ai\ infra*)
      scenario="ai_infra"
      display="AI Infrastructure Engineer"
      ;;
    *)
      scenario=""
      display=""
      ;;
  esac

  if [[ -z "$scenario" ]]; then
    echo ""
    return 1
  fi

  echo "${scenario}|${display}"
}

_rfs_dispatch() {
  local mode="$1"
  shift

  local raw="$(_rfs_normalize "$@")"
  if [[ -z "$raw" ]]; then
    echo "❌ Missing role. Examples:"
    echo "  demo frontier"
    echo "  scenario machine learning engineer"
    return 1
  fi

  local mapped
  mapped="$(_rfs_map_role "$raw")" || {
    echo "❌ Unknown role: $raw"
    echo "Available roles:"
    echo "  frontier"
    echo "  machine learning engineer"
    echo "  rlhf engineer"
    echo "  ai infra engineer"
    return 1
  }

  local scenario="${mapped%%|*}"
  local display_role="${mapped#*|}"

  cd "$_RFS_ROOT" || return 1

  # Normalize mode for preview
  local mode_lc="scenario"
  [[ "$mode" == "Demo" ]] && mode_lc="demo"

  # Run core pipeline (CSV writer is inside run_safe.py)
  # Suppress ONLY the known broken preview spam from run_safe.py (we will run preview correctly after)
  set -o pipefail
  python3 EXECUTION_CORE/run_safe.py "$scenario" 2>&1 \
    | sed -E '/^► Talent Intelligence Preview$/d;/^Usage: python3 EXECUTION_CORE\/talent_intel_preview\.py/d;/^\* FAILED: Talent Intelligence Preview$/d' \
    || return 1

  # Canonical CSV path convention observed in your output:
  # outputs/<scenario>_CANONICAL.csv
  local csv_path="$_RFS_ROOT/outputs/${scenario}_CANONICAL.csv"
  if [[ ! -f "$csv_path" ]]; then
    echo "❌ Expected CSV not found: $csv_path"
    echo "Check outputs/ directory for the generated file."
    return 1
  fi

  # Run Talent Intelligence Preview correctly (never blocks the CSV)
  python3 EXECUTION_CORE/talent_intel_preview.py "$csv_path" "$mode_lc" "$display_role" || true

  # Auto-open CSV for interview flow (non-blocking)
  if command -v open >/dev/null 2>&1; then
    open "$csv_path" >/dev/null 2>&1 || true
  fi

  return 0
}
