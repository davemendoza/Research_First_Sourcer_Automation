#!/usr/bin/env python3
"""
EXECUTION_CORE/determinant_tier_rules.py
============================================================
DAY 8 — DETERMINANT TIER POLICY (IMPORT-ONLY)

PURPOSE
- Define which evidence categories are determinative vs contextual vs weak
- Provide deterministic tier resolution with strict matching

THIS FILE:
- IS policy
- IS role-aware
- IS deterministic
- IS import-only

THIS FILE IS NOT:
- NOT a scorer
- NOT an aggregator
- NOT a CSV reader
- NOT executable
"""

from __future__ import annotations
from typing import Dict, List


DETERMINANT_TIERS: Dict[str, Dict[str, str]] = {
    "tier_1": {
        "label": "Primary Determinant",
        "description": "Direct evidence of role-critical capability; independently sufficient."
    },
    "tier_2": {
        "label": "Supporting Determinant",
        "description": "Strong supporting evidence; meaningful only when paired with Tier 1."
    },
    "tier_3": {
        "label": "Contextual Signal",
        "description": "Relevant background or exposure; never decisive alone."
    },
    "tier_4": {
        "label": "Non-Determinative",
        "description": "Generic, ambiguous, or surface-level signal."
    },
}


ROLE_DETERMINANT_CATEGORIES: Dict[str, Dict[str, List[str]]] = {
    "frontier": {
        "tier_1": [
            "base model training",
            "architecture research",
            "scaling laws",
            "rlhf training",
            "reward modeling",
            "first-author publications",
            "neurips",
            "iclr",
            "icml",
        ],
        "tier_2": [
            "fine-tuning",
            "evaluation benchmarks",
            "parameter-efficient tuning",
            "lora",
            "qlora",
            "dpo",
            "ppo",
        ],
        "tier_3": [
            "framework usage",
            "pytorch",
            "jax",
            "tensorflow",
        ],
        "tier_4": [
            "ai interest",
            "machine learning familiarity",
        ],
    },
    "infra": {
        "tier_1": [
            "gpu orchestration",
            "cuda",
            "distributed training",
            "deepspeed",
            "fsdp",
            "nccl",
            "kubernetes gpu",
        ],
        "tier_2": [
            "inference optimization",
            "tensorrt",
            "onnx",
            "vllm",
            "tgi",
            "triton",
        ],
        "tier_3": [
            "cloud infrastructure",
            "monitoring",
            "observability",
        ],
        "tier_4": [
            "docker",
            "linux",
        ],
    },
    "applied": {
        "tier_1": [
            "rag system design",
            "production llm deployment",
            "vector database integration",
            "langchain pipelines",
            "llamaindex pipelines",
        ],
        "tier_2": [
            "prompt engineering with context",
            "embeddings optimization",
            "retrieval tuning",
        ],
        "tier_3": [
            "model apis",
            "python ml stack",
        ],
        "tier_4": [
            "chatbot experience",
        ],
    },
    "solutions": {
        "tier_1": [
            "end-to-end deployment ownership",
            "customer production rollout",
            "integration architecture",
        ],
        "tier_2": [
            "api integration",
            "data pipeline design",
        ],
        "tier_3": [
            "technical documentation",
            "solution demos",
        ],
        "tier_4": [
            "client interaction",
        ],
    },
    "evangelism": {
        "tier_1": [
            "authoritative technical content",
            "open-source leadership",
            "conference talks",
        ],
        "tier_2": [
            "developer advocacy",
            "tutorial creation",
        ],
        "tier_3": [
            "blog posts",
            "community participation",
        ],
        "tier_4": [
            "social media presence",
        ],
    },
    "gtm": {
        "tier_1": [
            "technical deal ownership",
            "ai infrastructure sales",
        ],
        "tier_2": [
            "usage-based pricing knowledge",
            "technical gtm strategy",
        ],
        "tier_3": [
            "sales analytics",
        ],
        "tier_4": [
            "general saas sales",
        ],
    },
}


ANTI_INFLATION_RULES: Dict[str, bool] = {
    "single_keyword_never_sufficient": True,
    "tier_4_never_upgrades": True,
    "tier_3_requires_pairing": True,
    "tier_2_requires_tier_1": True,
}


def _norm(s: str) -> str:
    return (s or "").strip().lower()


def resolve_determinant_tier(
    *,
    role_family: str,
    evidence_category: str,
) -> str:
    """
    Strict deterministic resolution:
    - Normalize role_family and evidence_category
    - Exact match only within ROLE_DETERMINANT_CATEGORIES
    - Unknown -> tier_4
    """
    rf = _norm(role_family)
    ec = _norm(evidence_category)
    if not rf or not ec:
        return "tier_4"

    family_rules = ROLE_DETERMINANT_CATEGORIES.get(rf, {})
    if not family_rules:
        return "tier_4"

    for tier, categories in family_rules.items():
        for c in categories:
            if ec == _norm(c):
                return tier

    return "tier_4"


def explain_tier(tier: str) -> Dict[str, str]:
    info = DETERMINANT_TIERS.get(tier, DETERMINANT_TIERS["tier_4"])
    return {
        "tier": tier,
        "label": info["label"],
        "description": info["description"],
    }


__all__ = [
    "DETERMINANT_TIERS",
    "ROLE_DETERMINANT_CATEGORIES",
    "ANTI_INFLATION_RULES",
    "resolve_determinant_tier",
    "explain_tier",
]
