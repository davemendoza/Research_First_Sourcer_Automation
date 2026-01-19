#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
role_signal_blank_reasoner.py
------------------------------------------------------------
Explains intentional blanks for Tier-2 role signal columns.

Purpose:
- Prevent "looks broken" reactions
- Make blanks auditable and defensible
- Ensure absence of evidence ≠ failure

Design Rules:
- Deterministic
- No scraping
- No hallucination
"""

from typing import Dict, List


# ------------------------------------------------------------------
# PUBLIC API (CANONICAL)
# ------------------------------------------------------------------

def explain_role_signal_blanks(
    row: Dict[str, str],
    populated_fields: List[str],
) -> Dict[str, str]:
    """
    Returns:
        Dict[column_name -> explanation string]
    """

    explanations: Dict[str, str] = {}

    tier2_fields = [
        "Role_Signal_Summary",
        "Primary_Skill_Cluster",
        "Secondary_Skill_Cluster",
        "Research_vs_Infra_vs_Applied",
        "Core_Domain_Classification",
    ]

    for field in tier2_fields:
        if field in populated_fields:
            continue

        explanations[field] = (
            "Insufficient corroborated technical signals available "
            "to assign this role signal deterministically."
        )

    return explanations
