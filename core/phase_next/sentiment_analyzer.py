"""
sentiment_analyzer.py
Technical sentiment, not opinionated.

Purpose:
- Score peer reception signals as technical credibility indicators.
- Input is structured evidence harvested by Python ingestion.

© 2025 L. David Mendoza
Version: v1.0.0
Date: 2025-12-23
"""

from __future__ import annotations
from typing import Dict

def score_technical_sentiment(text: str) -> Dict[str, float]:
    # Deterministic placeholder scoring:
    # Later: GPT can interpret nuanced tone, but Python should provide feature hooks.
    t = (text or "").lower()
    pos = sum(1 for w in ["excellent", "robust", "state-of-the-art", "breakthrough", "solid"] if w in t)
    neg = sum(1 for w in ["broken", "buggy", "incorrect", "misleading", "unsafe"] if w in t)
    return {
        "tech_sent_pos_hits": float(pos),
        "tech_sent_neg_hits": float(neg),
        "tech_sent_balance": float(pos - neg),
    }
