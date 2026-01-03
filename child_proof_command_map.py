#!/usr/bin/env python3
"""
Child-Proof Command Map
Version: Day 5 – Interview-Safe Frontier Fix
© 2025 L. David Mendoza

Purpose
-------
This file defines the ONLY allowed human commands (e.g. 'demo frontier')
and maps them deterministically to real execution scenarios.

No discovery.
No guessing.
No phantom flags.
No placeholder data.

All demo modes execute the REAL pipeline with bounded scope.
"""

from dataclasses import dataclass

@dataclass(frozen=True)
class CommandSpec:
    scenario: str
    demo_mode: bool
    description: str
    confirmation_banner: str

COMMAND_MAP = {
    # =====================
    # FRONTIER
    # =====================
    "demo frontier": CommandSpec(
        scenario="frontier",
        demo_mode=True,
        description="Real frontier pipeline with interview-safe bounds",
        confirmation_banner=(
            "FRONTIER PIPELINE — REAL DATA\n"
            "Mode: DEMO (bounded scope, fast execution)\n"
            "Signals, alignment, and evidence are real."
        )
    ),
    "frontier": CommandSpec(
        scenario="frontier",
        demo_mode=False,
        description="Real frontier pipeline, full exhaustive execution",
        confirmation_banner=(
            "FRONTIER PIPELINE — REAL DATA\n"
            "Mode: FULL (exhaustive execution)\n"
            "This may take significant time."
        )
    ),

    # =====================
    # APPLIED
    # =====================
    "demo applied": CommandSpec(
        scenario="applied",
        demo_mode=True,
        description="Applied AI pipeline with bounded demo scope",
        confirmation_banner="APPLIED PIPELINE — REAL DATA (DEMO MODE)"
    ),
    "applied": CommandSpec(
        scenario="applied",
        demo_mode=False,
        description="Applied AI pipeline, full execution",
        confirmation_banner="APPLIED PIPELINE — REAL DATA (FULL MODE)"
    ),

    # =====================
    # INFRA
    # =====================
    "demo infra": CommandSpec(
        scenario="infra",
        demo_mode=True,
        description="AI Infra pipeline, bounded demo scope",
        confirmation_banner="INFRA PIPELINE — REAL DATA (DEMO MODE)"
    ),
    "infra": CommandSpec(
        scenario="infra",
        demo_mode=False,
        description="AI Infra pipeline, full execution",
        confirmation_banner="INFRA PIPELINE — REAL DATA (FULL MODE)"
    ),
}

def resolve_command(command: str) -> CommandSpec:
    if command not in COMMAND_MAP:
        raise ValueError(
            f"Invalid command: '{command}'.\n"
            "Allowed commands are:\n" +
            "\n".join(f"  - {k}" for k in COMMAND_MAP.keys())
        )
    return COMMAND_MAP[command]
