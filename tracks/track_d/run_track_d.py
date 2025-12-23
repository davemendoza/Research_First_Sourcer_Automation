# -*- coding: utf-8 -*-
"""
Track D Runner (Inventory-Locked)
(c) 2025 L. David Mendoza. All Rights Reserved.

Version: v1.0.0-trackd-hardreset
Date: 2025-12-22

Track D Contract (ENFORCED):
- Inventory ALWAYS runs first
- ONLY Seed_Hub_Type supported: GitHub_Repo_Contributors
- Missing adapters = HARD FAIL
- Zero-output runs are FORBIDDEN
- Output must be written to: outputs/track_d/people.csv
"""

from __future__ import annotations

import argparse
import csv
import os
import sys
from typing import Any, Dict, List, Optional, Sequence, Set

import pandas as pd

from tracks.track_d.adapter_registry import SEED_HUB_TYPE_TO_ADAPTER, get_adapter_class_for_seed_hub_type


def fatal(msg: str, code: int = 2) -> None:
    print(f"\n[FATAL] {msg}\n", file=sys.stderr)
    raise SystemExit(code)


def info(msg: str) -> None:
    print(f"[INFO] {msg}")


def s(v: Any) -> str:
    if v is None:
        return ""
    try:
        return str(v).strip()
    except Exception:
        return ""


def read_seed_hubs(xlsx: str) -> tuple[list[dict], set[str]]:
    if not os.path.exists(xlsx):
        fatal(f"Seed hub Excel not found: {xlsx}")

    try:
        book = pd.ExcelFile(xlsx, engine="openpyxl")
    except Exception as e:
        fatal(f"Failed to open Excel: {e}")

    rows: list[dict] = []
    discovered: set[str] = set()
    found_col = False

    for sheet in book.sheet_names:
        df = pd.read_excel(book, sheet_name=sheet, dtype=object)
        if df is None or df.empty:
            continue

        norm_cols = {c.lower().replace(" ", "_"): c for c in df.columns}
        if "seed_hub_type" not in norm_cols:
            continue

        found_col = True
        col = norm_cols["seed_hub_type"]

        for _, r in df.iterrows():
            rec = {k: (None if pd.isna(v) else v) for k, v in r.to_dict().items()}
            rec["__sheet__"] = sheet
            val = s(rec.get(col))
            if val:
                rec["Seed_Hub_Type"] = val
                discovered.add(val)
                rows.append(rec)

    if not found_col:
        fatal("No Seed_Hub_Type column found in any worksheet")

    if not discovered:
        fatal("Seed_Hub_Type column exists but no values were found")

    return rows, discovered


def extract_repo_url(row: Dict[str, Any]) -> str:
    for k in [
        "Repo_URL",
        "Repository_URL",
        "GitHub_Repo_URL",
        "URL",
        "Hub_URL",
        "Seed_Hub_URL",
        "Value",
        "Target_URL",
    ]:
        v = s(row.get(k))
        if v:
            return v
    return ""


def write_people_csv(path: str, people: list[dict]) -> None:
    if not people:
        fatal("Refusing to write people.csv with zero rows")

    keys: set[str] = set()
    for p in people:
        keys.update(p.keys())

    fieldnames = sorted(keys)
    os.makedirs(os.path.dirname(path), exist_ok=True)

    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for p in people:
            w.writerow({k: p.get(k, "") for k in fieldnames})


def main(argv: Optional[Sequence[str]] = None) -> int:
    ap = argparse.ArgumentParser("Track D Runner")
    ap.add_argument("--seed-hubs", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--github-token", default=os.environ.get("GITHUB_TOKEN", ""))
    args = ap.parse_args(list(argv) if argv is not None else None)

    target_type = "GitHub_Repo_Contributors"
    out_csv = os.path.join(args.out, "people.csv")

    info("=== TRACK D INVENTORY ===")
    info(f"Seed hubs file: {args.seed_hubs}")
    info(f"Output CSV: {out_csv}")
    info(f"Adapter registry: {list(SEED_HUB_TYPE_TO_ADAPTER.keys())}")

    if target_type not in SEED_HUB_TYPE_TO_ADAPTER:
        fatal(f"Adapter registry missing mapping for {target_type}")

    rows, discovered = read_seed_hubs(args.seed_hubs)
    info(f"Discovered Seed_Hub_Type values: {sorted(discovered)}")

    hubs = [r for r in rows if r["Seed_Hub_Type"] == target_type]
    info(f"Target hubs ({target_type}): {len(hubs)}")

    if not hubs:
        fatal(f"No hubs found for Seed_Hub_Type={target_type}")

    Adapter = get_adapter_class_for_seed_hub_type(target_type)
    adapter = Adapter(github_token=args.github_token)

    people: list[dict] = []
    failures: list[str] = []

    for i, hub in enumerate(hubs, 1):
        repo = extract_repo_url(hub)
        hub_id = s(hub.get("Seed_Hub_ID") or hub.get("Hub_ID") or hub.get("ID") or f"row_{i}")
        info(f"[{i}/{len(hubs)}] Enumerating repo contributors: {repo}")

        try:
            batch = adapter.enumerate_people(hub)
        except Exception as e:
            failures.append(f"{hub_id}: {e}")
            continue

        if not batch:
            failures.append(f"{hub_id}: zero contributors returned")
            continue

        info(f"  -> contributors: {len(batch)}")
        people.extend(batch)

    if failures:
        fatal("One or more hubs failed:\n" + "\n".join(failures))

    if not people:
        fatal("Zero people produced across all hubs")

    write_people_csv(out_csv, people)

    if not os.path.exists(out_csv) or os.path.getsize(out_csv) == 0:
        fatal("people.csv missing or empty after write")

    info("=== TRACK D COMPLETE ===")
    info(f"people.csv written: {out_csv}")
    info(f"total people rows: {len(people)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
