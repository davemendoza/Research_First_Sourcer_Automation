#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EXECUTION_CORE/output_namer.py
============================================================
CANONICAL OUTPUT NAMER (UNIQUE, SORTABLE, NO OVERWRITE)

Maintainer: L. David Mendoza © 2026
Version: v1.1.0

Purpose
- Route canonical outputs into OUTPUTS/<mode>/<role_slug>/
- Produce unique, sortable filenames using timestamp
- Maintain LATEST.csv pointer per role (copy-based, cross-platform)
- Produce per-run metadata JSON path

Filename Format (LOCKED)
<role_slug>__<mode>__schema81__YYYY-MM-DD_HH-MM-SS.csv

Validation
python3 -c "from EXECUTION_CORE.output_namer import build_paths; import pathlib; print(build_paths('frontier_ai_scientist','scenario','2026-01-18_02-00-00',pathlib.Path('.')).canonical_csv)"

Git Commands
git add EXECUTION_CORE/output_namer.py
git commit -m "Add canonical output namer (unique filenames + LATEST pointer)"
git push
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


def slugify(s: str) -> str:
    return (s or "").strip().lower().replace(" ", "_").replace("-", "_")


@dataclass(frozen=True)
class OutputPaths:
    mode: str
    role_slug: str
    out_dir: Path
    canonical_csv: Path
    latest_csv: Path
    metadata_json: Path


def build_paths(prefix: str, mode: str, ts_human: str, repo_root: Path) -> OutputPaths:
    mode = (mode or "").strip().lower()
    if mode not in ("demo", "scenario", "gpt_slim"):
        raise RuntimeError(f"Invalid mode: {mode}. Must be demo, scenario, or gpt_slim.")

    role_slug = slugify(prefix)
    if not role_slug:
        raise RuntimeError("Empty role/prefix for output naming")

    outputs = (repo_root / "OUTPUTS").resolve()
    out_dir = (outputs / mode / role_slug).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    filename = f"{role_slug}__{mode}__schema81__{ts_human}.csv"
    canonical_csv = (out_dir / filename).resolve()

    latest_csv = (out_dir / "LATEST.csv").resolve()
    metadata_json = (out_dir / f"{role_slug}__{mode}__schema81__{ts_human}.metadata.json").resolve()

    return OutputPaths(
        mode=mode,
        role_slug=role_slug,
        out_dir=out_dir,
        canonical_csv=canonical_csv,
        latest_csv=latest_csv,
        metadata_json=metadata_json,
    )


__all__ = ["slugify", "OutputPaths", "build_paths"]
