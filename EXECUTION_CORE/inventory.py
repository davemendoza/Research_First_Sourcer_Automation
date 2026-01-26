"""
EXECUTION_CORE/inventory.py
============================================================
INVENTORY ENTRYPOINT — GOLD STANDARD (HARD-SCOPED, SEALED)

Maintainer: L. David Mendoza © 2026
Purpose:
- Produce exactly THREE inventory artifacts
- Prevent drift, recursion, or historical noise
- NEVER block execution

Artifacts written:
- INVENTORY_FINAL/AI_Talent_Inventory_Manifest.json
- INVENTORY_FINAL/AI_Talent_Repo_Inventory.json
- INVENTORY_FINAL/AI_Talent_Schema_Inventory.txt
"""

from __future__ import annotations

from pathlib import Path
from dataclasses import dataclass, asdict
from typing import Dict, List, Tuple
import hashlib
import json
import os
import platform
import sys
import time

# =============================================================================
# CONSTANTS (SINGLE SOURCE OF TRUTH)
# =============================================================================

REPO_ROOT = Path(__file__).resolve().parents[1]

EXECUTION_CORE_DIR = REPO_ROOT / "EXECUTION_CORE"
INVENTORY_DIR = REPO_ROOT / "INVENTORY_FINAL"

REQ_MANIFEST = INVENTORY_DIR / "AI_Talent_Inventory_Manifest.json"
REQ_REPO_INV = INVENTORY_DIR / "AI_Talent_Repo_Inventory.json"
REQ_SCHEMA_TXT = INVENTORY_DIR / "AI_Talent_Schema_Inventory.txt"

APPROVED_ROOTS = [
    EXECUTION_CORE_DIR,
    REPO_ROOT / "docs",
    REPO_ROOT / "GOVERNANCE",
    REPO_ROOT / "data",
]

# =============================================================================
# HARD FAIL HELPERS
# =============================================================================

def die(msg: str) -> None:
    print(f"❌ [INVENTORY] {msg}", file=sys.stderr)
    raise SystemExit(1)

def require(cond: bool, msg: str) -> None:
    if not cond:
        die(msg)

# =============================================================================
# UTILS
# =============================================================================

def now_timestamp() -> str:
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
    os.replace(tmp, path)

def atomic_write_json(path: Path, obj: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(
        json.dumps(obj, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    os.replace(tmp, path)

# =============================================================================
# INVENTORY (HARD-SCOPED)
# =============================================================================

def walk_repo_files() -> List[Path]:
    files: List[Path] = []

    for root in APPROVED_ROOTS:
        if not root.exists():
            continue
        for p in root.rglob("*"):
            if p.is_file():
                files.append(p)

    files.sort(key=lambda x: str(x).lower())
    return files

def find_schema_candidates(repo_files: List[Path]) -> List[str]:
    candidates: List[str] = []

    canonical = EXECUTION_CORE_DIR / "CANONICAL_SCHEMA_81_COLUMNS_MACHINE.txt"
    if canonical.exists():
        candidates.append(safe_rel(canonical))

    for p in repo_files:
        if p.name in {
            "canonical_people_writer.py",
            "canonical_schema_mapper.py",
            "schema_guard.py",
        }:
            candidates.append(safe_rel(p))

    return sorted(set(candidates), key=str.lower)

@dataclass(frozen=True)
class ArtifactFingerprint:
    path: str
    bytes: int
    sha256: str

def validate_required_artifacts() -> Dict[str, ArtifactFingerprint]:
    required = [REQ_MANIFEST, REQ_REPO_INV, REQ_SCHEMA_TXT]
    out: Dict[str, ArtifactFingerprint] = {}

    for p in required:
        require(p.exists(), f"Missing artifact: {p}")
        size = p.stat().st_size
        require(size > 0, f"Empty artifact: {p}")
        out[p.name] = ArtifactFingerprint(
            path=safe_rel(p),
            bytes=size,
            sha256=sha256_file(p),
        )

    return out

def build_inventory(repo_files: List[Path]) -> Tuple[dict, dict, str]:
    py_files = sorted(
        (safe_rel(p) for p in repo_files if p.suffix == ".py"),
        key=str.lower,
    )

    repo_inventory = {
        "generated_timestamp": now_timestamp(),
        "repo_root": str(REPO_ROOT),
        "counts": {
            "total_files_indexed": len(repo_files),
            "python_files": len(py_files),
        },
        "python_files": py_files,
        "schema_candidates": find_schema_candidates(repo_files),
    }

    schema_lines = [
        "AI TALENT ENGINE — SCHEMA INVENTORY (LOCKED)",
        f"Generated: {now_timestamp()}",
        f"Repo Root: {REPO_ROOT}",
        "",
        "Schema-related candidates:",
    ]

    for c in repo_inventory["schema_candidates"]:
        schema_lines.append(f"- {c}")

    if not repo_inventory["schema_candidates"]:
        schema_lines.append("- (none found)")

    schema_txt = "\n".join(schema_lines) + "\n"

    manifest = {
        "generated_timestamp": now_timestamp(),
        "platform": {
            "python": sys.version.split()[0],
            "os": platform.platform(),
            "machine": platform.machine(),
        },
        "required_artifacts": {},
    }

    return manifest, repo_inventory, schema_txt

# =============================================================================
# MAIN
# =============================================================================

def main() -> int:
    require(EXECUTION_CORE_DIR.exists(), "EXECUTION_CORE missing")

    repo_files = walk_repo_files()
    manifest, repo_inventory, schema_txt = build_inventory(repo_files)

    atomic_write_json(REQ_REPO_INV, repo_inventory)
    atomic_write_text(REQ_SCHEMA_TXT, schema_txt)
    atomic_write_json(REQ_MANIFEST, manifest)

    fps = validate_required_artifacts()
    manifest["required_artifacts"] = {k: asdict(v) for k, v in fps.items()}
    atomic_write_json(REQ_MANIFEST, manifest)

    print("✔ [INVENTORY] Regenerated locked inventory artifacts:")
    for k in sorted(fps):
        v = fps[k]
        print(f"  - {v.path} | bytes={v.bytes} | sha256={v.sha256[:16]}...")

    return 0

if __name__ == "__main__":
    raise SystemExit(main())
