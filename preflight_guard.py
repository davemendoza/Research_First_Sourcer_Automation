#!/usr/bin/env python3
"""
Universal Preflight Guard v1.0.1
AI Talent Engine – Repo Safety Gate
© 2025 L. David Mendoza

Purpose:
- Hard-stop the pipeline when unsafe artifacts are present in ACTIVE code areas.
- Allow quarantined/backups/venv areas to contain historical debris without blocking execution.

Hard rule:
- If unsafe, DO NOT run pipeline.

Changelog:
- v1.0.1: Ignore quarantine/backups/venv paths for safety checks; only enforce on active repo paths.
"""

from __future__ import annotations

import os
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable, List


@dataclass(frozen=True)
class GuardConfig:
    forbidden_dir_names: tuple[str, ...] = ("__pycache__", ".autogen_backups")
    duplicate_suffix: str = " 2.py"

    # Anything under these prefixes is NOT considered "active code"
    ignore_prefixes: tuple[str, ...] = (
        "_QUARANTINE/",
        "backups/",
        "_QUARANTINE_WRITERS/",
        "deprecated_csv_writers/",
        ".venv/",
        "venv/",
    )


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def repo_root() -> Path:
    # Assumes this script is executed from repo root (Dave’s contract), but we still resolve robustly.
    return Path(__file__).resolve().parent


def to_posix_rel(root: Path, p: Path) -> str:
    try:
        return p.resolve().relative_to(root.resolve()).as_posix()
    except Exception:
        return p.as_posix()


def is_ignored(rel_posix: str, cfg: GuardConfig) -> bool:
    return any(rel_posix.startswith(prefix) for prefix in cfg.ignore_prefixes)


def walk_dirs(root: Path) -> Iterable[Path]:
    # Use rglob, but skip huge ignored trees early for speed.
    for p in root.rglob("*"):
        if p.is_dir():
            yield p


def walk_files(root: Path) -> Iterable[Path]:
    for p in root.rglob("*"):
        if p.is_file():
            yield p


def collect_forbidden_dirs(root: Path, cfg: GuardConfig) -> List[str]:
    hits: List[str] = []
    for d in walk_dirs(root):
        name = d.name
        if name not in cfg.forbidden_dir_names:
            continue
        rel = to_posix_rel(root, d)
        if is_ignored(rel + "/", cfg):  # treat directory as prefix
            continue
        hits.append(rel)
    hits.sort()
    return hits


def collect_duplicate_py(root: Path, cfg: GuardConfig) -> List[str]:
    hits: List[str] = []
    for f in walk_files(root):
        if not f.name.endswith(cfg.duplicate_suffix):
            continue
        rel = to_posix_rel(root, f)
        if is_ignored(rel, cfg):
            continue
        hits.append(rel)
    hits.sort()
    return hits


def fail(msg: str, details: List[str]) -> int:
    print("\n❌ PREFLIGHT GUARD FAILURE")
    print(msg)
    for item in details:
        print(f"  {item}")
    print("\nHard rule: If unsafe, DO NOT run pipeline.")
    return 2


def ok() -> int:
    print("\n✅ PREFLIGHT GUARD PASS")
    print("Safe to proceed.")
    return 0


def main() -> int:
    cfg = GuardConfig()
    root = repo_root()

    print("\nUniversal Preflight Guard v1.0.1")
    print(f"Repo root: {root}")
    print(f"Started: {utc_now_iso()}")
    print("-" * 60)

    forbidden_dirs = collect_forbidden_dirs(root, cfg)
    if forbidden_dirs:
        return fail("Forbidden directories present (active repo paths):", forbidden_dirs)

    dupes = collect_duplicate_py(root, cfg)
    if dupes:
        return fail("Duplicate / autogen artifacts detected (active repo paths):", dupes)

    return ok()


if __name__ == "__main__":
    raise SystemExit(main())
