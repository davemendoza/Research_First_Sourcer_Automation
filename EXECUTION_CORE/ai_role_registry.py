#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EXECUTION_CORE/ai_role_registry.py
============================================================
Authoritative AI Role Type Registry (LOCKED)

Source of truth for all demo + scenario role validation.
Any role not listed here is invalid by definition.

Maintainer: Dave Mendoza © 2026
Status: LOCKED
"""

from __future__ import annotations

from typing import List, Set


# DO NOT EDIT ORDER OR NAMES WITHOUT SCHEMA VERSION BUMP
CANONICAL_AI_ROLE_TYPES: List[str] = [
    "Foundational AI Scientist",
    "Frontier AI Research Scientist",
    "Applied AI Research Scientist",
    "Machine Learning Research Scientist",
    "RLHF Research Scientist",

    "AI Performance Engineer",
    "Model Training Engineer",
    "Inference Optimization Engineer",
    "LLM Systems Engineer",

    "AI Engineer (General)",
    "Applied Machine Learning Engineer",
    "Generative AI Engineer",
    "LLM Application Engineer",

    "AI Infrastructure Engineer",
    "ML Infrastructure Engineer",
    "Distributed Systems Engineer (AI Focus)",
    "Site Reliability Engineer (AI / ML)",
    "Platform Engineer (AI Systems)",

    "Machine Learning Engineer (Data-Centric)",
    "Data Engineer (AI Pipelines)",
    "MLOps Engineer",

    "Forward Deployed Engineer (AI)",
    "AI Solutions Architect",

    "Developer Relations Engineer (AI)",
    "Technical Evangelist (AI / ML)",

    "AI Safety Engineer / Researcher",
    "AI Evaluation & Benchmarking Specialist",
]


_CANONICAL_SET: Set[str] = set(CANONICAL_AI_ROLE_TYPES)


def is_valid_role(role: str) -> bool:
    if not role:
        return False
    return role.strip() in _CANONICAL_SET


def assert_valid_role(role: str) -> None:
    if not is_valid_role(role):
        raise ValueError(
            f"Invalid AI Role Type: '{role}'. "
            f"Must be one of the canonical AI role types."
        )


def list_roles() -> List[str]:
    return list(CANONICAL_AI_ROLE_TYPES)
