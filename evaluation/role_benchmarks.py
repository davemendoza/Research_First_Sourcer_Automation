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
# FILE: evaluation/role_benchmarks.py
# VERSION: v1.0.0
#
# CHANGELOG:
# - v1.0.0 (2026-01-31): Benchmark vocabulary seeds.
#
# VALIDATION:
# - python3 -c "from evaluation.role_benchmarks import BENCHMARK_TERMS; print(len(BENCHMARK_TERMS))"
#
# GIT:
# - git add evaluation/role_benchmarks.py
# - git commit -m "Add benchmark vocabulary seeds (v1.0.0)"
# - git push
#

from __future__ import annotations

from typing import Set

# Determinative if used in a model-driving evaluation context.
BENCHMARK_TERMS: Set[str] = {
    "HELM",
    "MMLU",
    "MMLU-Pro",
    "GSM8K",
    "HellaSwag",
    "ARC",
    "TruthfulQA",
    "HumanEval",
    "MBPP",
    "SWE-bench",
    "SWE-bench Verified",
    "MLE-bench",
    "PaperBench",
    "HarmBench",
    "AdvBench",
}

# Common evaluation framework terms that often indicate a Tier 1 evaluation function.
EVAL_FRAMEWORK_TERMS: Set[str] = {
    "eval harness",
    "evaluation harness",
    "evaluation framework",
    "frontier evals",
    "capability assessment",
    "benchmark-driven iteration",
}