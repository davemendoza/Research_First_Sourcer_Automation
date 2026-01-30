#!/usr/bin/env python3
# ==============================================================================
# AI TALENT ENGINE – SIGNAL INTELLIGENCE
# Proprietary and Confidential
# © 2025–2026 L. David Mendoza. All Rights Reserved.
# ==============================================================================
#
# This file contains proprietary intellectual property and trade secrets of
# L. David Mendoza and is part of the AI Talent Engine – Signal Intelligence system.
#
# Unauthorized access, use, copying, modification, distribution, disclosure,
# reverse engineering, or derivative use, in whole or in part, is strictly
# prohibited without prior written authorization.
#
# ==============================================================================

# -*- coding: utf-8 -*-
"""
EXECUTION_CORE/phase4_seed_materializer.py
============================================================
PHASE 4 — SEED MATERIALIZATION (PROVISIONAL TIERS; DETERMINANTS BUILT LATER)

Version: v4.1.0-phase4-provisional-tier-contract
Maintainer: Dave Mendoza © 2026

PURPOSE
- Materialize a Phase-4 seed CSV from the Seed Hub workbook (MASTER_SEED_HUBS).
- Enforce DEMO behavior: bounded (<=50) and never blocked by Tier scarcity.
- Enforce SCENARIO behavior: strict Tier 1–2 eligibility gate (fail-closed).

CRITICAL CONTRACT (LOCKED)
- Phase 4 tiers are PROVISIONAL at seed time.
- Determinant quality is constructed downstream (Phases 6–7).
- Therefore:
  - DEMO must never hard-fail solely due to missing Tier 1–2 rows.
  - SCENARIO remains strict by design; if Tier 1–2 rows are missing, fail-closed.

SEED HUB LOCATION (AUTO-RESOLVED)
- Preferred: <repo_root>/data/AI Talent Engine Seed Hub.xlsx
- Fallback:  <repo_root>/AI Talent Engine Seed Hub.xlsx

REQUIRED SHEET + COLUMNS
- Sheet: MASTER_SEED_HUBS
- Columns: Seed_Hub_URL, Seed_Hub_Type, Tier, Notes

OUTPUT
- CSV written to output_dir: <role_slug>_04_seed__<timestamp>.csv

CHANGELOG
- v4.1.0
  - Adds robust repo-relative seed hub resolution (data/ first).
  - Keeps scenario strict Tier 1–2.
  - Adds demo deterministic fallback to any-tier (capped 50) when Tier 1–2 missing.
  - Returns both all-tier and used-tier distributions for auditability.

VALIDATION
  python3 -c "from EXECUTION_CORE.phase4_seed_materializer import DEFAULT_SEED_HUB; print(DEFAULT_SEED_HUB)"

GIT (SSH)
  git add EXECUTION_CORE/phase4_seed_materializer.py
  git commit -m "Phase4: provisional tiers; demo fallback; scenario strict; data/ seed hub resolution"
  git push
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

import pandas as pd


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def _resolve_default_seed_hub() -> Path:
    root = _repo_root()
    candidates = [
        root / "data" / "AI Talent Engine Seed Hub.xlsx",
        root / "AI Talent Engine Seed Hub.xlsx",
    ]
    for p in candidates:
        if p.exists():
            return p
    # Fall back to the canonical intended location (data/) for a clear error message.
    return candidates[0]


DEFAULT_SEED_HUB = _resolve_default_seed_hub()


class SeedMaterializationError(RuntimeError):
    pass


def slugify(s: str) -> str:
    return s.strip().lower().replace(" ", "_")


@dataclass(frozen=True)
class SeedMaterializationResult:
    output_csv: Path
    rows_written: int
    tier_distribution: Dict[int, int]        # tiers USED in the emitted CSV
    all_tier_distribution: Dict[int, int]    # tiers present across all usable rows
    role_slug: str
    note: str                                # policy applied


# POLICY
ALLOWED_TIERS_STRICT = {1, 2}
DEMO_MAX_ROWS = 50


def _coerce_int(v) -> Optional[int]:
    try:
        if v is None:
            return None
        if isinstance(v, bool):
            return None
        if isinstance(v, int):
            return int(v)
        s = str(v).strip()
        if not s:
            return None
        # Handles "1.0"
        if "." in s:
            s = s.split(".", 1)[0]
        return int(s)
    except Exception:
        return None


def _load_master_seed_hubs(seed_hub_path: Path) -> pd.DataFrame:
    if not seed_hub_path.exists():
        raise SeedMaterializationError(f"Seed Hub workbook missing: {seed_hub_path}")
    try:
        return pd.read_excel(seed_hub_path, sheet_name="MASTER_SEED_HUBS")
    except Exception as e:
        raise SeedMaterializationError(f"Failed to read MASTER_SEED_HUBS: {e}")


def _build_rows_from_taxonomy(df: pd.DataFrame, role_slug: str, labels: Optional[List[str]]) -> List[Dict[str, object]]:
    required_cols = {"Seed_Hub_URL", "Seed_Hub_Type", "Tier", "Notes"}
    missing = required_cols - set(df.columns)
    if missing:
        raise SeedMaterializationError(f"Seed Hub missing required columns: {sorted(missing)}")

    out: List[Dict[str, object]] = []
    for _, r in df.iterrows():
        url = r.get("Seed_Hub_URL")
        if not isinstance(url, str) or not url.strip():
            continue

        tier_val = _coerce_int(r.get("Tier"))

        out.append(
            {
                "role_slug": role_slug,
                "seed_url": url.strip(),
                "source_type": r.get("Seed_Hub_Type", ""),
                "priority": tier_val if tier_val is not None else "",
                "labels": ",".join(labels) if labels else "",
                "notes": r.get("Notes", ""),
            }
        )
    return out


def _tier_distribution(rows: List[Dict[str, object]]) -> Dict[int, int]:
    dist: Dict[int, int] = {}
    for r in rows:
        t_int = _coerce_int(r.get("priority"))
        if t_int is None:
            continue
        dist[t_int] = dist.get(t_int, 0) + 1
    return dist


def _filter_tiers(rows: List[Dict[str, object]], allowed: set[int]) -> List[Dict[str, object]]:
    filtered: List[Dict[str, object]] = []
    for r in rows:
        t_int = _coerce_int(r.get("priority"))
        if t_int is None:
            continue
        if t_int in allowed:
            filtered.append(r)
    return filtered


def materialize_seed_csv(
    role: str,
    mode: str,
    seed_hub_path: Optional[Path],
    output_dir: Path,
    timestamp: str | None = None,
    labels: List[str] | None = None,
) -> SeedMaterializationResult:

    role_slug = slugify(role)
    ts = timestamp or datetime.now().strftime("%Y%m%d_%H%M%S")

    hub_path = seed_hub_path if seed_hub_path is not None else DEFAULT_SEED_HUB

    df = _load_master_seed_hubs(hub_path)
    all_rows = _build_rows_from_taxonomy(df, role_slug=role_slug, labels=labels)

    if not all_rows:
        raise SeedMaterializationError(
            f"No usable seed rows found in MASTER_SEED_HUBS for role '{role_slug}'. Seed Hub: {hub_path}"
        )

    all_tiers = _tier_distribution(all_rows)

    if mode == "scenario":
        strict_rows = _filter_tiers(all_rows, ALLOWED_TIERS_STRICT)
        if not strict_rows:
            raise SeedMaterializationError(
                f"No Tier-1/2 seed rows produced for role '{role_slug}'. "
                f"This is a SCENARIO strict gate. Determinants are constructed in Phases 6–7; "
                f"either re-tier the Seed Hub or run DEMO for bounded downstream signal construction. "
                f"Seed Hub: {hub_path}"
            )
        final_rows = strict_rows
        note = "scenario_strict_tiers_1_2"
    else:
        strict_rows = _filter_tiers(all_rows, ALLOWED_TIERS_STRICT)
        if strict_rows:
            final_rows = strict_rows[:DEMO_MAX_ROWS]
            note = "demo_preferred_tiers_1_2_capped_50"
        else:
            final_rows = all_rows[:DEMO_MAX_ROWS]
            note = "demo_fallback_any_tier_capped_50"

    if mode == "demo" and len(final_rows) > DEMO_MAX_ROWS:
        raise SeedMaterializationError(f"DEMO cap violated: {len(final_rows)} rows (max {DEMO_MAX_ROWS})")

    output_dir.mkdir(parents=True, exist_ok=True)
    out_csv = output_dir / f"{role_slug}_04_seed__{ts}.csv"
    pd.DataFrame(final_rows).to_csv(out_csv, index=False)

    return SeedMaterializationResult(
        output_csv=out_csv,
        rows_written=len(final_rows),
        tier_distribution=_tier_distribution(final_rows),
        all_tier_distribution=all_tiers,
        role_slug=role_slug,
        note=note,
    )
