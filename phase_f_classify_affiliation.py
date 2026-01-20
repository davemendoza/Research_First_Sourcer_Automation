"""
Phase F Affiliation Classifier (Conservative)
- Uses configurable regexes
- Outputs a tag: 'academia' | 'industry' | 'unknown'
- No claims, only flags
"""

from __future__ import annotations
from typing import List, Pattern

def classify(affiliation: str, academia_regexes: List[Pattern], industry_regexes: List[Pattern]) -> str:
    text = (affiliation or "").strip()
    if not text:
        return "unknown"

    for rx in academia_regexes:
        if rx.search(text):
            return "academia"

    for rx in industry_regexes:
        if rx.search(text):
            return "industry"

    return "unknown"
