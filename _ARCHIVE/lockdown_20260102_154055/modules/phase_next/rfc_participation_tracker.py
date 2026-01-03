"""
rfc_participation_tracker.py
RFC and standards participation hooks.

© 2025 L. David Mendoza
Version: v1.0.0
Date: 2025-12-23
"""

from __future__ import annotations
from typing import Dict, List

def track(rfcs: List[Dict[str, object]]) -> Dict[str, float]:
    items = rfcs or []
    authored = sum(1 for r in items if str(r.get("role","")).lower() in ["author", "editor"])
    referenced = float(len(items))
    return {"rfc_authored": float(authored), "rfc_referenced": referenced}
