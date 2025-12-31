"""
Phase F Velocity Analyzer
- Flags accelerated presence based on count of distinct sources/events
- Deterministic and conservative
"""

from __future__ import annotations
from typing import Dict, List, Any

def analyze_velocity(timelines: Dict[str, List[Dict[str, Any]]], min_events: int) -> Dict[str, Dict[str, Any]]:
    velocity = {}
    for name, events in timelines.items():
        distinct_sources = sorted(set(e.get("source", "") for e in events if e.get("source")))
        years = sorted(set(e.get("year") for e in events if e.get("year")))
        if len(events) >= min_events:
            velocity[name] = {
                "signal": "ACCELERATED_ACTIVITY",
                "event_count": len(events),
                "distinct_sources": distinct_sources,
                "years_observed": years,
            }
    return velocity
