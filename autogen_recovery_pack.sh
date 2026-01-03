#!/usr/bin/env bash
set -euo pipefail

# AI Talent Engine — Recovery Pack Autogen
# © 2025 L. David Mendoza
# Version: v1.0.0-recovery-pack
#
# Purpose:
# - Generate hardened preflight + duplicate gate (fail-closed)
# - Generate import-scope lockdown script (idempotent)
# - Generate canonical schema extractor (reads your LOCKED 82 docx)
# - Generate canonical schema JSON (writer-of-record)
#
# Non-negotiables:
# - No interactive editors
# - Full-file generation only (cat heredocs)
# - Fail-closed on ambiguity
#
# Usage:
#   bash autogen_recovery_pack.sh
# Optional:
#   bash autogen_recovery_pack.sh --dry-run

DRY_RUN="0"
if [[ "${1:-}" == "--dry-run" ]]; then
  DRY_RUN="1"
fi

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$REPO_ROOT"

mkdir -p tools schemas _ARCHIVE

echo "============================================"
echo "AI Talent Engine — Recovery Pack Autogen"
echo "Repo: $REPO_ROOT"
echo "Mode: $([[ "$DRY_RUN" == "1" ]] && echo DRY-RUN || echo WRITE)"
echo "============================================"

write_file () {
  local path="$1"
  local tmp="${path}.tmp"

  if [[ "$DRY_RUN" == "1" ]]; then
    echo "[DRY-RUN] would write: $path"
    cat > /dev/null
    return 0
  fi

  mkdir -p "$(dirname "$path")"
  cat > "$tmp"
  mv "$tmp" "$path"
  chmod 644 "$path"
  echo "[WROTE] $path"
}

write_exec () {
  local path="$1"
  local tmp="${path}.tmp"

  if [[ "$DRY_RUN" == "1" ]]; then
    echo "[DRY-RUN] would write executable: $path"
    cat > /dev/null
    return 0
  fi

  mkdir -p "$(dirname "$path")"
  cat > "$tmp"
  mv "$tmp" "$path"
  chmod 755 "$path"
  echo "[WROTE+X] $path"
}

# ------------------------------------------------------------
# 1) Preflight Duplicate Guard (fail-closed)
# ------------------------------------------------------------
write_exec "preflight_duplicate_guard.py" <<'PY'
#!/usr/bin/env python3
"""
AI Talent Engine — Preflight Duplicate Guard (Fail-Closed)
© 2025 L. David Mendoza
Version: v1.0.0-recovery-pack

Purpose
- Detect duplicate Python module basenames within import-visible scope
- Fail closed before any demo/scenario run can proceed
- Produce a clear report of collisions

Rules enforced:
- Inventory first
- No phantom imports
- One writer-of-record
- No duplicate module names in runtime scope
"""

from __future__ import annotations

import argparse
import os
import sys
from collections import defaultdict
from typing import Dict, List, Tuple, Set

DEFAULT_EXCLUDE_DIRS = {
    ".git",
    "__pycache__",
    ".venv",
    "venv",
    "_ARCHIVE",
    "_QUARANTINE",
    "backups",
    "backup",
    "dist",
    "build",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
}

DEFAULT_EXCLUDE_SUFFIXES = (
    " 2.py",
    " copy.py",
)

def discover_py_files(repo_root: str, exclude_dirs: Set[str]) -> List[str]:
    out: List[str] = []
    for root, dirs, files in os.walk(repo_root, topdown=True):
        dirs[:] = [d for d in dirs if d not in exclude_dirs]
        for f in files:
            if not f.endswith(".py"):
                continue
            out.append(os.path.join(root, f))
    out.sort()
    return out

def detect_basename_collisions(py_files: List[str]) -> Dict[str, List[str]]:
    buckets: Dict[str, List[str]] = defaultdict(list)
    for p in py_files:
        base = os.path.basename(p)
        buckets[base].append(p)
    return {k: v for k, v in buckets.items() if len(v) > 1}

