#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EXECUTION_CORE/inventory.py
============================================================
INVENTORY ENTRYPOINT (RECOVERY LOCKDOWN) — FIRST-CLASS ARTIFACT WRITER

Maintainer: L. David Mendoza © 2026
Version: v1.0.0 (Recovery: explicit inventory entrypoint + hard validation)

Purpose
- Regenerate and validate required inventory artifacts in:
    INVENTORY_FINAL/
      - AI_Talent_Inventory_Manifest.json
      - AI_Talent_Repo_Inventory.json
      - AI_Talent_Schema_Inventory.txt

Non-negotiable recovery rules
- Inventory does NOT route through scenario resolution, role parsing, or run_safe pipeline
- No phantom imports
- Deterministic outputs (sorted lists, stable keys)
- Fail closed if any required artifact is missing or empty

This file IS:
- A CLI-executable inventory entrypoint (explicitly)

This file IS NOT:
- NOT a scenario runner
- NOT a demo/scenario dispatcher
- NOT a canonical CSV writer
- NOT a preview tool
- NOT a phase executor

Changelog
- 2026-01-17: Initial recovery-stable inventory entrypoint.

Validation (local)
  cd ~/Desktop/Research_First_Sourcer_Automation
  python3 EXECUTION_CORE/inventory.py
  ls -la INVENTORY_FINAL

Git (SSH)
  git add EXECUTION_CORE/inventory.py
  git commit -m "Recovery: add explicit inventory entrypoint that regenerates required inventory artifacts"
  git push
