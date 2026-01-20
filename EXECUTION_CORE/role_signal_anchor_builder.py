#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
role_signal_anchor_builder.py
------------------------------------------------------------
Tier-2 Role Signal Anchors

Purpose:
- Produce human-legible role signal anchors
- Make rows feel intentional when scrolling
- Differentiate Frontier vs Infra vs Applied at a glance

Design Rules:
- Deterministic only
- No scraping
- No inference without evidence
- Blank when unclear (with reason handled elsewhere)
"""

from typing import Dict


# ------------------------------------------------------------------
# KEYWORD CLUSTERS
# ------------------------------------------------------------------

FRONTIER_SIGNALS = {
    "architecture", "scaling", "pretraining", "foundation model",
    "mixture-of-experts", "alignment", "rlhf", "evaluation"
}

INFRA_SIGNALS = {
    "distributed", "cuda", "nccl", "inference", "serving",
    "throughput", "latency", "kernel", "gpu", "systems"
}

APPLIED_SIGNALS = {
    "rag", "retrieval", "embeddings", "product", "integration",
    "application", "deployment", "pipeline"
}


# ------------------------------------------------------------------
# HELPERS
# ------------------------------------------------------------------

def _tokenize(text: str) -> set:
    return set((text or "").lower().replace(",", " ").split())


def _count_overlap(tokens: set, signals: set) -> int:
    return len(tokens & signals)


# ------------------------------------------------------------------
# PUBLIC API
# ------------------------------------------------------------------

def build_role_signal_anchors(row: Dict[str, str]) -> Dict[str, str]:
    """
    Returns a dict with Tier-2 role signal columns populated.
    """

    text_blob = " ".join([
        row.get("Determinative_Skill_Areas", ""),
        row.get("Repo_Topics_Keywords", ""),
        row.get("Inference_Training_Infra_Signals", ""),
        row.get("RLHF_Alignment_Signals", ""),
    ])

    tokens = _tokenize(text_blob)

    frontier_score = _count_overlap(tokens, FRONTIER_SIGNALS)
    infra_score = _count_overlap(tokens, INFRA_SIGNALS)
    applied_score = _count_overlap(tokens, APPLIED_SIGNALS)

    # Determine dominant orientation
    scores = {
        "Frontier": frontier_score,
        "Infrastructure": infra_score,
        "Applied": applied_score,
    }

    dominant = max(scores, key=scores.get)

    # No signal case
    if scores[dominant] == 0:
        return {
            "Role_Signal_Summary": "",
            "Primary_Skill_Cluster": "",
            "Secondary_Skill_Cluster": "",
            "Research_vs_Infra_vs_Applied": "",
            "Core_Domain_Classification": "",
        }

    # Build summaries
    summary = f"{dominant}-oriented AI contributor with corroborated technical signals"

    clusters = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    primary = clusters[0][0]
    secondary = clusters[1][0] if clusters[1][1] > 0 else ""

    return {
        "Role_Signal_Summary": summary,
        "Primary_Skill_Cluster": primary,
        "Secondary_Skill_Cluster": secondary,
        "Research_vs_Infra_vs_Applied": dominant,
        "Core_Domain_Classification": dominant,
    }
