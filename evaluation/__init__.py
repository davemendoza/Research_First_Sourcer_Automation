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
# FILE: evaluation/__init__.py
# VERSION: v1.0.0
#
# CHANGELOG:
# - v1.0.0 (2026-01-31): Initial evaluation module package exports.
#
# VALIDATION:
# - python3 -c "import evaluation; print('ok')"
#
# GIT:
# - git add evaluation/__init__.py
# - git commit -m "Add evaluation module package init (v1.0.0)"
# - git push
#

from .schemas import CandidateProfile, EvidenceArtifact, EvaluationResult
from .role_determinants import DeterminantStore
from .evidence import EvidenceNormalizer
from .scoring import evaluate_candidate, evaluate_batch
from .ranker import rank_candidates
from .business_impact import summarize_business_impact

__all__ = [
    "CandidateProfile",
    "EvidenceArtifact",
    "EvaluationResult",
    "DeterminantStore",
    "EvidenceNormalizer",
    "evaluate_candidate",
    "evaluate_batch",
    "rank_candidates",
    "summarize_business_impact",
]