"""
from __future__ import annotations

import hashlib
import json
import os
import platform
import sys
import time
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Dict, List, Tuple


# ----------------------------
# Paths (deterministic)
# ----------------------------
REPO_ROOT = Path(__file__).resolve().parents[1]
EXECUTION_CORE_DIR = REPO_ROOT / "EXECUTION_CORE"
INVENTORY_DIR = REPO_ROOT / "INVENTORY_FINAL"

REQ_MANIFEST = INVENTORY_DIR / "AI_Talent_Inventory_Manifest.json"
REQ_REPO_INV = INVENTORY_DIR / "AI_Talent_Repo_Inventory.json"
REQ_SCHEMA_TXT = INVENTORY_DIR / "AI_Talent_Schema_Inventory.txt"


# ----------------------------
# Helpers (fail-closed)
# ----------------------------
def die(msg: str) -> None:
    print(f"❌ [INVENTORY] {msg}", file=sys.stderr)
    raise SystemExit(1)


def require(cond: bool, msg: str) -> None:
    if not cond:
        die(msg)


def now_timestamp() -> str:
    # Reuse the same style as run_safe.py timestamps (stable, sortable)
    return time.strftime("%Y%m%d_%H%M%S")


def safe_rel(p: Path) -> str:
    try:
        return str(p.relative_to(REPO_ROOT))
    except Exception:
        return str(p)


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def atomic_write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(text, encoding="utf-8")
    os.replace(str(tmp), str(path))


def atomic_write_json(path: Path, obj: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(obj, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")
    os.replace(str(tmp), str(path))


# ----------------------------
# Inventory indexing (deterministic, reduction-only)
# ----------------------------
SKIP_DIR_NAMES = {
    ".git",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    ".DS_Store",
    "node_modules",
    "dist",
    "build",
    ".venv",
    "venv",
    "ENV",
    "env",
    # Do not index generated outputs as part of repo identity inventory
    "OUTPUTS",
    "outputs",
    "_work",
    "INVENTORY_FINAL",
}


def walk_repo_files(root: Path) -> List[Path]:
    files: List[Path] = []
    for p in root.rglob("*"):
        if any(part in SKIP_DIR_NAMES for part in p.parts):
            continue
        if p.is_file():
            files.append(p)
    files.sort(key=lambda x: str(x).lower())
    return files


def find_schema_candidates(repo_files: List[Path]) -> List[str]:
    """
    Inventory may enumerate candidates, but must not guess the canonical one.
    This keeps wiring verifiable without inventing paths.
    """
    candidates: List[str] = []

    # Strict/explicit canonical schema list file expected by canonical_schema_mapper.py
    schema_list = EXECUTION_CORE_DIR / "CANONICAL_SCHEMA_81_COLUMNS_MACHINE.txt"
    if schema_list.exists():
        candidates.append(safe_rel(schema_list))

    # Additional candidates for human review
    for p in repo_files:
        name = p.name
        if name in {"canonical_people_writer.py", "canonical_schema_mapper.py", "schema_guard.py"}:
            candidates.append(safe_rel(p))
            continue
        if "CANONICAL_SCHEMA_81" in name and p.suffix.lower() in {".txt", ".md"}:
            candidates.append(safe_rel(p))

    # De-dupe + stable order
    uniq = sorted(set(candidates), key=lambda x: x.lower())
    return uniq


@dataclass(frozen=True)
class ArtifactFingerprint:
    path: str
    bytes: int
    sha256: str


def validate_required_artifacts() -> Dict[str, ArtifactFingerprint]:
    required = [REQ_MANIFEST, REQ_REPO_INV, REQ_SCHEMA_TXT]
    for p in required:
        require(p.exists(), f"Required artifact missing: {p}")
        sz = p.stat().st_size
        require(sz > 0, f"Required artifact is empty: {p}")

    fp: Dict[str, ArtifactFingerprint] = {}
    for p in required:
        fp[p.name] = ArtifactFingerprint(
            path=safe_rel(p),
            bytes=p.stat().st_size,
            sha256=sha256_file(p),
        )
    return fp


def build_inventory(repo_files: List[Path]) -> Tuple[dict, dict, str]:
    py_files = [safe_rel(p) for p in repo_files if p.suffix.lower() == ".py"]
    sh_files = [safe_rel(p) for p in repo_files if p.suffix.lower() in {".sh", ".zsh", ".command"}]
    md_files = [safe_rel(p) for p in repo_files if p.suffix.lower() == ".md"]

    py_files.sort(key=str.lower)
    sh_files.sort(key=str.lower)
    md_files.sort(key=str.lower)

    schema_candidates = find_schema_candidates(repo_files)

    repo_inventory = {
        "generated_timestamp": now_timestamp(),
        "repo_root": str(REPO_ROOT),
        "counts": {
            "total_files_indexed": len(repo_files),
            "python_files": len(py_files),
            "shell_files": len(sh_files),
            "markdown_files": len(md_files),
        },
        "python_files": py_files,
        "shell_files": sh_files,
        "markdown_files": md_files,
        "schema_candidates": schema_candidates,
    }

    schema_txt_lines: List[str] = []
    schema_txt_lines.append("AI TALENT ENGINE — SCHEMA INVENTORY (RECOVERY LOCKDOWN)")
    schema_txt_lines.append(f"Generated: {now_timestamp()}")
    schema_txt_lines.append(f"Repo Root: {REPO_ROOT}")
    schema_txt_lines.append("")
    schema_txt_lines.append("Schema-related candidates (paths):")
    if schema_candidates:
        for c in schema_candidates:
            schema_txt_lines.append(f"- {c}")
    else:
        schema_txt_lines.append("- (none found)")
    schema_txt_lines.append("")
    schema_txt_lines.append("Important: this inventory lists candidates only.")
    schema_txt_lines.append("It does not assert a canonical schema beyond what the pipeline already uses.")
    schema_txt = "\n".join(schema_txt_lines) + "\n"

    manifest = {
        "generated_timestamp": now_timestamp(),
        "platform": {
            "python": sys.version.split()[0],
            "python_full": sys.version.replace("\n", " "),
            "os": platform.platform(),
            "machine": platform.machine(),
        },
        "required_artifacts": {
            "AI_Talent_Inventory_Manifest.json": None,
            "AI_Talent_Repo_Inventory.json": None,
            "AI_Talent_Schema_Inventory.txt": None,
        },
    }

    return manifest, repo_inventory, schema_txt


def main() -> int:
    require(REPO_ROOT.exists(), f"Repo root not found: {REPO_ROOT}")
    require(EXECUTION_CORE_DIR.exists(), f"EXECUTION_CORE directory not found: {EXECUTION_CORE_DIR}")

    repo_files = walk_repo_files(REPO_ROOT)

    manifest, repo_inventory, schema_txt = build_inventory(repo_files)

    # Write the two dependency artifacts first
    atomic_write_json(REQ_REPO_INV, repo_inventory)
    atomic_write_text(REQ_SCHEMA_TXT, schema_txt)

    # Write manifest placeholder, then finalize with fingerprints (including itself)
    atomic_write_json(REQ_MANIFEST, manifest)

    fps = validate_required_artifacts()
    manifest["required_artifacts"]["AI_Talent_Repo_Inventory.json"] = asdict(fps["AI_Talent_Repo_Inventory.json"])
    manifest["required_artifacts"]["AI_Talent_Schema_Inventory.txt"] = asdict(fps["AI_Talent_Schema_Inventory.txt"])

    # Re-write manifest so we can fingerprint it last
    atomic_write_json(REQ_MANIFEST, manifest)
    fps = validate_required_artifacts()
    manifest["required_artifacts"]["AI_Talent_Inventory_Manifest.json"] = asdict(fps["AI_Talent_Inventory_Manifest.json"])
    atomic_write_json(REQ_MANIFEST, manifest)

    # Final validation (fail-closed)
    fps = validate_required_artifacts()

    print("✔ [INVENTORY] Regenerated required artifacts:")
    for name in sorted(fps.keys(), key=str.lower):
        a = fps[name]
        print(f"  - {a.path} | bytes={a.bytes} | sha256={a.sha256[:16]}...")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
