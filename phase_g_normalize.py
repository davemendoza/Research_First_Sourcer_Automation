"""
Phase G Normalization
Normalizes input events into stable schema.

We intentionally support multiple event substrates:
- Phase E enqueue output (conference emergence)
- Optional custom "movement events" datasets (if user supplies later)
"""

from __future__ import annotations
from typing import Any, Dict, List

REQUIRED = ["name", "affiliation", "conference_signal", "source"]

def normalize_events(raw: Any) -> List[Dict[str, Any]]:
    events = []
    if isinstance(raw, list):
        for r in raw:
            name = (r.get("name") or "").strip()
            if not name:
                continue
            event = {
                "name": name,
                "affiliation": r.get("affiliation") or "",
                "signal": r.get("conference_signal") or r.get("signal") or "",
                "source": r.get("source") or "",
                "year": r.get("year"),
                "role_type": r.get("role_type") or "Unknown",  # optional, used for weighting
            }
            events.append(event)

    # Deterministic order
    events.sort(key=lambda x: (x["name"].lower(), (x.get("year") or 0), x["source"], x["signal"]))
    return events
