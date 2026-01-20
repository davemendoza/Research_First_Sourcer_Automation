"""
Seed locator for execution runs.
Resolves the correct seed CSV for demo, scenario, or production modes.
"""

import os
from pathlib import Path


class SeedResolutionError(Exception):
    pass


def resolve_seed_csv(role_key: str, mode: str) -> Path:
    """
    Resolve seed CSV based on role key and execution mode.

    Args:
        role_key: canonical role identifier (e.g. frontier_ai)
        mode: demo | scenario | production

    Returns:
        Path to CSV seed file
    """

    base_dir = Path("data/seeds")

    candidates = [
        base_dir / mode / f"{role_key}.csv",
        base_dir / f"{role_key}.csv",
    ]

    for path in candidates:
        if path.exists():
            return path.resolve()

    raise SeedResolutionError(
        f"No seed CSV found for role='{role_key}' mode='{mode}'. "
        f"Checked: {', '.join(str(p) for p in candidates)}"
    )
