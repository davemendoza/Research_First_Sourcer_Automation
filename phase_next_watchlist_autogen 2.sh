#!/usr/bin/env bash
set -euo pipefail

echo "🔒 Phase-Next Watchlist Autogen (READ-ONLY)"

# -----------------------------------------------------------------------------
# Control Plane – force safe defaults
# -----------------------------------------------------------------------------
cat <<'PY' > core/phase_next/control_plane.py
READ_ONLY = True
EXCEL_WRITE_ENABLED = False
GPT_WRITEBACK_ENABLED = False
WATCHLIST_RULES_ENABLED = True
PY

# -----------------------------------------------------------------------------
# Watchlist Rules (read-only evaluation)
# -----------------------------------------------------------------------------
cat <<'PY' > core/phase_next/watchlist_rules.py
from .control_plane import WATCHLIST_RULES_ENABLED

def evaluate_watchlist(row: dict) -> dict:
    """
    READ-ONLY watchlist evaluation.
    Returns decision + rationale. No writes.
    """
    if not WATCHLIST_RULES_ENABLED:
        return {
            "decision": row.get("Watchlist_Flag"),
            "reason": "Watchlist rules disabled"
        }

    tier = (row.get("Monitoring_Tier") or "").upper()
    domain = (row.get("Domain_Type") or "").lower()
    source = (row.get("Source_Category") or "").lower()

    promote_signals = 0

    if tier in {"T0", "T1"}:
        promote_signals += 1
    if domain in {"frontier", "foundational", "infra"}:
        promote_signals += 1
    if source in {"github", "arxiv", "openalex", "conference"}:
        promote_signals += 1

    if promote_signals >= 2:
        return {
            "decision": "PROMOTE",
            "reason": f"{promote_signals} escalation signals detected"
        }

    return {
        "decision": "HOLD",
        "reason": f"Only {promote_signals} escalation signals detected"
    }

# Compatibility alias (future-proof imports)
evaluate_watchlist_candidate = evaluate_watchlist
PY

# -----------------------------------------------------------------------------
# Activation Runner (READ-ONLY)
# -----------------------------------------------------------------------------
cat <<'PY' > core/phase_next/phase_next_activation.py
from .control_plane import (
    READ_ONLY,
    EXCEL_WRITE_ENABLED,
    GPT_WRITEBACK_ENABLED,
    WATCHLIST_RULES_ENABLED,
)
from .adaptive_cadence import plan_from_tier
from .watchlist_rules import evaluate_watchlist_candidate

def main():
    print("🧭 Phase-Next Control Plane:", {
        "read_only": READ_ONLY,
        "excel_write_enabled": EXCEL_WRITE_ENABLED,
        "watchlist_rules_enabled": WATCHLIST_RULES_ENABLED,
        "gpt_writeback_enabled": GPT_WRITEBACK_ENABLED,
    })

    # Sample row (no Excel IO)
    sample = {
        "Monitoring_Tier": "T1",
        "Domain_Type": "Frontier",
        "Source_Category": "GitHub",
        "Watchlist_Flag": None,
    }

    cadence = plan_from_tier(sample["Monitoring_Tier"])
    watch = evaluate_watchlist_candidate(sample)

    print("⏱ Cadence example:", cadence)
    print("👁 Watchlist evaluation:", watch)
    print("✅ READ-ONLY execution complete. No writes performed.")

if __name__ == "__main__":
    main()
PY

# -----------------------------------------------------------------------------
# Runner Script (shell-safe)
# -----------------------------------------------------------------------------
cat <<'BASH2' > phase_next_run.sh
#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$REPO_ROOT"

command -v python3 >/dev/null 2>&1 || { echo "❌ python3 not found"; exit 1; }

python3 -c "from core.phase_next.phase_next_activation import main; main()"
BASH2

chmod +x phase_next_run.sh phase_next_watchlist_autogen.sh

echo "✅ AUTOGEN COMPLETE"
echo "NEXT:"
echo "  ./phase_next_run.sh"
