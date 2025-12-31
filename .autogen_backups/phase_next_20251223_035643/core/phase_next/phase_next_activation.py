"""
Phase-Next Activation — Cadence Only (Read-Only)

Author: Dave Mendoza
Mode: Monitoring Cadence Validation
Writes: NONE
"""

from dataclasses import dataclass
from typing import List

# 🔒 MASTER SWITCH
PHASE_NEXT_MODE = "cadence_only"  # other modes intentionally disabled

# 🔒 Explicitly disabled subsystems
WATCHLIST_RULES_ENABLED = False
GPT_WRITEBACK_ENABLED = False
EXCEL_WRITE_ENABLED = False


@dataclass
class PhaseNextMetadata:
    watchlist_flag: str | None
    monitoring_tier: str | None
    domain_type: str | None
    source_category: str | None
    language_code: str | None


def plan_from_tier(tier: str | None) -> str:
    if tier is None:
        return "no-monitoring"
    tier = tier.lower()
    return {
        "high": "daily",
        "medium": "weekly",
        "low": "monthly",
    }.get(tier, "adhoc")


def compute_domain_profile(domain: str | None, source: str | None) -> dict:
    return {
        "domain": domain or "unknown",
        "source_category": source or "unknown",
        "weighting": "semantic-only",
    }


def validate_metadata_read(rows: List[dict]):
    if not rows:
        print("⚠️ No rows supplied")
        return

    r0 = rows[0]

    meta = PhaseNextMetadata(
        watchlist_flag=r0.get("Watchlist_Flag"),
        monitoring_tier=r0.get("Monitoring_Tier"),
        domain_type=r0.get("Domain_Type"),
        source_category=r0.get("Source_Category"),
        language_code=r0.get("Language_Code"),
    )

    print("✅ Metadata read:", meta)
    print("✅ Cadence plan:", plan_from_tier(meta.monitoring_tier))
    print("✅ Domain profile:", compute_domain_profile(meta.domain_type, meta.source_category))
    print("✅ No writes performed.")


if __name__ == "__main__":
    print("🧭 Phase-Next running in READ-ONLY cadence mode")
    print("🔒 Watchlist enabled:", WATCHLIST_RULES_ENABLED)
    print("🔒 GPT writeback enabled:", GPT_WRITEBACK_ENABLED)
    print("🔒 Excel writes enabled:", EXCEL_WRITE_ENABLED)
