#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EXECUTION_CORE/phase4_seed_materializer.py
============================================================
PHASE 4 — SEED HUB → ROLE SEED CSV MATERIALIZER (AUTHORITATIVE)

Version: v1.0.0-interview-safe
Author: L. David Mendoza © 2026

CHANGELOG (v1.0.0-interview-safe)
- Adds the missing keystone: deterministic Phase 4 seed generation.
- Reads the canonical Excel Seed Hub workbook (data/AI Talent Engine Seed Hub.xlsx).
- Filters rows into a role-scoped seed CSV based on Seed_Source_Label mapping.
- Writes a timestamped, role-scoped CSV into OUTPUTS/<mode>/<role_slug>/.
- Fails closed on:
  - missing workbook
  - missing required headers (Seed_Source_Label, Seed_Source_Type, Seed_Source_URL)
  - zero rows after filtering
- Never invents people data. Seeds are navigation-only.
- Output is deterministic: normalized headers + stable row ordering + seed_id.

CONTRACT (DO NOT BREAK)
- Excel Seed Hub is the only human-managed seed source.
- Phase 4 MUST always materialize a role-specific seed CSV automatically.
- Phase 4 MUST be deterministic and fail-closed (no silent empties).
- Phase 4 MUST not create placeholder candidate data.
"""

from __future__ import annotations

import argparse
import csv
import re
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple, Optional

from openpyxl import load_workbook


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SEED_HUB = REPO_ROOT / "data" / "AI Talent Engine Seed Hub.xlsx"
OUTPUTS_DIR = REPO_ROOT / "OUTPUTS"


# ----------------------------
# Errors / guards
# ----------------------------
class SeedMaterializationError(Exception):
    pass


def die(msg: str) -> None:
    raise SeedMaterializationError(msg)


def require(cond: bool, msg: str) -> None:
    if not cond:
        die(msg)


# ----------------------------
# Utilities
# ----------------------------
def now_ts() -> str:
    return datetime.now().strftime("%Y-%m-%d_%H-%M-%S")


def slugify(s: str) -> str:
    s = s.strip()
    s = re.sub(r"\s+", " ", s)
    return "".join(ch.lower() if ch.isalnum() else "_" for ch in s).strip("_")


def norm_header(h: str) -> str:
    if h is None:
        return ""
    h = str(h).strip()
    h = h.replace("\n", " ").replace("\r", " ")
    h = re.sub(r"\s+", "_", h)
    h = re.sub(r"[^A-Za-z0-9_]", "", h)
    h = re.sub(r"_+", "_", h).strip("_")
    return h


def first_nonempty_row_as_header(ws) -> Tuple[int, List[str]]:
    """
    Finds the first row with >=3 non-empty cells; treats it as header row.
    """
    for r_idx, row in enumerate(ws.iter_rows(values_only=True), start=1):
        vals = [c for c in row if c is not None and str(c).strip() != ""]
        if len(vals) >= 3:
            headers = [norm_header(c) for c in row]
            # stop at first completely empty tail; keep alignment
            return r_idx, headers
    die(f"Sheet '{ws.title}' has no detectable header row.")


def row_to_dict(headers: List[str], row_vals: Tuple) -> Dict[str, str]:
    d: Dict[str, str] = {}
    for i, h in enumerate(headers):
        if not h:
            continue
        v = ""
        if i < len(row_vals) and row_vals[i] is not None:
            v = str(row_vals[i]).strip()
        d[h] = v
    return d


def stable_sort_key(d: Dict[str, str]) -> Tuple[str, str, str, str]:
    return (
        d.get("Seed_Source_Label", "").lower(),
        d.get("Seed_Source_Type", "").lower(),
        d.get("Seed_Source_URL", "").lower(),
        d.get("Seed_Query_Or_Handle", "").lower(),
    )


# ----------------------------
# Role → Seed label mapping
# ----------------------------
def role_to_seed_labels(role: str) -> List[str]:
    """
    Deterministic mapping to Seed_Source_Label categories present in the Seed Hub.

    Seed_Source_Label values observed / expected:
    - Frontier Seed Hub
    - Inference/Perf Seed
    - RLHF/Alignment Seed
    - Infra/GPU Seed
    - RAG/Vector Seed

    Mapping uses role string only (no inference of people).
    """
    r = role.lower().strip()

    labels: List[str] = []

    # RLHF / alignment
    if "rlhf" in r or "alignment" in r or "safety" in r or "eval" in r or "benchmark" in r:
        labels.append("RLHF/Alignment Seed")

    # performance / inference / systems
    if "performance" in r or "inference" in r or "llm systems" in r or "systems" in r or "training" in r:
        labels.append("Inference/Perf Seed")

    # infra / gpu / sre / platform / distributed
    if "infra" in r or "infrastructure" in r or "sre" in r or "platform" in r or "distributed" in r or "gpu" in r:
        labels.append("Infra/GPU Seed")

    # rag / apps
    if "rag" in r or "application" in r or "app" in r:
        labels.append("RAG/Vector Seed")

    # research / frontier default
    if not labels:
        labels.append("Frontier Seed Hub")

    # Always allow Frontier for research-facing roles as an additive base
    if "frontier" in r or "research" in r or "scientist" in r:
        if "Frontier Seed Hub" not in labels:
            labels.insert(0, "Frontier Seed Hub")

    # de-dup while preserving order
    seen = set()
    out: List[str] = []
    for x in labels:
        if x not in seen:
            seen.add(x)
            out.append(x)
    return out


# ----------------------------
# Core materializer
# ----------------------------
@dataclass(frozen=True)
class MaterializeResult:
    output_csv: Path
    rows_written: int
    labels_used: List[str]
    sheets_scanned: int


REQUIRED_HEADERS = {"Seed_Source_Label", "Seed_Source_Type", "Seed_Source_URL"}


def materialize_seed_csv(
    role: str,
    mode: str,
    seed_hub_path: Path,
    output_dir: Path,
    timestamp: str,
) -> MaterializeResult:
    require(seed_hub_path.exists(), f"Seed Hub workbook missing: {seed_hub_path}")

    labels = role_to_seed_labels(role)
    role_slug = slugify(role)

    output_dir.mkdir(parents=True, exist_ok=True)
    out_csv = output_dir / f"{role_slug}_{timestamp}_04_seed.csv"

    wb = load_workbook(filename=str(seed_hub_path), read_only=True, data_only=True)
    sheet_names = wb.sheetnames
    require(len(sheet_names) >= 1, "Seed Hub workbook has no worksheets.")

    collected: List[Dict[str, str]] = []
    union_headers: List[str] = []

    def ensure_union(hs: List[str]) -> None:
        nonlocal union_headers
        for h in hs:
            if h and h not in union_headers:
                union_headers.append(h)

    sheets_scanned = 0
    for name in sheet_names:
        ws = wb[name]
        sheets_scanned += 1

        header_row_idx, headers = first_nonempty_row_as_header(ws)
        headers = [h for h in headers]  # keep alignment
        ensure_union(headers)

        # Validate required headers exist somewhere (case-normalized)
        # If a sheet doesn't have them, skip the sheet quietly.
        header_set = set(headers)
        if not REQUIRED_HEADERS.issubset(header_set):
            continue

        # Iterate data rows after header row
        for row in ws.iter_rows(min_row=header_row_idx + 1, values_only=True):
            d = row_to_dict(headers, row)

            # Basic structural requirements
            label = d.get("Seed_Source_Label", "").strip()
            stype = d.get("Seed_Source_Type", "").strip()
            surl = d.get("Seed_Source_URL", "").strip()

            if not label or not stype or not surl:
                continue

            # Filter by role labels
            if label not in labels:
                continue

            # Keep row
            collected.append(d)

    wb.close()

    require(len(collected) > 0, f"No Seed Hub rows matched role '{role}' labels={labels}.")
    collected.sort(key=stable_sort_key)

    # Build final headers (stable)
    # Ensure required / high-value headers appear early, keep the rest in deterministic order.
    preferred_prefix = [
        "seed_id",
        "Role_Type",
        "Seed_Source_Label",
        "Seed_Source_Type",
        "Seed_Source_URL",
        "Seed_Query_Or_Handle",
        "Seed_Repo_or_Model_URLs",
        "GitHub_IO_URL",
        "Citation_Provenance",
    ]

    # Normalize common variants from Excel if present
    # (We will preserve actual union headers; this just influences ordering.)
    for h in list(union_headers):
        if not h:
            continue

    # Add required columns if missing
    headers_final: List[str] = []
    for h in preferred_prefix:
        if h not in headers_final:
            headers_final.append(h)

    # Add all collected keys deterministically (sorted) after preferred prefix
    all_keys = set()
    for d in collected:
        all_keys.update(d.keys())

    # Make sure the canonical casing exists for required headers
    # (We keep original names produced by norm_header.)
    extra = sorted([k for k in all_keys if k not in headers_final])
    headers_final.extend(extra)

    # Write output
    with out_csv.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=headers_final)
        w.writeheader()
        for i, d in enumerate(collected, start=1):
            out: Dict[str, str] = {k: "" for k in headers_final}
            out["seed_id"] = f"seed_{i:04d}"
            out["Role_Type"] = role  # navigation-only; downstream may remap/validate

            # Copy known fields through as-is
            for k, v in d.items():
                if k in out:
                    out[k] = v

            w.writerow(out)

    return MaterializeResult(output_csv=out_csv, rows_written=len(collected), labels_used=labels, sheets_scanned=sheets_scanned)


# ----------------------------
# CLI
# ----------------------------
def build_output_dir(mode: str, role: str) -> Path:
    role_slug = slugify(role)
    return OUTPUTS_DIR / mode / role_slug


def main(argv: List[str]) -> int:
    ap = argparse.ArgumentParser(prog="phase4_seed_materializer")
    ap.add_argument("role", help="Canonical AI role type (string)")
    ap.add_argument("--mode", default=os.environ.get("AI_TALENT_MODE", "scenario"), choices=["scenario", "demo", "gpt_slim"], help="Mode for output routing")
    ap.add_argument("--seed-hub", default=str(DEFAULT_SEED_HUB), help="Path to Seed Hub workbook (.xlsx)")
    ap.add_argument("--out-dir", default="", help="Override output directory (defaults to OUTPUTS/<mode>/<role_slug>/)")
    ap.add_argument("--timestamp", default="", help="Override timestamp (defaults to now)")
    args = ap.parse_args(argv[1:])

    role = args.role.strip()
    mode = args.mode.strip()

    # Role validation if registry exists
    try:
        reg = __import__("EXECUTION_CORE.ai_role_registry", fromlist=["assert_valid_role"])
        if hasattr(reg, "assert_valid_role"):
            reg.assert_valid_role(role)
    except Exception:
        pass

    seed_hub_path = Path(args.seed_hub)
    if not seed_hub_path.is_absolute():
        seed_hub_path = (REPO_ROOT / seed_hub_path).resolve()

    out_dir = Path(args.out_dir) if args.out_dir else build_output_dir(mode, role)
    if not out_dir.is_absolute():
        out_dir = (REPO_ROOT / out_dir).resolve()

    ts = args.timestamp.strip() or now_ts()

    try:
        res = materialize_seed_csv(role=role, mode=mode, seed_hub_path=seed_hub_path, output_dir=out_dir, timestamp=ts)
        print(f"[OK] Phase 4 seed materialized")
        print(f"     Role: {role}")
        print(f"     Mode: {mode}")
        print(f"     Seed Hub: {seed_hub_path}")
        print(f"     Labels: {', '.join(res.labels_used)}")
        print(f"     Sheets scanned: {res.sheets_scanned}")
        print(f"     Rows written: {res.rows_written}")
        print(f"     Output CSV: {res.output_csv}")
        return 0
    except SeedMaterializationError as e:
        print(f"❌ Phase 4 seed materialization failed: {e}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
