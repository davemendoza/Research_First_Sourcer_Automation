#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
AI Talent Engine - Demo Summary Generator

This module generates a final human-readable summary artifact
from the demo pipeline outputs. It is intentionally conservative,
audit-safe, and ASCII-only to ensure deterministic execution
in interview and live demo environments.

Copyright (c) 2025 L. David Mendoza
All rights reserved.

This software and all associated artifacts are proprietary.
No scraping of restricted sources is performed.
No inferred personal data is generated.
"""

import os
import json
import datetime
import pandas as pd

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(ROOT_DIR, "outputs")
DEMO_DIR = os.path.join(ROOT_DIR, "demo")
META_FILE = os.path.join(DEMO_DIR, "demo_run_meta.json")

APPLIED_FILE = os.path.join(DEMO_DIR, "applied_ai_candidates.csv")
FRONTIER_FILE = os.path.join(DEMO_DIR, "frontier_ai_candidates.csv")

SUMMARY_OUT = os.path.join(DEMO_DIR, "demo_summary.txt")


def safe_read_csv(path: str) -> pd.DataFrame:
    if not os.path.exists(path):
        return pd.DataFrame()
    try:
        return pd.read_csv(path)
    except Exception:
        return pd.DataFrame()


def generate_summary():
    applied_df = safe_read_csv(APPLIED_FILE)
    frontier_df = safe_read_csv(FRONTIER_FILE)

    timestamp = datetime.datetime.utcnow().isoformat() + "Z"

    meta = {}
    if os.path.exists(META_FILE):
        try:
            with open(META_FILE, "r", encoding="utf-8") as f:
                meta = json.load(f)
        except Exception:
            meta = {}

    lines = []
    lines.append("AI TALENT ENGINE - DEMO SUMMARY")
    lines.append("=" * 40)
    lines.append("")
    lines.append(f"Generated (UTC): {timestamp}")
    lines.append("")

    lines.append("Demo Guarantees:")
    lines.append("- Evidence-first evaluation")
    lines.append("- Public-domain sources only")
    lines.append("- No inferred contact data")
    lines.append("- Deterministic, audit-safe execution")
    lines.append("")

    lines.append("Candidate Counts:")
    lines.append(f"- Applied AI candidates: {len(applied_df)}")
    lines.append(f"- Frontier AI candidates: {len(frontier_df)}")
    lines.append("")

    if meta:
        lines.append("Run Metadata:")
        for k, v in meta.items():
            lines.append(f"- {k}: {v}")
        lines.append("")

    lines.append("Interpretation Notes:")
    lines.append(
        "This output reflects conservative role classification, "
        "bounded scoring, and provenance-aware aggregation. "
        "Missing data remains missing by design."
    )

    os.makedirs(DEMO_DIR, exist_ok=True)
    with open(SUMMARY_OUT, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    print("Demo summary written to:", SUMMARY_OUT)


if __name__ == "__main__":
    generate_summary()
