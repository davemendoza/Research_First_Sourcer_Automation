"""
Phase F Timeline Builder
- Builds per-person ordered timelines
- Deterministic output ordering
"""

from __future__ import annotations
from collections import defaultdict
from typing import Dict, List, Any

def build_timelines(records: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
    timelines = defaultdict(list)
    for r in records:
        timelines[r["name"]].append({
            "year": r.get("year"),
            "affiliation": r.get("affiliation", ""),
            "conference_signal": r.get("conference_signal", ""),
            "source": r.get("source", ""),
            "role": r.get("role")
        })

    for name in list(timelines.keys()):
        timelines[name].sort(key=lambda e: ((e["year"] or 0), e["source"], e["conference_signal"]))

    # Deterministic key order by sorting names
    ordered = {k: timelines[k] for k in sorted(timelines.keys(), key=lambda s: s.lower())}
    return ordered
