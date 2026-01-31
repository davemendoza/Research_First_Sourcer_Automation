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
# FILE: evaluation/role_determinants.py
# VERSION: v1.0.0
#
# CHANGELOG:
# - v1.0.0 (2026-01-31): Determinant store with fail-closed role validation.
#
# VALIDATION:
# - python3 -c "from evaluation.role_determinants import DeterminantStore; print('ok')"
#
# GIT:
# - git add evaluation/role_determinants.py
# - git commit -m "Add determinant store (v1.0.0)"
# - git push
#

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from typing import Dict, List, Set, Tuple

try:
    from ai_role_registry import CANONICAL_AI_ROLE_TYPES, assert_valid_role
except Exception as e:
    CANONICAL_AI_ROLE_TYPES = []
    def assert_valid_role(role: str) -> None:
        raise RuntimeError("ai_role_registry.py not available in import path") from e


DEFAULT_GUARDRAIL_CATEGORIES: Dict[str, Dict[str, List[str]]] = {
    "LLM Foundation Models": {
        "tier1_roles": ["Foundational AI Scientist", "Frontier AI Research Scientist", "Applied AI Research Scientist", "Machine Learning Research Scientist", "RLHF Research Scientist"],
        "tier2_roles": ["AI Engineer (General)", "LLM Application Engineer", "AI Solutions Architect"],
        "notes": ["Tier 1 only if training or alignment is explicit."],
    },
    "GPU Cloud Model Serving": {
        "tier1_roles": ["AI Infrastructure Engineer", "ML Infrastructure Engineer", "Inference Optimization Engineer", "AI Performance Engineer", "LLM Systems Engineer", "Distributed Systems Engineer (AI Focus)", "Site Reliability Engineer (AI / ML)"],
        "tier2_roles": ["AI Engineer (General)", "Forward Deployed Engineer (AI)", "AI Solutions Architect"],
        "notes": ["Serving is not training."],
    },
    "Distributed Training Systems": {
        "tier1_roles": ["Foundational AI Scientist", "Frontier AI Research Scientist", "Model Training Engineer", "LLM Systems Engineer", "Distributed Systems Engineer (AI Focus)", "ML Infrastructure Engineer"],
        "tier2_roles": ["Applied Machine Learning Engineer", "Machine Learning Engineer (Data-Centric)"],
        "notes": ["Strong frontier signal when base model or scale is explicit."],
    },
    "Inference Engine Optimization": {
        "tier1_roles": ["Inference Optimization Engineer", "AI Performance Engineer", "LLM Systems Engineer", "Distributed Systems Engineer (AI Focus)"],
        "tier2_roles": ["AI Engineer (General)", "LLM Application Engineer"],
        "notes": ["Kernel or runtime ownership required for Tier 1."],
    },
    "Benchmark Evaluation": {
        "tier1_roles": ["Foundational AI Scientist", "Frontier AI Research Scientist", "AI Safety Engineer / Researcher", "AI Evaluation & Benchmarking Specialist", "RLHF Research Scientist"],
        "tier2_roles": ["LLM Application Engineer", "AI Engineer (General)"],
        "notes": ["Tier 1 only when evals drive model decisions."],
    },
    "Compiler / Kernel Acceleration": {
        "tier1_roles": ["AI Performance Engineer", "Inference Optimization Engineer", "LLM Systems Engineer"],
        "tier2_roles": [],
        "notes": ["CUDA or Triton kernel work is determinative."],
    },
}

DEFAULT_ROLE_FINGERPRINTS: Dict[str, Dict[str, List[str]]] = {
    # Minimal deterministic seed. Final v1.3+ will load from knowledge files.
    "AI Engineer (General)": {
        "tier1": [],
        "tier2": ["RAG", "Retrieval-Augmented Generation", "LangChain", "LlamaIndex", "Vector DB", "Pinecone", "Weaviate", "Chroma", "Qdrant", "FAISS", "FastAPI", "OpenAI API", "Anthropic API", "Gemini API"],
        "conditional": ["fine-tuning", "inference", "evaluation"],
    },
}


@dataclass(frozen=True)
class RoleDeterminants:
    role_type: str
    tier1_allow: Tuple[str, ...]
    tier2_allow: Tuple[str, ...]
    conditional: Tuple[str, ...]


class DeterminantStore:
    """
    Loads role-specific determinants from evaluation/knowledge/role_determinants.json.
    Falls back to minimal defaults if the file is not present.
    Fail-closed on invalid role names.
    """

    def __init__(self, repo_root: str) -> None:
        self.repo_root = repo_root
        self.knowledge_path = os.path.join(repo_root, "evaluation", "knowledge", "role_determinants.json")
        self._store: Dict[str, RoleDeterminants] = {}

        self._load()

    def _load(self) -> None:
        data = None
        if os.path.isfile(self.knowledge_path):
            with open(self.knowledge_path, "r", encoding="utf-8") as f:
                data = json.load(f)

        if data and isinstance(data, dict) and "roles" in data:
            roles = data.get("roles", {})
            for role, payload in roles.items():
                assert_valid_role(role)
                tier1 = tuple(payload.get("tier1", []))
                tier2 = tuple(payload.get("tier2", []))
                cond = tuple(payload.get("conditional", []))
                self._store[role] = RoleDeterminants(role, tier1, tier2, cond)
            return

        # Fallback minimal defaults
        for role in CANONICAL_AI_ROLE_TYPES:
            payload = DEFAULT_ROLE_FINGERPRINTS.get(role, {"tier1": [], "tier2": [], "conditional": []})
            self._store[role] = RoleDeterminants(
                role_type=role,
                tier1_allow=tuple(payload["tier1"]),
                tier2_allow=tuple(payload["tier2"]),
                conditional=tuple(payload["conditional"]),
            )

    def get(self, role_type: str) -> RoleDeterminants:
        assert_valid_role(role_type)
        if role_type not in self._store:
            raise ValueError(f"Role determinants missing for canonical role: {role_type}")
        return self._store[role_type]

    def list_roles(self) -> List[str]:
        return list(self._store.keys())