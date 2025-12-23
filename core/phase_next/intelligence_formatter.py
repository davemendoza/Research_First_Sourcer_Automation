"""
Intelligence Formatter (READ-ONLY)

Builds a deterministic IntelligenceEnvelope from:
- Seed hub row fields
- Cadence plan (Phase C)
- Watchlist decision (Phase D)
- GPT writeback payload generation scaffold (Phase E)

No GPT calls. No Excel writes.
"""

from __future__ import annotations

from typing import Any, Dict, Optional

from .analysis_envelope import IntelligenceEnvelope, SeedHubMetadata
from .adaptive_cadence import plan_from_tier
from .watchlist_rules import evaluate_watchlist
from .gpt_writeback import prepare_gpt_writeback_payload


def _safe_str(v: Any) -> Optional[str]:
    if v is None:
        return None
    s = str(v).strip()
    return s if s else None


def build_envelope(row: Dict[str, Any]) -> IntelligenceEnvelope:
    meta = SeedHubMetadata(
        watchlist_flag=_safe_str(row.get("Watchlist_Flag")),
        monitoring_tier=_safe_str(row.get("Monitoring_Tier")),
        domain_type=_safe_str(row.get("Domain_Type")),
        source_category=_safe_str(row.get("Source_Category")),
        language_code=_safe_str(row.get("Language_Code")),
    )

    env = IntelligenceEnvelope(
        seed_hub_row_id=_safe_str(row.get("Seed_Hub_Row_ID") or row.get("Row_ID") or row.get("Person ID")),
        seed_hub_type=_safe_str(row.get("Seed_Hub_Type")),
        seed_hub_value=_safe_str(row.get("Seed_Hub_Value") or row.get("Value") or row.get("URL")),
        metadata=meta,
    )

    env.cadence_plan = plan_from_tier(meta.monitoring_tier)
    env.watchlist = evaluate_watchlist(row)

    # Phase E scaffolds: deterministic, conservative
    env.strengths = [
        "Read-only scaffolds active: cadence planning and watchlist evaluation are operational.",
        "Seed Hub metadata fields are wired as targets (not populated) for future monitoring.",
    ]

    env.weaknesses = [
        "No live evidence ingestion in this phase (by design).",
        "No GPT writeback enabled; payload generation only.",
    ]

    env.notes = [
        "This run is read-only. No writes performed.",
        "To enable writes later, set PHASE_NEXT_READ_ONLY=0 and PHASE_NEXT_EXCEL_WRITE_ENABLED=1 explicitly.",
        "GPT writeback remains disabled unless PHASE_NEXT_GPT_WRITEBACK_ENABLED=1 is explicitly set.",
    ]

    env.confidence = "Medium"

    # Generate payload (but do not send anywhere)
    env.gpt_payload = prepare_gpt_writeback_payload(env)

    return env
