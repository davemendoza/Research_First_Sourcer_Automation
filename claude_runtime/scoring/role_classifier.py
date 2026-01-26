"""
AI TALENT ENGINE — SIGNAL INTELLIGENCE
Role Classifier (Claude Runtime)

Purpose:
- Classify candidates into AI role types using the canonical role registry
- Designed for isolated claude_runtime execution
- Bridges safely to EXECUTION_CORE.ai_role_registry (single source of truth)

Maintainer: L. David Mendoza © 2025
Status: Phase 1 (Runtime-Safe, Deterministic)
"""

from typing import Dict, Any, Optional

# Canonical role registry (authoritative source)
from EXECUTION_CORE.ai_role_registry import (
    ROLE_REGISTRY,
    DEFAULT_ROLE,
    classify_role_from_signals,
)


class RoleClassifier:
    """
    Determines the most appropriate AI role classification for a candidate
    based on normalized signals produced earlier in the pipeline.
    """

    def __init__(self, registry: Optional[Dict[str, Any]] = None):
        # Allow override for testing, default to canonical registry
        self.registry = registry if registry is not None else ROLE_REGISTRY

    def classify(self, candidate_record: Dict[str, Any]) -> Dict[str, Any]:
        """
        Classify a single candidate.

        Parameters
        ----------
        candidate_record : dict
            Enriched candidate data containing titles, skills, signals, etc.

        Returns
        -------
        dict
            Classification result with:
              - role_type
              - confidence
              - rationale
        """

        if not isinstance(candidate_record, dict):
            return self._fallback("Invalid candidate record type")

        try:
            role, confidence, rationale = classify_role_from_signals(
                candidate_record,
                self.registry
            )

            return {
                "role_type": role,
                "confidence": confidence,
                "rationale": rationale,
            }

        except Exception as exc:
            return self._fallback(str(exc))

    def _fallback(self, reason: str) -> Dict[str, Any]:
        """
        Safe fallback classification when determinative logic fails.
        """

        return {
            "role_type": DEFAULT_ROLE,
            "confidence": 0.0,
            "rationale": f"Fallback classification applied: {reason}",
        }
