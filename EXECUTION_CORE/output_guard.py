#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EXECUTION_CORE/output_guard.py
============================================================
OUTPUTS ROOT GUARD (FAIL-CLOSED)

Maintainer: L. David Mendoza © 2026
Version: v1.0.1

Purpose
- Enforce that OUTPUTS/ root only contains:
  demo/, scenario/, gpt_slim/, _ARCHIVE_INTERNAL/
- Fail closed if a file exists at OUTPUTS root
- Fail closed if unexpected directory exists at OUTPUTS root

Validation
python3 -c "from EXECUTION_CORE.output_guard import enforce_outputs_root_clean; import pathlib; enforce_outputs_root_clean(pathlib.Path('.')); print('ok')"

Git Commands
git add EXECUTION_CORE/output_guard.py
git commit -m "Add OUTPUTS root guard (fail-closed, contract enforcement)"
git push
"""

from __future__ import annotations

from pathlib import Path
from typing import Set


ALLOWED_OUTPUT_DIRS: Set[str] = {"demo", "scenario", "gpt_slim", "_ARCHIVE_INTERNAL"}


def enforce_outputs_root_clean(repo_root: Path) -> None:
    outputs = (repo_root / "OUTPUTS").resolve()
    if not outputs.exists():
        return

    for item in outputs.iterdir():
        if item.is_file():
            raise RuntimeError(
                f"OUTPUTS root contract violated: file exists at OUTPUTS/: {item.name}\n"
                "Only directories are allowed at OUTPUTS/ root.\n"
                "Run: python3 scripts/lock_outputs_structure.py"
            )
        if item.is_dir() and item.name not in ALLOWED_OUTPUT_DIRS:
            raise RuntimeError(
                f"OUTPUTS root contract violated: unexpected directory at OUTPUTS/: {item.name}\n"
                f"Allowed: {sorted(ALLOWED_OUTPUT_DIRS)}\n"
                "Move it under OUTPUTS/_ARCHIVE_INTERNAL/ or remove it."
            )


__all__ = ["enforce_outputs_root_clean", "ALLOWED_OUTPUT_DIRS"]
