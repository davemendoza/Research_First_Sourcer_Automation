#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
canonical_role_resolver.py
--------------------------------------------------
Day 4 – Canonical Role Resolution

Purpose:
- Resolve natural-language scenario phrases into
  canonical AI role categories.
- Support child-proof demo inputs:
    "demo frontier scientist"
    "applied ml engineer"
    "infra gpu"
- Deterministic, auditable, and extensible.

Design Rules:
- No scraping
- No mutation
- No inference scoring
- Pure resolution logic only
"""

from typing import Optional

# --------------------------------------------------
# Canonical role map
# --------------------------------------------------

_CANONICAL_ROLE_MAP = {
    # Frontier / Research
    "frontier": "Frontier AI Scientist",
    "frontier scientist": "Frontier AI Scientist",
    "ai scientist": "Frontier AI Scientist",
    "research scientist": "Frontier AI Scientist",
    "research": "Frontier AI Scientist",

    # Applied ML
    "applied": "Applied ML Engineer",
    "applied ml": "Applied ML Engineer",
    "ml engineer": "Applied ML Engineer",
    "machine learning engineer": "Applied ML Engineer",

    # Infrastructure
    "infra": "AI Infrastructure Engineer",
    "infrastructure": "AI Infrastructure Engineer",
    "gpu": "AI Infrastructure Engineer",
    "systems": "AI Infrastructure Engineer",
    "platform": "AI Infrastructure Engineer",

    # RLHF / Alignment
    "rlhf": "RLHF Engineer",
    "alignment": "RLHF Engineer",
    "reward modeling": "RLHF Engineer",

    # General fallback
    "ai engineer": "AI Engineer",
}

# --------------------------------------------------
# Public API
# --------------------------------------------------

def resolve_canonical_role(scenario: Optional[str]) -> Optional[str]:
    """
    Resolve a natural-language scenario phrase into
    a canonical role label.

    Returns:
        Canonical role string or None
    """

    if not scenario:
        return None

    text = scenario.strip().lower()

    # Strip common demo prefixes safely
    for prefix in ("demo", "run", "simulate", "example"):
        if text.startswith(prefix + " "):
            text = text[len(prefix):].strip()

    # Direct phrase match (longest first)
    for key in sorted(_CANONICAL_ROLE_MAP.keys(), key=len, reverse=True):
        if key in text:
            return _CANONICAL_ROLE_MAP[key]

    return None


# --------------------------------------------------
# Debug / self-test
# --------------------------------------------------

if __name__ == "__main__":
    tests = [
        "demo frontier scientist",
        "applied ml engineer",
        "gpu infra",
        "rlhf alignment",
        "ai engineer",
        "unknown role"
    ]

    for t in tests:
        print(f"{t!r} -> {resolve_canonical_role(t)}")
