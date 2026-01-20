"""
GPT Writeback Scaffold (READ-ONLY)

This module generates a structured payload intended for a future GPT writeback step.
It does NOT call any GPT APIs and does NOT write to Excel.

If GPT_WRITEBACK_ENABLED is False, prepare_gpt_writeback_payload returns None.
"""

from __future__ import annotations

from typing import Any, Dict, Optional

from .control_plane import GPT_WRITEBACK_ENABLED
from .analysis_envelope import IntelligenceEnvelope


def prepare_gpt_writeback_payload(env: IntelligenceEnvelope) -> Optional[Dict[str, Any]]:
    if not GPT_WRITEBACK_ENABLED:
        return None

    # This is a deterministic, schema-aligned envelope for a future GPT step.
    return {
        "row_identity": {
            "seed_hub_row_id": env.seed_hub_row_id,
            "seed_hub_type": env.seed_hub_type,
            "seed_hub_value": env.seed_hub_value,
        },
        "metadata": {
            "watchlist_flag": env.metadata.watchlist_flag,
            "monitoring_tier": env.metadata.monitoring_tier,
            "domain_type": env.metadata.domain_type,
            "source_category": env.metadata.source_category,
            "language_code": env.metadata.language_code,
        },
        "phase_next": {
            "cadence_plan": None if not env.cadence_plan else {
                "tier": env.cadence_plan.tier,
                "period_days": env.cadence_plan.period_days,
                "rationale": env.cadence_plan.rationale,
            },
            "watchlist": None if not env.watchlist else {
                "decision": env.watchlist.decision,
                "reason": env.watchlist.reason,
                "signals": env.watchlist.signals,
            },
        },
        "narrative_scaffolds": {
            "strengths": env.strengths,
            "weaknesses": env.weaknesses,
            "notes": env.notes,
            "confidence": env.confidence,
        },
        "writeback_targets": {
            # Wired targets only; do not populate during read-only.
            "Watchlist_Flag": "target_only",
            "Monitoring_Tier": "target_only",
            "Domain_Type": "target_only",
            "Source_Category": "target_only",
            "Language_Code": "target_only",
        },
    }


def writeback(env: IntelligenceEnvelope) -> Optional[Dict[str, Any]]:
    # Alias for integration convenience
    return prepare_gpt_writeback_payload(env)
