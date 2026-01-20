"""
Phase G Cluster Detector
Detects clusters of signals by:
- Affiliation (default)
- Optional year window clustering if year present

No inference about "departures" unless explicitly represented by input events.
We only detect clustered *signals* from input.
"""

from __future__ import annotations
from collections import defaultdict
from typing import Dict, List, Any, Tuple

def cluster_by_affiliation(events: List[Dict[str, Any]], min_size: int) -> Dict[str, Dict[str, Any]]:
    buckets = defaultdict(list)
    for e in events:
        key = (e.get("affiliation") or "").strip() or "UNKNOWN_AFFILIATION"
        buckets[key].append(e)

    clusters = {}
    for aff, items in buckets.items():
        if len(items) >= min_size:
            clusters[aff] = {
                "cluster_type": "AFFILIATION_CLUSTER",
                "affiliation": aff,
                "count": len(items),
                "members": sorted({i["name"] for i in items}, key=lambda s: s.lower())
            }
    return clusters

def cluster_by_affiliation_year_window(events: List[Dict[str, Any]], min_size: int, year_window: int) -> Dict[str, Dict[str, Any]]:
    """
    Builds clusters per affiliation within +-year_window of a focal year.
    This is conservative: it only clusters when year exists.
    """
    by_aff_year = defaultdict(list)
    for e in events:
        aff = (e.get("affiliation") or "").strip() or "UNKNOWN_AFFILIATION"
        yr = e.get("year")
        if isinstance(yr, int):
            by_aff_year[(aff, yr)].append(e)

    clusters = {}
    for (aff, yr), items in by_aff_year.items():
        # Expand window by checking neighboring years
        window_items = []
        for dy in range(-year_window, year_window + 1):
            window_items.extend(by_aff_year.get((aff, yr + dy), []))

        if len(window_items) >= min_size:
            key = f"{aff}__{yr}"
            clusters[key] = {
                "cluster_type": "AFFILIATION_YEAR_WINDOW",
                "affiliation": aff,
                "focal_year": yr,
                "year_window": year_window,
                "count": len(window_items),
                "members": sorted({i["name"] for i in window_items}, key=lambda s: s.lower())
            }
    return clusters
