"""
Phase G Watchlists
Optional filtering to only score/watch entities of interest.
"""

from __future__ import annotations
import json
from pathlib import Path
from typing import Set

WATCHLIST_DIR = Path("watchlists")

def load_watchlist(name: str) -> Set[str]:
    path = WATCHLIST_DIR / f"{name}.json"
    if not path.exists():
        return set()
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    return set(data) if isinstance(data, list) else set()

def filter_scores(scores: dict, watchset: Set[str]) -> dict:
    if not watchset:
        return scores
    return {k: v for k, v in scores.items() if k in watchset}
