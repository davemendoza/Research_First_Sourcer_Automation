#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Deterministic output path builder.
One run → one unique timestamped directory.
"""

from dataclasses import dataclass
from pathlib import Path
import time


@dataclass(frozen=True)
class OutputPaths:
    out_dir: Path
    canonical_csv: Path
    metadata_json: Path
    latest_csv: Path
    role_slug: str


def _slugify(s: str) -> str:
    return s.strip().lower().replace(" ", "_")


def build_paths(prefix: str, mode: str, ts_human: str, repo_root: Path) -> OutputPaths:
    """
    Build deterministic, non-overwriting output paths.
    """
    role_slug = _slugify(prefix)

    # ROOT/ROLE/MODE/TIMESTAMP
    out_dir = (
        repo_root
        / "OUTPUTS"
        / role_slug
        / mode
        / ts_human
    )

    canonical_name = f"{role_slug}__{mode}.csv"
    metadata_name = f"{role_slug}__{mode}.meta.json"

    return OutputPaths(
        out_dir=out_dir,
        canonical_csv=out_dir / canonical_name,
        metadata_json=out_dir / metadata_name,
        latest_csv=(
            repo_root
            / "OUTPUTS"
            / role_slug
            / mode
            / "LATEST.csv"
        ),
        role_slug=role_slug,
    )
