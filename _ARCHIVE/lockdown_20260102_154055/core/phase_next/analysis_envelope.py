"""
Analysis Envelope

A stable, import-safe container for Phase-Next output artifacts.
This does NOT call any network services and does NOT write to Excel.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class SeedHubMetadata:
    watchlist_flag: Optional[str] = None
    monitoring_tier: Optional[str] = None
    domain_type: Optional[str] = None
    source_category: Optional[str] = None
    language_code: Optional[str] = None


@dataclass
class CadencePlan:
    tier: str
    period_days: int
    rationale: str


@dataclass
class WatchlistDecision:
    decision: str
    reason: str
    signals: List[str] = field(default_factory=list)


@dataclass
class IntelligenceEnvelope:
    # Identity / provenance
    seed_hub_row_id: Optional[str] = None
    seed_hub_type: Optional[str] = None
    seed_hub_value: Optional[str] = None
    metadata: SeedHubMetadata = field(default_factory=SeedHubMetadata)

    # C/D outputs
    cadence_plan: Optional[CadencePlan] = None
    watchlist: Optional[WatchlistDecision] = None

    # E outputs (read-only scaffolds)
    strengths: List[str] = field(default_factory=list)
    weaknesses: List[str] = field(default_factory=list)
    notes: List[str] = field(default_factory=list)
    confidence: str = "Unknown"

    # GPT writeback payload (generated only; never posted)
    gpt_payload: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "seed_hub_row_id": self.seed_hub_row_id,
            "seed_hub_type": self.seed_hub_type,
            "seed_hub_value": self.seed_hub_value,
            "metadata": {
                "watchlist_flag": self.metadata.watchlist_flag,
                "monitoring_tier": self.metadata.monitoring_tier,
                "domain_type": self.metadata.domain_type,
                "source_category": self.metadata.source_category,
                "language_code": self.metadata.language_code,
            },
            "cadence_plan": None if not self.cadence_plan else {
                "tier": self.cadence_plan.tier,
                "period_days": self.cadence_plan.period_days,
                "rationale": self.cadence_plan.rationale,
            },
            "watchlist": None if not self.watchlist else {
                "decision": self.watchlist.decision,
                "reason": self.watchlist.reason,
                "signals": list(self.watchlist.signals),
            },
            "strengths": list(self.strengths),
            "weaknesses": list(self.weaknesses),
            "notes": list(self.notes),
            "confidence": self.confidence,
            "gpt_payload": self.gpt_payload,
        }
