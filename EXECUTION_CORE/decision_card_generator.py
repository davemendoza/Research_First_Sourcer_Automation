# © 2026 L. David Mendoza
#
# FILE: decision_card_generator.py
#
# PURPOSE:
# Generate structured, machine-readable "decision cards" explaining
# why one candidate ranks above another.
#
# DESIGN:
# - No IO
# - No formatting
# - No scoring
# - Consumes evaluation outputs only
#
# IMPORT-ONLY. NO SIDE EFFECTS.

from typing import Dict, Any, List


def generate_decision_card(
    higher: Dict[str, Any],
    lower: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Compare two evaluated candidates and explain the ranking difference.

    Expects each input to include:
    - role_family
    - final_score
    - determinant_tiers
    - canonical_evidence
    """

    reasons: List[str] = []

    if higher.get("final_score", 0) != lower.get("final_score", 0):
        reasons.append("final_score_difference")

    if higher.get("determinant_tiers") != lower.get("determinant_tiers"):
        reasons.append("determinant_tier_strength")

    if len(higher.get("canonical_evidence", [])) > len(lower.get("canonical_evidence", [])):
        reasons.append("evidence_density")

    return {
        "higher_candidate_id": higher.get("candidate_id"),
        "lower_candidate_id": lower.get("candidate_id"),
        "role_family": higher.get("role_family"),
        "reasons": reasons,
        "score_delta": higher.get("final_score", 0) - lower.get("final_score", 0),
    }
