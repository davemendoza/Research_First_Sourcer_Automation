"""
EXECUTION_CORE/ai_role_registry.py
Authoritative canonical AI role registry.

Version: v1.0.0
Author: Dave Mendoza
Copyright (c) 2025-2026 L. David Mendoza. All rights reserved.

Changelog:
- v1.0.0: Canonical 27-role registry, strict validation, alias resolution, CLI list/resolve.

Validation:
- python3 -m py_compile EXECUTION_CORE/ai_role_registry.py
- python3 -m EXECUTION_CORE.ai_role_registry --list
- python3 -m EXECUTION_CORE.ai_role_registry --resolve "AI infra"

Git:
- git add EXECUTION_CORE/ai_role_registry.py
- git commit -m "Fix: canonical 27-role registry with alias resolution"
- git push
"""

from __future__ import annotations

import re
from typing import Dict, List, Set

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

_WS = re.compile(r"\s+")
_NON_ALNUM = re.compile(r"[^a-z0-9]+")


def normalize_key(s: str) -> str:
    s = (s or "").strip().lower()
    s = _NON_ALNUM.sub(" ", s)
    s = _WS.sub(" ", s).strip()
    return s


def list_roles() -> List[str]:
    return list(CANONICAL_AI_ROLE_TYPES)


def is_valid_role(role: str) -> bool:
    return bool(role) and role.strip() in _CANONICAL_SET


def _build_alias_map() -> Dict[str, str]:
    aliases: Dict[str, str] = {}

    # Canonical roles are always resolvable
    for role in CANONICAL_AI_ROLE_TYPES:
        aliases[normalize_key(role)] = role
        simplified = re.sub(r"\s*\([^)]*\)\s*", " ", role).strip()
        aliases.setdefault(normalize_key(simplified), role)
        aliases.setdefault(normalize_key(role.replace("/", " ")), role)

    # Human shorthand
    shorthand = {
        "frontier": "Frontier AI Research Scientist",
        "foundational": "Foundational AI Scientist",
        "foundation": "Foundational AI Scientist",
        "rlhf": "RLHF Research Scientist",
        "alignment": "RLHF Research Scientist",
        "reward modeling": "RLHF Research Scientist",
        "performance": "AI Performance Engineer",
        "perf": "AI Performance Engineer",
        "training": "Model Training Engineer",
        "inference": "Inference Optimization Engineer",
        "optimization": "Inference Optimization Engineer",
        "llm": "LLM Systems Engineer",
        "llm systems": "LLM Systems Engineer",
        "ai engineer": "AI Engineer (General)",
        "genai": "Generative AI Engineer",
        "generative ai": "Generative AI Engineer",
        "rag": "LLM Application Engineer",
        "ai infra": "AI Infrastructure Engineer",
        "infra": "AI Infrastructure Engineer",
        "ml infra": "ML Infrastructure Engineer",
        "distributed": "Distributed Systems Engineer (AI Focus)",
        "distributed systems": "Distributed Systems Engineer (AI Focus)",
        "sre": "Site Reliability Engineer (AI / ML)",
        "platform": "Platform Engineer (AI Systems)",
        "data centric": "Machine Learning Engineer (Data-Centric)",
        "data engineer": "Data Engineer (AI Pipelines)",
        "mlops": "MLOps Engineer",
        "fde": "Forward Deployed Engineer (AI)",
        "forward deployed": "Forward Deployed Engineer (AI)",
        "solutions architect": "AI Solutions Architect",
        "devrel": "Developer Relations Engineer (AI)",
        "developer relations": "Developer Relations Engineer (AI)",
        "evangelist": "Technical Evangelist (AI / ML)",
        "safety": "AI Safety Engineer / Researcher",
        "eval": "AI Evaluation & Benchmarking Specialist",
        "evaluation": "AI Evaluation & Benchmarking Specialist",
        "benchmarking": "AI Evaluation & Benchmarking Specialist",
    }

    for k, v in shorthand.items():
        aliases[normalize_key(k)] = v

    return aliases


_ALIAS_MAP = _build_alias_map()


def resolve_role(human_input: str) -> str:
    key = normalize_key(human_input)
    return _ALIAS_MAP.get(key, "")


def assert_valid_role(role: str) -> None:
    if not is_valid_role(role):
        raise ValueError(f"Invalid role: {role}")


def _cli_main() -> int:
    import argparse

    ap = argparse.ArgumentParser(description="Canonical AI role registry.")
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--resolve", default="")
    args = ap.parse_args()

    if args.list:
        print("\n".join(CANONICAL_AI_ROLE_TYPES))
        return 0

    if args.resolve:
        r = resolve_role(args.resolve)
        if r:
            print(r)
            return 0
        return 2

    ap.print_help()
    return 0


if __name__ == "__main__":
    raise SystemExit(_cli_main())
