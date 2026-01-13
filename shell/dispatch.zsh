# ============================================================
# RFS Dispatch (LOCKED) — plain English -> scenario slug
# ============================================================

_rfs_normalize() {
  echo "$*" | tr '[:upper:]' '[:lower:]' | sed -E 's/[^a-z0-9]+/ /g' | xargs
}

_rfs_dispatch() {
  local mode="$1"
  shift
  local raw="$(_rfs_normalize "$@")"
  local scenario=""
  local role=""

  case "$raw" in
    frontier*|frontier\ ai*|ai\ scientist*|frontier\ scientist*)
      scenario="frontier_ai_scientist"; role="Frontier AI Scientist" ;;
    machine\ learning*|ml\ engineer*|machine\ learning\ engineer*)
      scenario="ml_engineer"; role="Machine Learning Engineer" ;;
    rlhf*|reinforcement*|rl\ engineer*)
      scenario="rlhf_engineer"; role="RLHF Engineer" ;;
    infra*|infrastructure*|ai\ infra*)
      scenario="ai_infra"; role="AI Infrastructure Engineer" ;;
    *)
      echo "❌ Unknown role: $raw"
      echo "Available: frontier | machine learning engineer | rlhf engineer | ai infra engineer"
      return 1 ;;
  esac

  cd "$_RFS_ROOT" || return 1
  local mode_lc="scenario"
  [[ "$mode" == "Demo" ]] && mode_lc="demo"

  # Run pipeline via ONE canonical runner
  python3 run_safe.py "$scenario" "$mode_lc" || return 1

  # Preview is fault-tolerant and never blocks
  python3 talent_intel_preview.py "outputs/${scenario}_CANONICAL.csv" "$mode_lc" "$role" || true

  # Auto-open CSV for interview flow
  command -v open >/dev/null 2>&1 && open "outputs/${scenario}_CANONICAL.csv" >/dev/null 2>&1 || true
}
