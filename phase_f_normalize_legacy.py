"""
Phase F Normalization
- Normalizes records to stable schema
- No enrichment, no scraping
"""

from __future__ import annotations
from typing import Dict, Any, List, Optional

REQUIRED_KEYS = ["name", "affiliation", "conference_signal", "source"]

def normalize_records(raw: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    norm = []
    for r in raw:
        item = {k: r.get(k) for k in REQUIRED_KEYS}
        # Optional keys if present
        item["year"] = r.get("year")
        item["role"] = r.get("role")
        # Stable fallbacks
        item["affiliation"] = item["affiliation"] or ""
        item["source"] = item["source"] or ""
        item["conference_signal"] = item["conference_signal"] or ""
        item["name"] = (item["name"] or "").strip()
        if not item["name"]:
            # Skip invalid rows deterministically
            continue
        norm.append(item)
    # Deterministic ordering
    norm.sort(key=lambda x: (x["name"].lower(), (x.get("year") or 0), x["source"]))
    return norm
