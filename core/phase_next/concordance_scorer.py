"""
concordance_scorer.py
Measured concordance between claims and evidence.

© 2025 L. David Mendoza
Version: v1.0.0
Date: 2025-12-23
"""

from __future__ import annotations
from typing import Dict, List

def score(claims: List[str], evidence: List[str]) -> Dict[str, float]:
    # Deterministic placeholder: overlap count.
    c = " ".join(claims or []).lower()
    e = " ".join(evidence or []).lower()
    hits = 0
    for w in ["trained", "deployed", "optimized", "published", "open sourced"]:
        if w in c and w in e:
            hits += 1
    return {"concordance_hits": float(hits)}
