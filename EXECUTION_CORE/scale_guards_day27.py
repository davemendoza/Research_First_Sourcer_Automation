# © 2026 L. David Mendoza
#
# FILE: scale_guards_day27.py
#
# PURPOSE:
# Guardrails that prevent accidental O(n^2) growth, runaway recomputation,
# and uncontrolled external recovery attempts.
#
# DESIGN:
# - Import-only
# - No IO
# - Fail-closed checks
# - Pure helpers intended to be called by binders/runners
#
# IMPORT-ONLY. NO SIDE EFFECTS.

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Iterable, List, Mapping, Optional, Sequence


class ScaleGuardError(RuntimeError):
    """Raised when a scale or recomputation invariant is violated."""


@dataclass(frozen=True)
class ScaleLimits:
    max_rows: int
    max_pairwise_comparisons: int
    max_recovery_calls: int


def enforce_row_limit(rows: Sequence[Any], max_rows: int) -> None:
    if len(rows) > max_rows:
        raise ScaleGuardError(f"Row limit exceeded: {len(rows)} > {max_rows}")


def estimate_pairwise_comparisons(n: int) -> int:
    # n*(n-1)/2
    return (n * (n - 1)) // 2


def enforce_pairwise_limit(n: int, max_pairwise: int) -> None:
    est = estimate_pairwise_comparisons(n)
    if est > max_pairwise:
        raise ScaleGuardError(f"Pairwise comparison limit exceeded: {est} > {max_pairwise}")


def enforce_recovery_call_limit(planned_calls: int, max_calls: int) -> None:
    if planned_calls > max_calls:
        raise ScaleGuardError(f"Recovery call limit exceeded: {planned_calls} > {max_calls}")


def enforce_no_accidental_recompute(flags: Mapping[str, Any], required_false_keys: Sequence[str]) -> None:
    """
    Enforces that specific recomputation flags are explicitly False.
    This prevents accidental reruns of expensive steps.
    """
    for k in required_false_keys:
        if flags.get(k) is True:
            raise ScaleGuardError(f"Recompute flag must not be True: {k}")
