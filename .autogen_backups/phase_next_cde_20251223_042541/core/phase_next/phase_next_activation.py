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
