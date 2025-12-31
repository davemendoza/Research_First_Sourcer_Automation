"""
Phase G Role Weighting
Applies criticality multipliers based on role_type.
"""

from __future__ import annotations
from typing import Dict

def weight_for_role(role_type: str, weights: Dict[str, float]) -> float:
    rt = (role_type or "Unknown").strip()
    return float(weights.get(rt, weights.get("Unknown", 1.0)))
