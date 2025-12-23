"""
title_variant_resolver.py
Variant/Legacy/Adjacent/Industry Title resolution.

Purpose:
- Normalize drifting titles and map them into stable canonical families.
- Reduce misclassification due to ambiguous enterprise titles.

© 2025 L. David Mendoza
Version: v1.0.0
Date: 2025-12-23
Changelog:
- Initial Phase-Next implementation.
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, Optional
import re

@dataclass(frozen=True)
class TitleResolution:
    raw_title: str
    normalized_title: str
    canonical_family: str
    confidence: float

_CANONICAL_MAP: Dict[str, str] = {
    # Examples, extend over time in a governed way:
    "member of technical staff": "MTS",
    "mts": "MTS",
    "research engineer": "Research Engineer",
    "research scientist": "Research Scientist",
    "software engineer": "Software Engineer",
    "principal engineer": "Principal Engineer",
}

_FAMILY_RULES = [
    (re.compile(r"\b(research)\b", re.I), "Research"),
    (re.compile(r"\b(ml|machine learning|ai)\b", re.I), "AI/ML"),
    (re.compile(r"\b(infra|platform|distributed|systems|sre)\b", re.I), "Infra/Systems"),
]

def resolve_title(title: str) -> TitleResolution:
    raw = title or ""
    t = raw.strip().lower()
    t = re.sub(r"\s+", " ", t)

    normalized = _CANONICAL_MAP.get(t, raw.strip())

    canonical_family = "General"
    conf = 0.50

    for rx, fam in _FAMILY_RULES:
        if rx.search(raw):
            canonical_family = fam
            conf = 0.70
            break

    # If normalized maps strongly, bump confidence.
    if t in _CANONICAL_MAP:
        conf = max(conf, 0.80)

    return TitleResolution(
        raw_title=raw,
        normalized_title=normalized,
        canonical_family=canonical_family,
        confidence=conf
    )
