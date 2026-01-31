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
# FILE: evaluation/scoring.py
# VERSION: v1.0.0
#
# CHANGELOG:
# - v1.0.0 (2026-01-31): Deterministic tier assignment and EQI scoring.
#
# VALIDATION:
# - python3 -c "from evaluation.scoring import evaluate_candidate; print('ok')"
#
# GIT:
# - git add evaluation/scoring.py
# - git commit -m "Add deterministic scoring (v1.0.0)"
# - git push
#

from __future__ import annotations

from typing import List, Tuple

try:
    from ai_role_registry import assert_valid_role
except Exception as e:
    def assert_valid_role(role: str) -> None:
        raise RuntimeError("ai_role_registry.py not available in import path") from e

from .schemas import CandidateProfile, EvaluationResult, unique_terms
from .role_determinants import DeterminantStore
from .evidence import EvidenceNormalizer


def _compute_eqi(tier1_hits: List[str], tier2_hits: List[str], conditional_hits: List[str]) -> float:
    """
    Evidence Quality Index (EQI): deterministic, monotonic.
    Tier 1 hits carry higher weight by design.
    """
    t1 = len(tier1_hits) * 3.0
    t2 = len(tier2_hits) * 1.0
    tc = len(conditional_hits) * 0.5
    return round(t1 + t2 + tc, 2)


def _tier_decision(role_type: str, tier1_hits: List[str], tier2_hits: List[str]) -> str:
    """
    Fail-closed tiering rule:
    - Tier 1 requires explicit Tier 1 determinative evidence hits.
    - Tier 2 requires at least one Tier 2 signal when Tier 1 is absent.
    - Otherwise Indeterminate.
    """
    if tier1_hits:
        return "Tier 1"
    if tier2_hits:
        return "Tier 2"
    return "Indeterminate"


def evaluate_candidate(
    repo_root: str,
    candidate: CandidateProfile,
    canonical_role_type: str,
) -> EvaluationResult:
    assert_valid_role(canonical_role_type)

    det = DeterminantStore(repo_root).get(canonical_role_type)
    normalizer = EvidenceNormalizer(repo_root)

    evidence_blob = " ".join([
        candidate.headline or "",
        candidate.summary or "",
        candidate.skills_text or "",
        candidate.experience_text or "",
        " ".join([a.raw_text or "" for a in candidate.artifacts]),
    ]).strip()

    terms = normalizer.extract_terms(evidence_blob)

    tier1_hits = [t for t in terms if t in set(det.tier1_allow)]
    tier2_hits = [t for t in terms if t in set(det.tier2_allow)]
    conditional_hits = [t for t in terms if t in set(det.conditional)]

    tier1_hits = unique_terms(tier1_hits)
    tier2_hits = unique_terms(tier2_hits)
    conditional_hits = unique_terms(conditional_hits)

    tier = _tier_decision(canonical_role_type, tier1_hits, tier2_hits)
    eqi = _compute_eqi(tier1_hits, tier2_hits, conditional_hits)

    rationale = (
        f"Role locked to '{canonical_role_type}'. "
        f"Tier assigned deterministically from explicit evidence hits. "
        f"Tier 1 hits: {len(tier1_hits)}. Tier 2 hits: {len(tier2_hits)}. Conditional hits: {len(conditional_hits)}."
    )

    strengths = (
        "Strengths derived from explicit evidence hits. "
        "Populate role-specific narrative once role allow-lists are fully expanded in knowledge files."
    )
    weaknesses = (
        "Weaknesses derived from missing determinative evidence for this role. "
        "Populate role-specific gaps once allow-lists are expanded."
    )

    return EvaluationResult(
        person_id=candidate.person_id,
        canonical_role_type=canonical_role_type,
        tier=tier,
        eqi_score=eqi,
        tier1_hits=tier1_hits,
        tier2_hits=tier2_hits,
        conditional_hits=conditional_hits,
        rationale=rationale,
        strengths=strengths,
        weaknesses=weaknesses,
        debug={
            "terms_extracted_count": str(len(terms)),
            "evidence_blob_chars": str(len(evidence_blob)),
        },
    )


def evaluate_batch(repo_root: str, candidates: List[CandidateProfile], canonical_role_type: str) -> List[EvaluationResult]:
    assert_valid_role(canonical_role_type)
    out: List[EvaluationResult] = []
    for c in candidates:
        out.append(evaluate_candidate(repo_root, c, canonical_role_type))
    return out