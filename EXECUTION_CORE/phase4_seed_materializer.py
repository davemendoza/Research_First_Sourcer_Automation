"""
EXECUTION_CORE/phase4_seed_materializer.py
Creates role-scoped seed CSV for pipeline ingress.

Version: v1.1.0
Author: Dave Mendoza
Copyright (c) 2025-2026 L. David Mendoza. All rights reserved.

Seed contract:
- outputs/seed/<role_slug>.seed.csv
- NO Person_ID
- Must contain at least one anchor per row: GitHub OR Scholar OR Source_URL

Changelog:
- v1.1.0: role slugging, strict source selection, fail-closed, no cross-role fallback.

Validation:
- python3 -m py_compile EXECUTION_CORE/phase4_seed_materializer.py
- python3 -m EXECUTION_CORE.phase4_seed_materializer "AI infra" --debug

Git:
- git add EXECUTION_CORE/phase4_seed_materializer.py
- git commit -m "Fix: seed materializer role-slugged, fail-closed, no Person_ID"
- git push
"""

from __future__ import annotations

import argparse
import csv
import os
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional

from EXECUTION_CORE.ai_role_registry import resolve_role, is_valid_role

SEED_COLUMNS: List[str] = [
    "Primary_Role",
    "Full_Name",
    "GitHub",
    "Scholar",
    "Source_URL",
    "Affiliation",
    "Discovery_Source",
]

_WS = re.compile(r"\s+")
_NON_ALNUM = re.compile(r"[^a-z0-9]+")


def _slug(s: str) -> str:
    s = (s or "").strip().lower()
    s = _NON_ALNUM.sub("_", s)
    s = _WS.sub("_", s)
    s = re.sub(r"_+", "_", s).strip("_")
    return s


def _norm(s: str) -> str:
    return (s or "").strip()


def _pick_first(row: Dict[str, str], candidates: List[str]) -> str:
    for c in candidates:
        if c in row:
            v = _norm(row.get(c, ""))
            if v:
                return v
    return ""


def _has_anchor(mapped: Dict[str, str]) -> bool:
    return bool(_norm(mapped.get("GitHub", "")) or _norm(mapped.get("Scholar", "")) or _norm(mapped.get("Source_URL", "")))


@dataclass(frozen=True)
class SeedResult:
    canonical_role: str
    role_slug: str
    seed_path: str
    source_path: str
    rows_written: int


def _detect(fieldnames: List[str]) -> Dict[str, List[str]]:
    lows = {f: f.lower() for f in fieldnames}

    def find_any(subs: List[str]) -> List[str]:
        return [f for f, fl in lows.items() if any(s in fl for s in subs)]

    return {
        "full_name": find_any(["full_name", "full name", "name"]),
        "github": find_any(["github"]),
        "scholar": find_any(["scholar"]),
        "source_url": find_any(["source_url", "source url", "profile", "homepage", "website", "url"]),
        "affiliation": find_any(["affiliation", "company", "org", "organization", "institution", "lab"]),
        "discovery_source": find_any(["discovery_source", "discovery source", "origin", "source"]),
    }


def create_seed(role_input: str, outputs_root: str = "outputs", debug: bool = False) -> SeedResult:
    canonical = role_input.strip()
    if not is_valid_role(canonical):
        canonical = resolve_role(role_input)
    if not canonical or not is_valid_role(canonical):
        raise ValueError(f"Unknown role: {role_input}")

    role_slug = _slug(canonical)

    out_root = Path(outputs_root)
    demo_src = out_root / "demo" / role_slug / f"demo_{role_slug}.01_people_source.csv"
    if not demo_src.exists():
        raise FileNotFoundError(f"Missing role demo source (fail-closed): {demo_src}")

    seed_dir = out_root / "seed"
    seed_dir.mkdir(parents=True, exist_ok=True)
    seed_path = seed_dir / f"{role_slug}.seed.csv"

    with demo_src.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        fieldnames = list(reader.fieldnames or [])
        if not fieldnames:
            raise RuntimeError(f"No headers: {demo_src}")

        det = _detect(fieldnames)
        if debug:
            print(f"[seed] canonical={canonical}")
            print(f"[seed] slug={role_slug}")
            print(f"[seed] source={demo_src}")
            print(f"[seed] detected={det}")

        out_rows: List[Dict[str, str]] = []
        for row in reader:
            row = {k: (v if v is not None else "") for k, v in row.items()}

            mapped = {
                "Primary_Role": canonical,
                "Full_Name": _pick_first(row, det["full_name"]),
                "GitHub": _pick_first(row, det["github"]),
                "Scholar": _pick_first(row, det["scholar"]),
                "Source_URL": _pick_first(row, det["source_url"]),
                "Affiliation": _pick_first(row, det["affiliation"]),
                "Discovery_Source": _pick_first(row, det["discovery_source"]),
            }

            if not _has_anchor(mapped):
                continue

            out_rows.append({c: _norm(mapped.get(c, "")) for c in SEED_COLUMNS})

    with seed_path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=SEED_COLUMNS, extrasaction="ignore")
        w.writeheader()
        for r in out_rows:
            w.writerow(r)

    return SeedResult(
        canonical_role=canonical,
        role_slug=role_slug,
        seed_path=str(seed_path),
        source_path=str(demo_src),
        rows_written=len(out_rows),
    )


def _cli_main(argv: Optional[List[str]] = None) -> int:
    ap = argparse.ArgumentParser(description="Create role seed (no Person_ID).")
    ap.add_argument("role")
    ap.add_argument("--outputs-root", default="outputs")
    ap.add_argument("--debug", action="store_true")
    args = ap.parse_args(argv)

    try:
        res = create_seed(args.role, outputs_root=args.outputs_root, debug=args.debug)
        print(f"✅ SEED OK role={res.canonical_role} rows={res.rows_written}")
        print(f"seed={res.seed_path}")
        print(f"source={res.source_path}")
        return 0
    except Exception as e:
        print(f"🚫 SEED FAILED: {e}")
        return 1


if __name__ == "__main__":
    raise SystemExit(_cli_main())
