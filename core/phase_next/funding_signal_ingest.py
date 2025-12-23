"""
funding_signal_ingest.py
Funding signals: grants, venture, lab funding (public sources).

© 2025 L. David Mendoza
Version: v1.0.0
Date: 2025-12-23
"""

from __future__ import annotations
from typing import Dict, List

def ingest(records: List[Dict[str, object]]) -> Dict[str, float]:
    recs = records or []
    grants = sum(1 for r in recs if str(r.get("type","")).lower() == "grant")
    venture = sum(1 for r in recs if str(r.get("type","")).lower() == "venture")
    return {
        "funding_grants": float(grants),
        "funding_venture": float(venture),
    }
