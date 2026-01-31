#!/usr/bin/env python3
# -*- coding: utf-8 -*-

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

"""
tools/fix_headers_eval_module.py

Purpose:
- Enforce the canonical proprietary header across evaluation module files in one pass.
- Targets: evaluation/**/*.py and evaluation/**/*.md
- Creates .bak backups for every modified file.

Safety:
- If a file already starts with the exact canonical header, it is left unchanged.
- If a file has a prior AI Talent Engine header near the top, it is removed and replaced.
- If no recognizable header is found, the canonical header is prepended.

Usage:
- python3 tools/fix_headers_eval_module.py

Exit codes:
- 0 on success
- 1 on error
"""

from __future__ import annotations

import os
import shutil
import sys
from pathlib import Path
from typing import List, Tuple


CANON_HEADER_LINES = [
    "# ==============================================================================",
    "# AI TALENT ENGINE – SIGNAL INTELLIGENCE",
    "# Proprietary and Confidential",
    "# © 2025–2026 L. David Mendoza. All Rights Reserved.",
    "# ==============================================================================",
    "#",
    "# This file contains proprietary intellectual property and trade secrets of",
    "# L. David Mendoza and is part of the AI Talent Engine – Signal Intelligence system.",
    "#",
    "# Unauthorized access, use, copying, modification, distribution, disclosure,",
    "# reverse engineering, or derivative use, in whole or in part, is strictly",
    "# prohibited without prior written authorization.",
    "#",
    "# ==============================================================================",
    "",
]

CANON_HEADER = "\n".join(CANON_HEADER_LINES)

TARGET_EXTS = {".py", ".md"}


def _read_text(p: Path) -> str:
    return p.read_text(encoding="utf-8")


def _write_text(p: Path, s: str) -> None:
    p.write_text(s, encoding="utf-8")


def _looks_like_old_header(top: str) -> bool:
    """
    Detect any prior ATE header variants in the first chunk.
    We intentionally match loosely to catch your earlier incorrect header variants.
    """
    t = top.lower()
    if "ai talent engine" in t and "signal intelligence" in t:
        return True
    if "proprietary" in t and "l. david mendoza" in t:
        return True
    return False


def _strip_existing_header(content: str) -> str:
    """
    Remove an existing header-like comment block at the top if it appears
    to be an AI Talent Engine header.

    Strategy:
    - Look at the first ~120 lines.
    - If it contains ATE header cues, remove everything from the start through the
      last separator line that looks like a long ===== or ==== line (commented or not),
      then remove trailing blank lines.
    - Otherwise, do not strip anything.
    """
    lines = content.splitlines()

    head_n = min(len(lines), 120)
    head = "\n".join(lines[:head_n])

    if not _looks_like_old_header(head):
        return content

    # Identify the last header separator index within the first 120 lines.
    sep_idx = -1
    for i in range(head_n):
        ln = lines[i].strip()
        # Accept commented or plain separators.
        if "====" in ln and len(ln.replace("#", "").strip()) >= 10:
            sep_idx = i

    if sep_idx == -1:
        # If we can't find separators, conservatively strip only the first 30 lines
        # when it clearly matches ATE header cues.
        sep_idx = min(30, len(lines) - 1)

    remainder = "\n".join(lines[sep_idx + 1 :]).lstrip("\n")
    return remainder


def _already_has_canon_header(content: str) -> bool:
    return content.startswith(CANON_HEADER)


def _apply_header(path: Path) -> Tuple[bool, str]:
    original = _read_text(path)

    if _already_has_canon_header(original):
        return (False, "already canonical")

    # Preserve shebang if present
    shebang = ""
    rest = original
    if original.startswith("#!"):
        first_line, _, remainder = original.partition("\n")
        shebang = first_line.strip() + "\n"
        rest = remainder

    stripped = _strip_existing_header(rest).lstrip("\n")
    updated = shebang + CANON_HEADER + stripped

    if updated == original:
        return (False, "no change")
    _write_text(path, updated)
    return (True, "updated")


def _iter_targets(root: Path) -> List[Path]:
    out: List[Path] = []
    for p in root.rglob("*"):
        if p.is_file() and p.suffix.lower() in TARGET_EXTS:
            out.append(p)
    return out


def main() -> int:
    repo_root = Path.cwd()
    eval_root = repo_root / "evaluation"

    if not eval_root.exists() or not eval_root.is_dir():
        print("ERROR: evaluation/ directory not found from current working directory.")
        print(f"Current dir: {repo_root}")
        return 1

    targets = _iter_targets(eval_root)
    if not targets:
        print("No target files found under evaluation/.")
        return 0

    changed = 0
    skipped = 0

    for p in sorted(targets):
        # Backup
        bak = p.with_suffix(p.suffix + ".bak")
        if not bak.exists():
            shutil.copy2(p, bak)

        did_change, reason = _apply_header(p)
        if did_change:
            changed += 1
            print(f"UPDATED  {p}")
        else:
            skipped += 1
            print(f"SKIPPED  {p}  ({reason})")

    print("")
    print(f"Done. Updated: {changed} | Skipped: {skipped}")
    print("Backups: *.bak created alongside each file (first run only).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
