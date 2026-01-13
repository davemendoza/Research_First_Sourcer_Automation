#!/usr/bin/env python3
"""
AI Talent Engine – Canonical Runner
© 2025 L. David Mendoza

USAGE:
  python3 run.py demo <ai_role_type>
  python3 run.py scenario <ai_role_type>
  python3 run.py slim <ai_role_type>
"""

import sys
import json
from pathlib import Path
from datetime import datetime

import pandas as pd

from people_scenario_resolver import run_people


CANONICAL_SCHEMA_PATH = Path("data/talent_schema_inventory.csv")


def load_schema():
    if not CANONICAL_SCHEMA_PATH.exists():
        sys.exit("FATAL: canonical schema not found")
    cols = CANONICAL_SCHEMA_PATH.read_text().strip().split(",")
    if len(cols) != 82:
        sys.exit(f"FATAL: schema has {len(cols)} columns, expected 82")
    return cols


def run_demo_or_scenario(mode: str, role: str):
    schema_cols = load_schema()

    if mode == "demo":
        min_rows, max_rows = 25, 50
    else:
        min_rows, max_rows = 50, 500

    df = run_people(
        scenario=role,
        mode=mode,
        min_rows=min_rows,
        max_rows=max_rows,
        outdir=None
    )

    for col in schema_cols:
        if col not in df.columns:
            df[col] = None

    df = df[schema_cols]

    out_dir = Path("outputs/people")
    out_dir.mkdir(parents=True, exist_ok=True)

    out_csv = out_dir / f"{role}_{mode}.csv"
    df.to_csv(out_csv, index=False)

    return out_csv, len(df)


def run_slim(role: str):
    # Slim is a VIEW, not a schema
    src = Path("outputs/people") / f"{role}_demo.csv"
    if not src.exists():
        sys.exit(f"FATAL: demo file not found for role {role}")

    slim_cols = [
        "Person_ID",
        "Full_Name",
        "AI_Role_Type",
        "Current_Title",
        "Current_Company",
        "Determinative_Skill_Areas",
        "Primary_Model_Families",
        "Inference_Training_Infra_Signals",
        "RLHF_Alignment_Signals",
        "Key_GitHub_AI_Repos",
        "Publication_Count",
        "Citation_Count_Raw",
        "Influence_Tier",
        "GitHub_IO_URL",
    ]

    df = pd.read_csv(src)
    df = df[[c for c in slim_cols if c in df.columns]]

    out_dir = Path("outputs/slim")
    out_dir.mkdir(parents=True, exist_ok=True)

    out_csv = out_dir / f"{role}_slim.csv"
    df.to_csv(out_csv, index=False)

    return out_csv, len(df)


def main():
    if len(sys.argv) != 3:
        sys.exit(__doc__)

    mode = sys.argv[1]
    role = sys.argv[2]

    manifest = {
        "mode": mode,
        "role": role,
        "timestamp_utc": datetime.utcnow().isoformat() + "Z",
    }

    if mode in ("demo", "scenario"):
        out_csv, rows = run_demo_or_scenario(mode, role)
        manifest.update({"rows": rows, "output_csv": str(out_csv)})

    elif mode == "slim":
        out_csv, rows = run_slim(role)
        manifest.update({"rows": rows, "output_csv": str(out_csv)})

    else:
        sys.exit(f"Unknown mode: {mode}")

    Path("outputs").mkdir(exist_ok=True)
    Path("outputs/manifest.json").write_text(
        json.dumps(manifest, indent=2),
        encoding="utf-8"
    )

    print("✅ RUN COMPLETE")
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    raise SystemExit(main())
