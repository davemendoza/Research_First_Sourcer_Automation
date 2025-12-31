#!/usr/bin/env python3
"""
AI Talent Engine – People Scorer
Version: v1.0.0-ultra
Date: 2025-12-30
© 2025 L. David Mendoza. All Rights Reserved.

GOAL
Deterministic scoring for interview-safe ranking.
No hidden knobs. No unstable heuristics.

Score inputs:
- Count of scenarios triggered
- Count of evidence URLs
- Count of unique topics/keywords from raw_signals
"""

from __future__ import annotations

from typing import List, Dict

def score_people(people: List[dict]) -> List[dict]:
    out = []
    for p in people:
        scenario_count = len(set(p.get("scenario_tags") or []))
        evidence_count = len(set(p.get("evidence_urls") or []))
        rs = p.get("raw_signals") or {}
        topic_count = 0
        if isinstance(rs.get("topics"), list):
            topic_count = len(set(rs["topics"]))

        # deterministic linear score
        score = (scenario_count * 10.0) + (evidence_count * 2.0) + (topic_count * 1.5)

        p2 = dict(p)
        p2["signal_score"] = round(float(score), 2)
        out.append(p2)

    out.sort(key=lambda x: (-float(x.get("signal_score", 0.0)), (x.get("full_name") or "").lower()))
    return out
