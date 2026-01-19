#!/usr/bin/env python3
"""
EXECUTION_CORE/csv_density_policy.py
============================================================
DAY 7 — SIGNAL DENSITY POLICY (IMPORT-ONLY)

PURPOSE
- Define what "dense enough" means for signal population
- Provide deterministic density classification with no heuristic scaling

THIS FILE:
- IS policy
- IS deterministic
- IS role-aware
- IS import-only

THIS FILE IS NOT:
- NOT executable
- NOT a scorer
- NOT an aggregator
- NOT a CSV reader
- NOT a preview
"""

from __future__ import annotations
from typing import Dict


ROLE_FAMILIES: Dict[str, str] = {
    "Foundational AI Scientist": "frontier",
    "Frontier AI Scientist": "frontier",
    "Research Scientist": "frontier",
    "RLHF Researcher": "frontier",

    "AI Engineer": "applied",
    "AI Engineer (Parasail)": "applied",
    "Applied ML Engineer": "applied",
    "Machine Learning Engineer": "applied",

    "AI Infra Engineer": "infra",
    "ML Infrastructure Engineer": "infra",
    "Site Reliability Engineer": "infra",
    "Distributed Systems Engineer": "infra",

    "AI Solutions Architect": "solutions",
    "Forward Deployed Engineer": "solutions",

    "Developer Evangelist": "evangelism",
    "Technical Writer": "evangelism",

    "Account Executive": "gtm",
    "Revenue Operations Analyst": "gtm",
}


DENSITY_THRESHOLDS: Dict[str, Dict[str, float]] = {
    "frontier": {
        "min_nonempty_fields_avg": 18.0,
        "min_signal_fields_nonempty_avg": 6.0,
        "min_evidence_fields_nonempty_avg": 3.0,
    },
    "infra": {
        "min_nonempty_fields_avg": 15.0,
        "min_signal_fields_nonempty_avg": 5.0,
        "min_evidence_fields_nonempty_avg": 3.0,
    },
    "applied": {
        "min_nonempty_fields_avg": 14.0,
        "min_signal_fields_nonempty_avg": 4.0,
        "min_evidence_fields_nonempty_avg": 2.0,
    },
    "solutions": {
        "min_nonempty_fields_avg": 13.0,
        "min_signal_fields_nonempty_avg": 4.0,
        "min_evidence_fields_nonempty_avg": 2.0,
    },
    "evangelism": {
        "min_nonempty_fields_avg": 12.0,
        "min_signal_fields_nonempty_avg": 3.0,
        "min_evidence_fields_nonempty_avg": 2.0,
    },
    "gtm": {
        "min_nonempty_fields_avg": 10.0,
        "min_signal_fields_nonempty_avg": 2.0,
        "min_evidence_fields_nonempty_avg": 1.0,
    },
}


DENSITY_CLASSIFICATION: Dict[str, str] = {
    "strong": "Meets all minimum density thresholds.",
    "adequate": "Meets two of three minimum density thresholds.",
    "weak": "Meets one of three minimum density thresholds.",
    "deficient": "Meets zero minimum density thresholds.",
}


def resolve_role_family(role_type: str) -> str:
    role_type = (role_type or "").strip()
    if not role_type:
        return "applied"
    return ROLE_FAMILIES.get(role_type, "applied")


def classify_density(
    *,
    role_family: str,
    nonempty_fields_avg: float,
    signal_fields_nonempty_avg: float,
    evidence_fields_nonempty_avg: float,
) -> Dict[str, object]:
    rf = (role_family or "").strip().lower()
    thresholds = DENSITY_THRESHOLDS.get(rf, DENSITY_THRESHOLDS["applied"])

    min_nonempty = thresholds["min_nonempty_fields_avg"]
    min_signal = thresholds["min_signal_fields_nonempty_avg"]
    min_evidence = thresholds["min_evidence_fields_nonempty_avg"]

    checks = {
        "nonempty": nonempty_fields_avg >= min_nonempty,
        "signal": signal_fields_nonempty_avg >= min_signal,
        "evidence": evidence_fields_nonempty_avg >= min_evidence,
    }
    passed = sum(1 for v in checks.values() if v)

    if passed == 3:
        level = "strong"
    elif passed == 2:
        level = "adequate"
    elif passed == 1:
        level = "weak"
    else:
        level = "deficient"

    return {
        "density_level": level,
        "explanation": DENSITY_CLASSIFICATION[level],
        "role_family": rf if rf in DENSITY_THRESHOLDS else "applied",
        "thresholds": {
            "min_nonempty_fields_avg": min_nonempty,
            "min_signal_fields_nonempty_avg": min_signal,
            "min_evidence_fields_nonempty_avg": min_evidence,
        },
        "inputs": {
            "nonempty_fields_avg": nonempty_fields_avg,
            "signal_fields_nonempty_avg": signal_fields_nonempty_avg,
            "evidence_fields_nonempty_avg": evidence_fields_nonempty_avg,
        },
        "passed_checks": checks,
        "passed_count": passed,
    }


__all__ = [
    "ROLE_FAMILIES",
    "DENSITY_THRESHOLDS",
    "resolve_role_family",
    "classify_density",
]
