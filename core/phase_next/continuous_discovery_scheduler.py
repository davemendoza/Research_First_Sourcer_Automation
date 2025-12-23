"""
continuous_discovery_scheduler.py
Continuous discovery loop driver.

Purpose:
- Establish a deterministic schedule of discovery runs.
- Does not run in background. It is invoked explicitly by runner.

© 2025 L. David Mendoza
Version: v1.0.0
Date: 2025-12-23
"""

from __future__ import annotations
from typing import Dict

def plan(monitoring_tier: str) -> Dict[str, int]:
    tier = (monitoring_tier or "").strip().lower()
    if tier in ["high", "tier1", "t1"]:
        return {"recommended_days": 3}
    if tier in ["medium", "tier2", "t2"]:
        return {"recommended_days": 7}
    return {"recommended_days": 14}
