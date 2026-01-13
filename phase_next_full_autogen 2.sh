#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$REPO_ROOT"

echo "🔹 Repo Root: $REPO_ROOT"
command -v python3 >/dev/null 2>&1 || { echo "❌ python3 not found"; exit 1; }

mkdir -p core/phase_next

# ---------------------------------------------------------
# Control Plane (single source of truth)
# ---------------------------------------------------------
cat <<'PY' > core/phase_next/control_plane.py
READ_ONLY_MODE = True

EXCEL_WRITE_ENABLED = False
WATCHLIST_RULES_ENABLED = False
GPT_WRITEBACK_ENABLED = False

def status():
    return {
        "read_only": READ_ONLY_MODE,
        "excel_write_enabled": EXCEL_WRITE_ENABLED,
        "watchlist_rules_enabled": WATCHLIST_RULES_ENABLED,
        "gpt_writeback_enabled": GPT_WRITEBACK_ENABLED,
    }
PY

# ---------------------------------------------------------
# Adaptive Monitoring Cadence
# ---------------------------------------------------------
cat <<'PY' > core/phase_next/adaptive_cadence.py
from datetime import timedelta

TIER_TO_CADENCE = {
    "T0": timedelta(days=90),
    "T1": timedelta(days=30),
    "T2": timedelta(days=14),
    "T3": timedelta(days=7),
}

def plan_from_tier(tier):
    return TIER_TO_CADENCE.get(tier or "T0", TIER_TO_CADENCE["T0"])
PY

# ---------------------------------------------------------
# Watchlist Promotion Rules (Dormant)
# ---------------------------------------------------------
cat <<'PY' > core/phase_next/watchlist_rules.py
from .control_plane import WATCHLIST_RULES_ENABLED

def evaluate_watchlist(row):
    if not WATCHLIST_RULES_ENABLED:
        return row.get("Watchlist_Flag")
    # Placeholder logic (future)
    return "PROMOTE"
PY

# ---------------------------------------------------------
# GPT Writeback Scaffold (Dormant)
# ---------------------------------------------------------
cat <<'PY' > core/phase_next/gpt_writeback.py
from .control_plane import GPT_WRITEBACK_ENABLED

def writeback(row, analysis):
    if not GPT_WRITEBACK_ENABLED:
        return None
    return {
        "Strengths": analysis.get("strengths"),
        "Weaknesses": analysis.get("weaknesses"),
        "Notes": analysis.get("notes"),
    }
PY

# ---------------------------------------------------------
# Phase-Next Activation Runner (Read-Only)
# ---------------------------------------------------------
cat <<'PY' > core/phase_next/phase_next_activation.py
from .control_plane import status
from .adaptive_cadence import plan_from_tier

def main():
    flags = status()
    print("🧭 Phase-Next Control Plane:", flags)

    sample_tier = "T1"
    cadence = plan_from_tier(sample_tier)
    print("⏱️ Cadence example for T1:", cadence)

    print("✅ Phase-Next running in READ-ONLY mode. No writes performed.")

if __name__ == "__main__":
    main()
PY

chmod +x core/phase_next/*.py

# ---------------------------------------------------------
# Runner Script
# ---------------------------------------------------------
cat <<'BASH2' > phase_next_run.sh
#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
python3 -c "from core.phase_next.phase_next_activation import main; main()"
BASH2

chmod +x phase_next_run.sh

echo "✅ AUTOGEN COMPLETE"
echo "NEXT:"
echo "  ./phase_next_run.sh"
