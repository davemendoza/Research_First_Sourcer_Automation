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
