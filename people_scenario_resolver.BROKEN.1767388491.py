from __future__ import annotations
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
AI Talent Engine – People Scenario Resolver
© 2025 L. David Mendoza
"""

import argparse
import sys
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Tuple

import pandas as pd

from contracts.canonical_people_schema import enforce_canonical


REPO_ROOT = Path(__file__).resolve().parent
DEFAULT_PEOPLE_MASTER = REPO_ROOT / "outputs" / "people" / "people_master.csv"
DEFAULT_OUTDIR = REPO_ROOT / "outputs" / "people"

DEFAULT_MIN_ROWS = 25
DEFAULT_MAX_ROWS = 50


def _now_stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")


def _hard_fail(msg: str, code: int = 2) -> None:
    print(f"\nHARD FAILURE:\n{msg}\n")
    sys.exit(code)


def _read_csv_strict(path: Path) -> pd.DataFrame:
    if not path.exists():
        _hard_fail(f"People master missing: {path}")
    df = pd.read_csv(path)
    if df.empty:
        _hard_fail(f"People master empty: {path}")
    return df


def _norm(s: str) -> str:
    return re.sub(r"\s+", " ", str(s or "")).strip().lower()


@dataclass(frozen=True)
class KeywordRule:
    keyword: str
    weight: int
    bucket: str


def _frontier_rules() -> List[KeywordRule]:
    return [
        KeywordRule("cuda", 8, "gpu"),
        KeywordRule("triton", 8, "gpu"),
        KeywordRule("flashattention", 9, "gpu"),
        KeywordRule("vllm", 8, "inference"),
        KeywordRule("tensorrt", 7, "inference"),
        KeywordRule("deepspeed", 6, "train"),
        KeywordRule("fsdp", 6, "train"),
        KeywordRule("openai", 3, "org"),
        KeywordRule("anthropic", 3, "org"),
        KeywordRule("deepmind", 3, "org"),
    ]


def _score(text: str, rules: List[KeywordRule]) -> Tuple[int, Dict[str, int], List[str]]:
    score = 0
    buckets: Dict[str, int] = {}
    hits: List[str] = []
    for r in rules:
        if r.keyword in text:
            score += r.weight
            buckets[r.bucket] = buckets.get(r.bucket, 0) + 1
            hits.append(r.keyword)
    return score, buckets, hits


def resolve_people_scenario(
    scenario: str,
    people_master_path: Path,
    outdir: Path,
    min_rows: int,
    max_rows: int,
) -> Path:

    if scenario != "frontier":
        _hard_fail("Only 'frontier' scenario supported.")

    rules = _frontier_rules()
    df = _read_csv_strict(people_master_path)

    accepted, discards = [], []

    for _, row in df.iterrows():
        text = _norm(" ".join(str(v) for v in row.values))
        score, buckets, hits = _score(text, rules)

        if not hits:
            discards.append(row.to_dict())
            continue

        out = row.to_dict()
        out["Scenario"] = scenario
        out["Scenario_Score"] = score
        out["Scenario_Buckets"] = ",".join(buckets.keys())
        out["Scenario_Keywords"] = ";".join(hits)
        accepted.append(out)

    accepted_df = pd.DataFrame(accepted)
    discards_df = pd.DataFrame(discards)

    if len(accepted_df) < min_rows:
        _hard_fail(f"Accepted rows {len(accepted_df)} < minimum {min_rows}")

    accepted_df = (
        accepted_df
        .sort_values(by="Scenario_Score", ascending=False, kind="mergesort")
        .head(max_rows)
    )

    stamp = _now_stamp()
    outdir.mkdir(parents=True, exist_ok=True)

    people_path = outdir / f"{scenario}_people_{stamp}.csv"
    discards_path = outdir / f"{scenario}_discards_{stamp}.csv"
    status_path = outdir / f"{scenario}_people_status_{stamp}.txt"

    accepted_df.to_csv(people_path, index=False)

    if not discards_df.empty:
        discards_df = enforce_canonical(discards_df)
        discards_df.to_csv(discards_path, index=False)

    status_path.write_text(
        f"scenario={scenario}\n"
        f"accepted={len(accepted_df)}\n"
        f"discarded={len(discards_df)}\n"
        f"people_csv={people_path}\n"
        f"discards_csv={discards_path}\n",
        encoding="utf-8",
    )

    promote_to_people_master(str(out_path))
print("SUCCESS: People scenario resolved")
    print(f"people_csv: {people_path}")

    return people_path


def main(argv: List[str]) -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--scenario", required=True)
    p.add_argument("--people-master", default=str(DEFAULT_PEOPLE_MASTER))
    p.add_argument("--outdir", default=str(DEFAULT_OUTDIR))
    p.add_argument("--min-rows", type=int, default=DEFAULT_MIN_ROWS)
    p.add_argument("--max-rows", type=int, default=DEFAULT_MAX_ROWS)
    args = p.parse_args(argv)

    resolve_people_scenario(
        scenario=args.scenario,
        people_master_path=Path(args.people_master),
        outdir=Path(args.outdir),
        min_rows=args.min_rows,
        max_rows=args.max_rows,
    )


if __name__ == "__main__":
    main(sys.argv[1:])

# ===========================
# CANONICAL CSV PROMOTION
# ===========================
def promote_to_people_master(csv_path: str):
    import os, shutil
    master_dir = os.path.join("outputs", "people")
    os.makedirs(master_dir, exist_ok=True)
    master_path = os.path.join(master_dir, "people_master.csv")
    shutil.copy(csv_path, master_path)
    print(f"✅ Canonical handoff set → {master_path}")

# ============================================================
# CANONICAL CSV PROMOTION (HARD CONTRACT)
# ============================================================

def promote_to_people_master(csv_path: str) -> None:
    """
    Promote a resolved scenario CSV to canonical people_master.csv
    Required for downstream GPT Slim and demo integrity.
    """
    import os, shutil
    master_dir = os.path.join("outputs", "people")
    os.makedirs(master_dir, exist_ok=True)
    master_path = os.path.join(master_dir, "people_master.csv")
    shutil.copy(csv_path, master_path)
    print(f"✅ Canonical handoff set → {master_path}")

