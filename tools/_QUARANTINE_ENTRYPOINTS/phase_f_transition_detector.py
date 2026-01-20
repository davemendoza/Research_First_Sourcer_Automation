"""
Phase F Transition Detector
- Detects conservative 'academia_to_industry' transitions
- Requires year by default (configurable)
"""

from __future__ import annotations
from typing import Dict, List, Any, Optional
from phase_f_classify_affiliation import classify

def detect_transitions(
    timelines: Dict[str, List[Dict[str, Any]]],
    academia_regexes,
    industry_regexes,
    require_year: bool,
) -> Dict[str, Dict[str, Any]]:
    transitions = {}

    for name, events in timelines.items():
        prev_class = None
        prev_event = None
        for e in events:
            if require_year and not e.get("year"):
                continue
            c = classify(e.get("affiliation", ""), academia_regexes, industry_regexes)
            if prev_class == "academia" and c == "industry":
                transitions[name] = {
                    "signal": "ACADEMIC_TO_INDUSTRY",
                    "from": prev_event,
                    "to": e,
                }
                break
            prev_class = c
            prev_event = e

    return transitions
