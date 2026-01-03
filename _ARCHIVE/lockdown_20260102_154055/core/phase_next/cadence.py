from __future__ import annotations

from dataclasses import dataclass
from datetime import timedelta
from typing import Dict

from .constants import DomainProfile

@dataclass(frozen=True)
class CadencePlan:
    tier: str
    interval: timedelta
    sample_cap: int
    notes: str

def plan_from_tier(tier: str) -> CadencePlan:
    """
    Adaptive cadence baseline (read-only):
    T0: daily (highest urgency)
    T1: 3 days
    T2: weekly
    T3: biweekly
    T4: monthly (lowest urgency)
    """
    t = (tier or "T3").upper().strip()

    if t == "T0":
        return CadencePlan(tier=t, interval=timedelta(days=1), sample_cap=250, notes="Highest urgency sampling")
    if t == "T1":
        return CadencePlan(tier=t, interval=timedelta(days=3), sample_cap=200, notes="High urgency sampling")
    if t == "T2":
        return CadencePlan(tier=t, interval=timedelta(days=7), sample_cap=150, notes="Weekly sampling")
    if t == "T4":
        return CadencePlan(tier=t, interval=timedelta(days=30), sample_cap=50, notes="Monthly sampling")
    # Default T3
    return CadencePlan(tier="T3", interval=timedelta(days=14), sample_cap=100, notes="Biweekly sampling (default)")

def compute_domain_profile(domain_type: str, source_category: str) -> DomainProfile:
    """
    Domain weighting (read-only):
    - semantic_weight influences which analyzers are emphasized downstream
    - provenance_confidence influences escalation thresholds downstream
    """
    d = (domain_type or "").strip().lower()
    s = (source_category or "").strip().lower()

    semantic_weight = 1.0
    provenance_confidence = 0.8
    notes = []

    # Domain type heuristics (safe defaults)
    if any(k in d for k in ["research", "paper", "scholar", "arxiv", "publication"]):
        semantic_weight = 1.25
        notes.append("Research-heavy domain")
    elif any(k in d for k in ["repo", "github", "open source", "oss", "code"]):
        semantic_weight = 1.15
        notes.append("Code-heavy domain")
    elif any(k in d for k in ["news", "press", "blog", "social"]):
        semantic_weight = 0.95
        notes.append("High-noise domain")
    elif d:
        notes.append("General domain")

    # Source category heuristics (provenance)
    if any(k in s for k in ["official", "primary", "maintainer", "org"]):
        provenance_confidence = 0.95
        notes.append("High provenance source")
    elif any(k in s for k in ["aggregator", "scrape", "mirror"]):
        provenance_confidence = 0.70
        notes.append("Lower provenance source")
    elif s:
        notes.append("Unknown provenance bucket")

    return DomainProfile(
        domain_type=domain_type or "",
        source_category=source_category or "",
        semantic_weight=semantic_weight,
        provenance_confidence=provenance_confidence,
        notes="; ".join(notes) if notes else "Default profile",
    )
