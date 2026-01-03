#!/usr/bin/env python3
"""
AI Talent Engine — GPT Slim CSV Generator
© 2026 L. David Mendoza

Purpose:
Generate a GPT-optimized, deliberative evaluation CSV derived from the
locked 82-column Canonical People Schema.

Design principles:
- GPT Slim is a reasoning spine, not a convenience subset
- Python performs projection only
- GPT performs judgment, ranking, and hiring recommendation
- Columns are ordered to prevent hallucination, role confusion, and keyword collapse

Output:
Writes <input>_gpt_slim.csv alongside the source file
"""

import sys
import os
import pandas as pd

# ---- GPT SLIM CANONICAL COLUMNS (LOCKED) ----

GPT_SLIM_COLUMNS = [

    # A. Identity & Context (anchors reasoning)
    "Person_ID",
    "Full_Name",
    "Current_Title",
    "Current_Company",
    "Primary_AI_Classification",

    # B. Evidence Authority Spine (non-negotiable)
    "Primary_Evidence_Sources",
    "Evidence_Tier_Summary",
    "Artifact_Coverage",

    # C. Role Calibration (prevents role confusion)
    "Primary_Role_Type",
    "Secondary_Role_Type",
    "Research_vs_Production_Indicator",

    # D. Determinative Skill Signals (the heart)
    "Determinative_Skill_Clusters",
    "Core_Technical_Strengths",
    "Skill_Gaps_or_Weaknesses",

    # E. Model / System Proof (forces substantiation)
    "Primary_Model_Families",
    "Training_or_Alignment_Methods",
    "Systems_or_Retrieval_Architectures",
    "Inference_or_Deployment_Signals",

    # F. Scholarly & Influence Signals (normalizes seniority)
    "Publication_Count",
    "Citation_Velocity",
    "Influence_Tier",

    # G. Leadership & Translation (staff / principal separator)
    "Research_to_Product_Translation_Signal",
    "Technical_Leadership_Signal",
]

GPT_SLIM_COLUMN_COUNT = len(GPT_SLIM_COLUMNS)


def generate_gpt_slim(input_csv: str) -> str:
    if not os.path.exists(input_csv):
        raise FileNotFoundError(f"Input CSV not found: {input_csv}")

    df = pd.read_csv(input_csv)

    # Project columns; create empty fields where absent
    slim_df = pd.DataFrame()
    for col in GPT_SLIM_COLUMNS:
        if col in df.columns:
            slim_df[col] = df[col]
        else:
            slim_df[col] = ""

    output_csv = input_csv.replace(".csv", "_gpt_slim.csv")
    slim_df.to_csv(output_csv, index=False)

    print("✅ GPT Slim CSV generated")
    print(f"Input rows:   {len(df)}")
    print(f"Output rows:  {len(slim_df)}")
    print(f"Columns:      {GPT_SLIM_COLUMN_COUNT}")
    print(f"File:         {output_csv}")

    return output_csv


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: generate_gpt_slim.py <canonical_people.csv>")
        sys.exit(1)

    generate_gpt_slim(sys.argv[1])
