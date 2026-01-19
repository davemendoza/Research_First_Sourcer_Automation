#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EXECUTION_CORE/seed_locator.py
============================================================
AUTHORITATIVE SEED RESOLUTION (FAIL-CLOSED)

Author: L. David Mendoza © 2026
Version: v1.0.0

Seed priority (LOCKED):
1) seeds/{prefix}.csv
2) OUTPUTS/scenario/{prefix}/LATEST.csv   (scenario replay only)
3) data/{prefix}_input.csv                (legacy dev fallback; warning)

NEVER:
- OUTPUTS/{prefix}.csv
- Any file directly under OUTPUTS root

If no seed is found, FAIL with an explicit list of paths checked.
"""

from __future__ import annotations

from pathlib import Path
from typing import List


class SeedResolutionError(RuntimeError):
    pass


def resolve_seed_csv(
    repo_root: Path,
    prefix: str,
    mode: str,
) -> Path:
    """
    Resolve the seed CSV for a given prefix and mode.

    Args:
        repo_root: Repository root Path
        prefix: canonical role/seed key (e.g., frontier_ai_scientist)
        mode: demo | scenario | gpt_slim

    Returns:
        Path to resolved seed CSV

    Raises:
        SeedResolutionError if no valid seed is found
    """

    prefix = (prefix or "").strip()
    if not prefix:
        raise SeedResolutionError("Seed prefix is empty")

    mode = (mode or "").strip().lower()
    if mode not in {"demo", "scenario", "gpt_slim"}:
        raise SeedResolutionError(f"Invalid mode for seed resolution: {mode}")

    checked: List[Path] = []

    # 1) Canonical seeds
    p1 = (repo_root / "seeds" / f"{prefix}.csv").resolve()
    checked.append(p1)
    if p1.exists():
        return p1

    # 2) Scenario replay (only if scenario)
    if mode == "scenario":
        p2 = (repo_root / "OUTPUTS" / "scenario" / prefix / "LATEST.csv").resolve()
        checked.append(p2)
        if p2.exists():
            return p2

    # 3) Legacy dev fallback (warn-only in logs)
    p3 = (repo_root / "data" / f"{prefix}_input.csv").resolve()
    checked.append(p3)
    if p3.exists():
        return p3

    # Fail closed with explicit diagnostics
    msg = (
        "Seed resolution failed.\n"
        f"Prefix: {prefix}\n"
        f"Mode: {mode}\n"
        "Checked paths:\n"
        + "\n".join(f"  - {p}" for p in checked)
        + "\n\nNOTE: OUTPUTS root is NOT a valid seed source."
    )
    raise SeedResolutionError(msg)


__all__ = ["SeedResolutionError", "resolve_seed_csv"]
