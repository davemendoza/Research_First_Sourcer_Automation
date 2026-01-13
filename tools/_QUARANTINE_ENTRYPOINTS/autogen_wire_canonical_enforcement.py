#!/usr/bin/env python3
"""
Universal Canonical Enforcement Autogen
© 2025 L. David Mendoza

Purpose
-------
Mechanically enforce the Canonical People Schema on *people-output CSV writers only*.

This script:
- Inventories .py files
- Detects people-output CSV writes
- Injects enforce_canonical(df) immediately before the write
- Adds canonical import if missing
- Rewrites FULL FILES ONLY
- Is idempotent (safe to re-run)
- Fails loudly if unsure

Non-Goals
---------
- Does NOT touch non-people CSVs (logs, audits, manifests)
- Does NOT guess dataframe names
- Does NOT partially edit files
- Does NOT modify canonical schema

Contract
--------
- Full-file replacement only
- Anchor-based insertion
- Fail-closed on ambiguity
"""

from __future__ import annotations

import os
import re
import sys
from pathlib import Path
from typing import List, Tuple


REPO_ROOT = Path(__file__).resolve().parents[1]

CANONICAL_IMPORT = "from contracts.canonical_people_schema import enforce_canonical\n"

# Heuristics that indicate a PEOPLE output (world-class conservative defaults)
PEOPLE_OUTPUT_HINTS = [
    "people",
    "person",
    "talent",
    "candidate",
    "frontier",
    "applied_ai",
    "infra",
]

CSV_WRITE_RE = re.compile(r"(\w+)\.to_csv\(")


class PatchResult:
    def __init__(self, path: Path, status: str, reason: str = ""):
        self.path = path
        self.status = status
        self.reason = reason


def is_people_output(path: Path, text: str) -> bool:
    haystack = (str(path).lower() + "\n" + text.lower())
    return any(hint in haystack for hint in PEOPLE_OUTPUT_HINTS)


def patch_file(path: Path) -> PatchResult:
    text = path.read_text(encoding="utf-8")

    if ".to_csv(" not in text:
        return PatchResult(path, "SKIP", "no csv write")

    if not is_people_output(path, text):
        return PatchResult(path, "SKIP", "non-people csv")

    matches = list(CSV_WRITE_RE.finditer(text))
    if len(matches) != 1:
        return PatchResult(path, "FAIL", "ambiguous csv writes")

    df_name = matches[0].group(1)

    if f"{df_name} = enforce_canonical({df_name})" in text:
        return PatchResult(path, "OK", "already enforced")

    lines = text.splitlines(keepends=True)
    out: List[str] = []

    import_added = False
    enforcement_added = False

    for line in lines:
        if not import_added and line.startswith("import") or line.startswith("from"):
            out.append(line)
            continue

        if not import_added:
            out.append(CANONICAL_IMPORT)
            import_added = True

        if ".to_csv(" in line and not enforcement_added:
            out.append(f"{df_name} = enforce_canonical({df_name})\n")
            enforcement_added = True

        out.append(line)

    if not enforcement_added:
        return PatchResult(path, "FAIL", "could not inject enforcement")

    path.write_text("".join(out), encoding="utf-8")
    return PatchResult(path, "PATCHED", "canonical enforced")


def main() -> None:
    results: List[PatchResult] = []

    for py in REPO_ROOT.rglob("*.py"):
        if "tools/autogen_wire_canonical_enforcement.py" in str(py):
            continue
        res = patch_file(py)
        results.append(res)

    print("\n=== Canonical Enforcement Autogen Report ===\n")
    for r in results:
        print(f"{r.status:8} {r.path.relative_to(REPO_ROOT)} {('- ' + r.reason) if r.reason else ''}")

    failures = [r for r in results if r.status == "FAIL"]
    if failures:
        print("\n❌ FAILURES DETECTED. Refusing silent completion.")
        sys.exit(1)

    print("\n✅ Completed. Re-run safe. Enforcement wired where appropriate.\n")


if __name__ == "__main__":
    main()
