#!/usr/bin/env python3
"""
EXECUTION_CORE/terminal_preview_renderer.py
============================================================
TERMINAL PREVIEW RENDERER — FORMAT LOCKED (RECOVERY MODE)

Maintainer: L. David Mendoza © 2026
Version: v1.1.0 (Format lock-in)

NON-NEGOTIABLE RULES
- This renderer is PRESENTATION-ONLY
- It NEVER computes counts
- It NEVER substitutes unknowns with numeric zeros
- It ALWAYS renders placeholders as: X / <total>

RATIONALE
- 'X / 50' communicates "unknown / not computed"
- '0 / 50' communicates "computed zero" (forbidden in preview)
"""

from typing import List, Tuple


TOTAL_CANDIDATES_DEFAULT = 50


def x_of_n(total: int = TOTAL_CANDIDATES_DEFAULT) -> str:
    """
    Canonical placeholder for preview counts.
    """
    return f"X / {total}"


def render_section(title: str, items: List[str], total: int = TOTAL_CANDIDATES_DEFAULT) -> str:
    lines = []
    lines.append(title)
    lines.append("")
    for label in items:
        lines.append(f"• {label:<45} {x_of_n(total)}")
    return "\n".join(lines)


def render_header(role: str, mode: str, total: int = TOTAL_CANDIDATES_DEFAULT) -> str:
    return (
        "=" * 78 + "\n"
        "AI TALENT INTELLIGENCE PREVIEW\n"
        f"Role: {role}\n"
        f"Mode: {mode}\n"
        f"Candidates Analyzed: {total}\n"
        + "=" * 78
    )


__all__ = [
    "render_header",
    "render_section",
    "x_of_n",
]
