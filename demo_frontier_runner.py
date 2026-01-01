#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Demo Frontier Runner (Canonical)

Executes a bounded, real frontier scenario using the
existing ai_talent_scenario_runner pipeline.

NO placeholders.
NO synthetic people.
NO demo-only shortcuts.
"""

from __future__ import annotations

import sys
from pathlib import Path
from contextlib import contextmanager


@contextmanager
def patched_argv(argv):
    old_argv = sys.argv[:]
    sys.argv = argv
    try:
        yield
    finally:
        sys.argv = old_argv


def run_demo_frontier(
    *,
    scenario: str,
    output_path: Path,
    min_results: int | None = None,
    target_results: int | None = None,
    max_results: int | None = None,
) -> None:
    """
    Execute the real frontier pipeline in demo-bounded mode.
    """

    from ai_talent_scenario_runner import main as pipeline_main

    argv = [
        "ai_talent_scenario_runner",
        scenario,
        "--output",
        str(output_path),
    ]

    if min_results is not None:
        argv += ["--min-results", str(min_results)]
    if target_results is not None:
        argv += ["--target-results", str(target_results)]
    if max_results is not None:
        argv += ["--max-results", str(max_results)]

    # Run pipeline exactly as CLI invocation
    with patched_argv(argv):
        pipeline_main()
