#!/usr/bin/env python3
# ============================================================
# RESEARCH FIRST SOURCER AUTOMATION
# © 2026 L. David Mendoza. All Rights Reserved.
# ============================================================
"""
PHASE 4 — SCENARIO SEED BUILDER (FAIL-CLOSED, DETERMINISTIC)

Purpose
- Create the required scenario seed CSV:
    OUTPUTS/scenario/<role_slug>/<stem>_04_seed.csv
- This enables scenario mode to start Phase 5 without weakening governance.

Non-negotiable rules
- No deletion. Ever.
- No fabrication. Ever.
- Preserve all input columns.
- Ensure Person_ID exists and is stable.
- Fail-closed on empty input or invalid CSV.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import os
from pathlib import Path
from typing import Dict, List, Tuple


CANONICAL_ROOT_NAME = "Research_First_Sourcer_Automation"


ROLE_ALIASES = {
    "frontier": "frontier_ai_research_scientist",
    "frontier_ai_scientist": "frontier_ai_research_scientist",
    "frontier_ai_research_scientist": "frontier_ai_research_scientist",
}


def _fail(msg: str) -> None:
    raise RuntimeError(msg)


def _resolve_role_slug(role_slug: str) -> str:
    if not role_slug:
        _fail("Role slug is required.")
    return ROLE_ALIASES.get(role_slug.strip(), role_slug.strip())


def _repo_root_guard() -> Path:
    cwd = Path.cwd().resolve()
    if cwd.name != CANONICAL_ROOT_NAME:
        _fail(
            "Refusing to run outside canonical repo root.\n"
            f"Expected cwd basename: {CANONICAL_ROOT_NAME}\n"
            f"Actual cwd: {cwd}"
        )
    return cwd


def _read_csv_rows(csv_path: Path) -> Tuple[List[str], List[Dict[str, str]]]:
    if not csv_path.exists():
        _fail(f"Input file not found: {csv_path}")
    if csv_path.suffix.lower() != ".csv":
        _fail(f"Input must be a .csv file: {csv_path}")

    with csv_path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        if not reader.fieldnames:
            _fail(f"Input CSV has no header row: {csv_path}")
        fieldnames = [h.strip() for h in reader.fieldnames]
        rows: List[Dict[str, str]] = []
        for r in reader:
            # Normalize keys exactly to header names
            row = {k.strip(): (v.strip() if isinstance(v, str) else "") for k, v in r.items()}
            rows.append(row)

    if not rows:
        _fail(f"Input CSV has 0 data rows (seed cannot be empty): {csv_path}")

    return fieldnames, rows


def _pick_first_present(row: Dict[str, str], keys: List[str]) -> str:
    for k in keys:
        if k in row and str(row.get(k, "")).strip():
            return str(row.get(k, "")).strip()
    return ""


def _stable_person_id(row: Dict[str, str], row_index_1based: int) -> str:
    """
    Deterministic ID derived from strongest available identity surface.
    Does not require external calls. Does not fabricate.
    """
    seed_material = _pick_first_present(
        row,
        [
            "LinkedIn_Vanity",
            "LinkedIn",
            "LinkedIn_URL",
            "GitHub_URL",
            "Github",
            "GitHub",
            "Email",
            "Work Email",
            "Home Email",
            "Full_Name",
            "Name",
        ],
    )

    if not seed_material:
        # Fall back to row position + any partial name-like fields, still deterministic.
        fallback = f"row:{row_index_1based}|name:{_pick_first_present(row, ['Full_Name','Name'])}"
        seed_material = fallback

    h = hashlib.sha256(seed_material.encode("utf-8")).hexdigest()[:16]
    return f"P{h}"


def _ensure_person_id(fieldnames: List[str], rows: List[Dict[str, str]]) -> List[str]:
    """
    Ensure Person_ID exists.
    If an ID exists under person_id/id, map it into Person_ID without losing original.
    """
    has_person_id = "Person_ID" in fieldnames
    has_lower = any(h in fieldnames for h in ["person_id", "id"])

    if not has_person_id:
        fieldnames = ["Person_ID"] + fieldnames

    for i, r in enumerate(rows, start=1):
        if "Person_ID" in r and str(r.get("Person_ID", "")).strip():
            continue

        mapped = _pick_first_present(r, ["person_id", "id"])
        if mapped:
            r["Person_ID"] = mapped.strip()
        else:
            r["Person_ID"] = _stable_person_id(r, i)

    # Preserve original headers; do not remove id columns if present.
    return fieldnames


def _write_seed(out_path: Path, fieldnames: List[str], rows: List[Dict[str, str]]) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = out_path.with_suffix(out_path.suffix + ".tmp")

    with tmp_path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        for r in rows:
            writer.writerow({h: r.get(h, "") for h in fieldnames})

    tmp_path.replace(out_path)


def main() -> None:
    parser = argparse.ArgumentParser(description="Phase 4 Scenario Seed Builder (deterministic, fail-closed)")
    parser.add_argument("--role", required=True, help="Role slug (e.g., frontier_ai_research_scientist or frontier)")
    parser.add_argument("--input", required=True, help="Source CSV path to normalize into scenario seed")
    args = parser.parse_args()

    _repo_root_guard()

    role_slug = _resolve_role_slug(args.role)
    stem = role_slug  # contract: stem == role_slug in scenario
    in_path = Path(args.input).expanduser().resolve()

    fieldnames, rows = _read_csv_rows(in_path)
    fieldnames = _ensure_person_id(fieldnames, rows)

    out_path = Path("OUTPUTS") / "scenario" / role_slug / f"{stem}_04_seed.csv"
    _write_seed(out_path, fieldnames, rows)

    print("[OK] Phase 4 seed written")
    print(f"Role: {role_slug}")
    print(f"Input: {in_path}")
    print(f"Output: {out_path}")


if __name__ == "__main__":
    main()
