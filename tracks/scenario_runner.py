#!/usr/bin/env python3
"""
Scenario Runner – Unified Entry Point
v2.4 | Silent Safe-Fallback
© 2025 L. David Mendoza. All Rights Reserved.

Guarantees:
- One CLI entry point
- Human-proof demo execution
- Zero hard exits unless safety mode fails
- Automatic silent fallback
"""

import argparse
import sys
import hashlib
from pathlib import Path
from datetime import datetime, timezone
import pandas as pd

SCENARIOS = {
    "max_volume_safety": {"top": 500, "min_contrib": 1},
    "frontier_core": {"top": 250, "min_contrib": 10},
    "inference_kernels": {"top": 250, "min_contrib": 8},
    "infra_scaling": {"top": 250, "min_contrib": 8},
}

DEFAULT_INPUT = "outputs/track_e/people_enriched.csv"
OUTPUT_ROOT = Path("outputs/scenarios")

def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()

def run_filter(df, min_contrib, top):
    if "repo_contributions" in df.columns:
        df = df[df["repo_contributions"].fillna(0) >= min_contrib]
    if "github_followers" in df.columns:
        df = df.sort_values("github_followers", ascending=False)
    return df.head(top)

def run_scenario(name, input_path, allow_fallback=True):
    cfg = SCENARIOS[name]
    df = pd.read_csv(input_path)
    result = run_filter(df, cfg["min_contrib"], cfg["top"])

    if result.empty:
        if allow_fallback and name != "max_volume_safety":
            print(f"⚠️ '{name}' returned 0 rows → falling back to safety")
            return run_scenario("max_volume_safety", input_path, allow_fallback=False)

        if name == "max_volume_safety":
            print("❌ Safety mode returned 0 rows — input data unusable")
            sys.exit(1)

    out_dir = OUTPUT_ROOT / name
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{name}.csv"
    result.to_csv(out_path, index=False)

    print("✅ Scenario run complete")
    print(f"Scenario: {name}")
    print(f"Output: {out_dir}")
    print(f"Rows output: {len(result)} | CSV SHA256: {sha256_file(out_path)}")

    return out_path

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--scenario", required=True, choices=SCENARIOS)
    p.add_argument("--input", default=DEFAULT_INPUT)
    args = p.parse_args()

    run_scenario(args.scenario, Path(args.input))

if __name__ == "__main__":
    main()
