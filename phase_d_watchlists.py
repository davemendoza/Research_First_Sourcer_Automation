"""
Phase D Watchlists
"""

import json
from pathlib import Path

WATCHLIST_DIR = Path("watchlists")

def load_watchlist(name: str):
    path = WATCHLIST_DIR / f"{name}.json"
    if not path.exists():
        return set()
    with open(path, encoding="utf-8") as f:
        return set(json.load(f))

def apply_watchlist(diffs: dict, watchset: set):
    if not watchset:
        return diffs
    return {k: v for k, v in diffs.items() if k in watchset}
