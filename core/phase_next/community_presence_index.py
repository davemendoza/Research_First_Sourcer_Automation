"""
community_presence_index.py
Community Presence Index (CPI).

Purpose:
- Quantify presence across communities and platforms.
- Provide deterministic counts for GPT interpretation.

© 2025 L. David Mendoza
Version: v1.0.0
Date: 2025-12-23
"""

from __future__ import annotations
from typing import Dict, List

def compute_cpi(platform_hits: Dict[str, int]) -> Dict[str, float]:
    hits = platform_hits or {}
    total = sum(max(0, int(v)) for v in hits.values())
    diversity = sum(1 for v in hits.values() if int(v) > 0)
    return {
        "cpi_total_hits": float(total),
        "cpi_platform_diversity": float(diversity),
        "cpi_score": float(total + 3 * diversity),
    }
