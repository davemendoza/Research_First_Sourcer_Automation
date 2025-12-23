"""
Adaptive Cadence (READ-ONLY)

Maps Monitoring_Tier values to sampling cadence plans.
No scheduling side effects; this only returns a plan object.
"""

from __future__ import annotations

from dataclasses import dataclass

from .analysis_envelope import CadencePlan


def _normalize_tier(tier: str | None) -> str:
    if not tier:
        return "T3"
    t = str(tier).strip().upper()
    if t in {"T0", "T1", "T2", "T3", "T4"}:
        return t
    # Common variants
    if t in {"HIGH", "HOT", "URGENT"}:
        return "T1"
    if t in {"MED", "MEDIUM"}:
        return "T2"
    if t in {"LOW", "COLD"}:
        return "T3"
    return "T3"


def plan_from_tier(tier: str | None) -> CadencePlan:
    t = _normalize_tier(tier)

    # Conservative defaults in days (can be tuned later)
    if t == "T0":
        return CadencePlan(tier=t, period_days=7, rationale="T0: highest urgency monitoring tier.")
    if t == "T1":
        return CadencePlan(tier=t, period_days=30, rationale="T1: active targets, monthly sampling.")
    if t == "T2":
        return CadencePlan(tier=t, period_days=60, rationale="T2: warm targets, bi-monthly sampling.")
    if t == "T3":
        return CadencePlan(tier=t, period_days=90, rationale="T3: baseline targets, quarterly sampling.")
    return CadencePlan(tier=t, period_days=180, rationale="T4: low priority, semiannual sampling.")
