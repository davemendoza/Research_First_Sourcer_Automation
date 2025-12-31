"""
openalex_lifecycle_tracker.py
Paper lifecycle tracking: preprint -> published -> patent references.

© 2025 L. David Mendoza
Version: v1.0.0
Date: 2025-12-23
"""

from __future__ import annotations
from typing import Dict, List

def track(records: List[Dict[str, object]]) -> Dict[str, float]:
    recs = records or []
    pre = sum(1 for r in recs if str(r.get("type","")).lower() in ["preprint", "arxiv"])
    pub = sum(1 for r in recs if str(r.get("type","")).lower() in ["paper", "journal", "conference"])
    pat = sum(1 for r in recs if str(r.get("type","")).lower() in ["patent"])
    return {
        "openalex_preprints": float(pre),
        "openalex_published": float(pub),
        "openalex_patents": float(pat),
    }