def detect_forbidden_suffixes(py_files: List[str], suffixes: Tuple[str, ...]) -> List[str]:
    bad: List[str] = []
    for p in py_files:
        base = os.path.basename(p)
        for s in suffixes:
            if base.endswith(s):
                bad.append(p)
                break
    return sorted(bad)

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo-root", default=os.path.abspath(os.path.dirname(__file__)))
    ap.add_argument("--allow-duplicates", action="store_true", help="Never use in demo. For forensic only.")
    args = ap.parse_args()

    repo_root = os.path.abspath(args.repo_root)

    py_files = discover_py_files(repo_root, DEFAULT_EXCLUDE_DIRS)

    collisions = detect_basename_collisions(py_files)
    bad_suffix = detect_forbidden_suffixes(py_files, DEFAULT_EXCLUDE_SUFFIXES)

    if collisions:
        print("❌ PREFLIGHT FAILURE: Duplicate Python basenames detected (import shadow risk).")
        for base in sorted(collisions.keys()):
            print(f"\n{base}:")
            for p in collisions[base]:
                print(f"  - {p}")
        if not args.allow_duplicates:
            print("\nAction required: quarantine or archive duplicates so only ONE copy remains import-visible.")
            return 2

    if bad_suffix:
        print("\n❌ PREFLIGHT FAILURE: Forbidden duplicate-style filenames detected:")
        for p in bad_suffix:
            print(f"  - {p}")
        if not args.allow_duplicates:
            print("\nAction required: quarantine/archive these files. They must not remain runnable or importable.")
            return 3

    print("✅ PREFLIGHT OK: No duplicate module basenames detected in import-visible scope.")
    print(f"Scanned .py files: {len(py_files)}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
PY

# ------------------------------------------------------------
# 2) Import-Scope Lockdown Script (idempotent)
# ------------------------------------------------------------
write_exec "lockdown_import_scope.sh" <<'SH'
#!/usr/bin/env bash
set -euo pipefail

# AI Talent Engine — Import Scope Lockdown
# © 2025 L. David Mendoza
# Version: v1.0.0-recovery-pack
#
# Purpose:
# - Move non-canonical duplicate-prone directories out of import scope
# - Idempotent: safe to run repeatedly
#
# This script does NOT delete anything.
# It archives into: _ARCHIVE/lockdown_<timestamp>/

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$REPO_ROOT"

TS="$(date +%Y%m%d_%H%M%S)"
DEST="_ARCHIVE/lockdown_${TS}"
mkdir -p "$DEST"

move_if_exists () {
  local p="$1"
  if [[ -e "$p" ]]; then
    echo "[MOVE] $p -> $DEST/"
    mv "$p" "$DEST/"
  else
    echo "[SKIP] $p (not found)"
  fi
}

echo "============================================"
echo "Lockdown import scope"
echo "Repo: $REPO_ROOT"
echo "Archive: $DEST"
echo "============================================"

# High-risk directories commonly containing duplicates/variants
move_if_exists "_QUARANTINE"
move_if_exists "backups"
move_if_exists "backup"
move_if_exists "Phase11"
move_if_exists "modules"
move_if_exists "core"

echo "Done."
echo "Next: run ./preflight_duplicate_guard.py"
SH

# ------------------------------------------------------------
# 3) Canonical Schema Extractor (reads LOCKED 82 docx)
# ------------------------------------------------------------
write_exec "tools/extract_canonical_schema_82.py" <<'PY'
#!/usr/bin/env python3
"""
AI Talent Engine — Canonical People Schema Extractor (LOCKED 82)
© 2025 L. David Mendoza
Version: v1.0.0-recovery-pack

Purpose
- Extract the canonical 82-column schema from the authoritative DOCX
- Write schemas/canonical_people_schema_82.json as writer-of-record
- Avoid manual retyping errors and "82 vs 92" drift forever

Input expectation
- A DOCX named exactly:
  1 AI_Talent_Engine_Canonical_People_Schema_LOCKED_82_DETERMINATIVE_FIRST.docx
  located at repo root (same directory as this script is run from)

If missing, fail closed with explicit instructions.
"""

from __future__ import annotations

import json
import os
import re
import sys
from datetime import datetime, timezone

try:
    from docx import Document
except Exception as e:
    raise RuntimeError(
        "Missing dependency: python-docx is required. Install with: pip3 install python-docx"
    ) from e

DOCX_NAME = "1 AI_Talent_Engine_Canonical_People_Schema_LOCKED_82_DETERMINATIVE_FIRST.docx"
OUT_JSON = os.path.join("schemas", "canonical_people_schema_82.json")

LINE_RE = re.compile(r"^\s*(?P<col>[A-Za-z0-9_]+)\s+—\s+(?P<desc>.+?)\s*$")

def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")

def main() -> int:
    if not os.path.exists(DOCX_NAME):
        raise RuntimeError(
            f"Canonical schema DOCX not found at repo root: {DOCX_NAME}\n"
            f"Action: copy the file into:\n  {os.path.abspath('.')}\n"
            "Then rerun:\n  python3 tools/extract_canonical_schema_82.py"
        )

    doc = Document(DOCX_NAME)
    items = []
    for p in doc.paragraphs:
        t = (p.text or "").strip()
        if not t:
            continue
        m = LINE_RE.match(t)
        if m:
            items.append({"name": m.group("col").strip(), "description": m.group("desc").strip()})

    if len(items) != 82:
        raise RuntimeError(
            "Schema extraction count mismatch.\n"
            f"Extracted: {len(items)} columns\n"
            "Expected: 82 columns\n"
            "This means the DOCX content or dash character format does not match the extractor.\n"
            "Do not proceed until this is resolved."
        )

    os.makedirs(os.path.dirname(OUT_JSON), exist_ok=True)
    payload = {
        "schema_name": "AI Talent Engine – Canonical People Schema (LOCKED, 82 Columns, Determinative-First)",
        "version": "locked-82",
        "created_utc": utc_now(),
        "source_docx": DOCX_NAME,
        "count": 82,
        "columns": items,
    }
    with open(OUT_JSON, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, sort_keys=True)

    print("✅ WROTE:", OUT_JSON)
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
PY

# ------------------------------------------------------------
# 4) Recovery README (authoritative, small)
# ------------------------------------------------------------
write_file "_RECOVERY_README.md" <<'MD'
# AI Talent Engine — Recovery Pack (v1.0.0)

This recovery pack exists to prevent a third incident.

## What it generates
- `preflight_duplicate_guard.py`  
  Fail-closed duplicate module baseline detector (import shadow prevention)

- `lockdown_import_scope.sh`  
  Idempotent isolation of duplicate-prone folders into `_ARCHIVE/`

- `tools/extract_canonical_schema_82.py`  
  Generates `schemas/canonical_people_schema_82.json` from the authoritative DOCX

## Run order (do not reorder)
1) `./preflight_duplicate_guard.py`  
2) `./lockdown_import_scope.sh`  
3) `./preflight_duplicate_guard.py` (must pass)  
4) `python3 tools/extract_canonical_schema_82.py`

## Definition of done
- No duplicate `.py` basenames in import-visible scope
- Canonical schema JSON exists and is count=82
MD

echo "============================================"
echo "Recovery pack generation complete."
echo "Next commands (copy/paste):"
echo "  ./preflight_duplicate_guard.py"
echo "  ./lockdown_import_scope.sh"
echo "  ./preflight_duplicate_guard.py"
echo "  python3 tools/extract_canonical_schema_82.py"
echo "============================================"
