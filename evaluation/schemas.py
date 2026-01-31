# ==============================================================================
# AI TALENT ENGINE – SIGNAL INTELLIGENCE
# Proprietary and Confidential
# © 2025–2026 L. David Mendoza. All Rights Reserved.
# ==============================================================================
#
# This file contains proprietary intellectual property and trade secrets of
# L. David Mendoza and is part of the AI Talent Engine – Signal Intelligence system.
#
# Unauthorized access, use, copying, modification, distribution, disclosure,
# reverse engineering, or derivative use, in whole or in part, is strictly
# prohibited without prior written authorization.
#
# ==============================================================================
#
# FILE: evaluation/schemas.py
# VERSION: v1.0.0
#
# CHANGELOG:
# - v1.0.0 (2026-01-31): Initial evaluation schemas.
#
# VALIDATION:
# - python3 -c "from evaluation.schemas import CandidateProfile; print('ok')"
#
# GIT:
# - git add evaluation/schemas.py
# - git commit -m "Add evaluation schemas (v1.0.0)"
# - git push
#

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set


@dataclass(frozen=True)
class EvidenceArtifact:
    """
    A single evidence item associated with a candidate.
    Evidence must be publicly verifiable and non-synthetic.

    Examples:
    - GitHub repo link, commits, PRs
    - Publications and citations
    - Benchmark results
    - Public design docs or writeups
    """
    artifact_type: str
    source_url: str
    raw_text: str = ""
    metadata: Dict[str, str] = field(default_factory=dict)


@dataclass
class CandidateProfile:
    """
    Candidate record used by the evaluation layer.
    Upstream ingestion may populate these fields from CSV and enrichment outputs.
    """
    person_id: str
    name: str = ""
    headline: str = ""
    summary: str = ""
    skills_text: str = ""
    experience_text: str = ""
    artifacts: List[EvidenceArtifact] = field(default_factory=list)


@dataclass
class EvaluationResult:
    """
    Deterministic evaluation output, intended for ranking and audit.
    """
    person_id: str
    canonical_role_type: str
    tier: str  # "Tier 1", "Tier 2", "Indeterminate"
    eqi_score: float
    tier1_hits: List[str] = field(default_factory=list)
    tier2_hits: List[str] = field(default_factory=list)
    conditional_hits: List[str] = field(default_factory=list)
    rationale: str = ""
    strengths: str = ""
    weaknesses: str = ""
    debug: Dict[str, str] = field(default_factory=dict)


def unique_terms(items: List[str]) -> List[str]:
    seen: Set[str] = set()
    out: List[str] = []
    for x in items:
        k = x.strip()
        if not k:
            continue
        if k in seen:
            continue
        seen.add(k)
        out.append(k)
    return out