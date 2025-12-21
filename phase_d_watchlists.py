"""
Phase D Watchlists

Phase D introduces temporal awareness without altering the point-in-time
guarantees of Tracks A, B, and C. All judgment and prioritization remain downstream.
"""

import json
from pathlib import Path

WATCHLIST_DIR = Path("watchlists")

def load_watchlist(name: str):
    path = WATCHLIST_DIR / f"{name}.json"
    if not path.exists():
        return set()
    with open(path) as f:
        return set(json.load(f))

def filter_diffs(diffs: dict, watchlist: set):
    if not watchlist:
        return diffs
    return {k: v for k, v in diffs.items() if k in watchlist}
