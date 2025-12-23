WATCHLIST_RULES_ENABLED = False

def evaluate_watchlist_candidate(row: dict) -> str | None:
    """
    Returns existing Watchlist_Flag unless rules are enabled.
    """
    if not WATCHLIST_RULES_ENABLED:
        return row.get("Watchlist_Flag")

    # Future logic (intentionally unreachable)
    return row.get("Watchlist_Flag")
