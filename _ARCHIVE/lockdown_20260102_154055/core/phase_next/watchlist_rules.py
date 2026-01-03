"""
Watchlist Promotion Rules (READ-ONLY)

This module evaluates whether a row should be escalated/promoted to a watchlist.
It NEVER writes to Excel; it only returns a decision object.

Signals are placeholders for now (no biasing population of Seed Hub columns).
Later phases can replace these with real evidence from open sources.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from .analysis_envelope import WatchlistDecision
from .control_plane import WATCHLIST_RULES_ENABLED


def _truthy(v: Any) -> bool:
    if v is None:
        return False
    s = str(v).strip().lower()
    return s in {"1", "true", "yes", "y", "on"}


def evaluate_watchlist(row: Dict[str, Any]) -> WatchlistDecision:
    """
    READ-ONLY evaluator.
    Returns WatchlistDecision regardless of enabled state, but if disabled,
    returns "NOOP" to keep the pipeline stable.
    """
    if not WATCHLIST_RULES_ENABLED:
        return WatchlistDecision(decision="NOOP", reason="Watchlist rules disabled.", signals=[])

    signals: List[str] = []

    # These are intentionally generic and non-invasive.
    # Later, real evidence signals (citations velocity, repo burst, conference movement) can be wired in.
    if _truthy(row.get("Watchlist_Flag")):
        signals.append("seed_hub_watchlist_flag_true")

    # Example: treat Tier T0/T1 as an escalation factor (planning only)
    tier = (row.get("Monitoring_Tier") or "").strip().upper()
    if tier in {"T0", "T1"}:
        signals.append(f"monitoring_tier_{tier.lower()}")

    # Domain/type provenance signals (planning only)
    domain_type = (row.get("Domain_Type") or "").strip()
    if domain_type:
        signals.append("domain_type_present")

    source_category = (row.get("Source_Category") or "").strip()
    if source_category:
        signals.append("source_category_present")

    # Decision logic (simple, deterministic)
    if len(signals) >= 3:
        return WatchlistDecision(
            decision="PROMOTE",
            reason="3 escalation signals detected",
            signals=signals,
        )

    if len(signals) == 2:
        return WatchlistDecision(
            decision="HOLD",
            reason="2 escalation signals detected",
            signals=signals,
        )

    return WatchlistDecision(
        decision="IGNORE",
        reason="Insufficient escalation signals",
        signals=signals,
    )


# Compatibility alias (future-proof)
evaluate_watchlist_candidate = evaluate_watchlist
