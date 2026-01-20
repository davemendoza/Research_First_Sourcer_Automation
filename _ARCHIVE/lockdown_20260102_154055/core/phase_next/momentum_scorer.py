"""
momentum_scorer.py
Momentum scoring for rising vs static contributors.

© 2025 L. David Mendoza
Version: v1.0.0
Date: 2025-12-23
"""

from __future__ import annotations
from typing import Dict

def score(momentum_inputs: Dict[str, float]) -> Dict[str, float]:
    mi = momentum_inputs or {}
    v = float(mi.get("velocity", 0.0))
    d = float(mi.get("delta", 0.0))
    score = v + 2.0 * d
    return {"momentum_score": score}
