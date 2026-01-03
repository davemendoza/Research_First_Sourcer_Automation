#!/usr/bin/env python3
"""
AI Talent Engine — Slim Projector (82 -> GPT Slim 24)
© 2025 L. David Mendoza
Version: v1.0.0

Produces a slim CSV with these 24 columns (in order):
- Person_ID
- Full_Name
- AI_Role_Type
- Current_Title
- Current_Company
- Determinative_Skill_Areas
- Benchmarks_Worked_On
- Primary_Model_Families
- Explicit_Model_Names
- Production_vs_Research_Indicator
- Training_or_Alignment_Methods
- RLHF_Alignment_Signals
- Systems_or_Retrieval_Architectures
- Inference_or_Deployment_Signals
- Inference_Training_Infra_Signals
- Key_GitHub_AI_Repos
- GitHub_Repo_Evidence_Why
- Downstream_Adoption_Signal
- Publication_Count
- Citation_Count_Raw
- Citation_Velocity_3yr
- Influence_Tier
- Resume_Link
- GitHub_IO_URL

Mapping is best-effort from existing 82 columns; missing fields remain blank.
"""

from __future__ import annotations
import os
import pandas as pd
from typing import Dict, List

SLIM_COLS: List[str] = [
    "Person_ID",
    "Full_Name",
    "AI_Role_Type",
    "Current_Title",
    "Current_Company",
    "Determinative_Skill_Areas",
    "Benchmarks_Worked_On",
    "Primary_Model_Families",
    "Explicit_Model_Names",
    "Production_vs_Research_Indicator",
    "Training_or_Alignment_Methods",
    "RLHF_Alignment_Signals",
    "Systems_or_Retrieval_Architectures",
    "Inference_or_Deployment_Signals",
    "Inference_Training_Infra_Signals",
    "Key_GitHub_AI_Repos",
    "GitHub_Repo_Evidence_Why",
    "Downstream_Adoption_Signal",
    "Publication_Count",
    "Citation_Count_Raw",
    "Citation_Velocity_3yr",
    "Influence_Tier",
    "Resume_Link",
    "GitHub_IO_URL"
]

# Best-effort mapping keys from the 82 schema.
# If your 82 schema uses different names, projector will still emit blanks (acceptable).
CANDIDATE_MAP: Dict[str, List[str]] = {
    "Person_ID": ["Person_ID"],
    "Full_Name": ["Full_Name", "Name", "FullName"],
    "AI_Role_Type": ["Role_Type", "AI_Role_Type"],
    "Current_Title": ["Current_Title", "Title"],
    "Current_Company": ["Current_Company", "Company"],
    "Resume_Link": ["Resume_Link", "Resume_URL", "CV_URL"],
    "GitHub_IO_URL": ["GitHub_IO_URL", "Github.io", "Github_IO", "GitHubIO"],
    "Key_GitHub_AI_Repos": ["Key_GitHub_AI_Repos", "GitHub_Repos", "Github_Repos"],
}

def _pick(row: pd.Series, candidates: List[str]) -> str:
    for c in candidates:
        if c in row.index:
            v = row.get(c)
            if pd.notna(v):
                s = str(v).strip()
                if s:
                    return s
    return ""

def project_slim(df: pd.DataFrame) -> pd.DataFrame:
    out = []
    for _, row in df.iterrows():
        slim_row = {c: "" for c in SLIM_COLS}
        for slim_col, candidates in CANDIDATE_MAP.items():
            slim_row[slim_col] = _pick(row, candidates)
        out.append(slim_row)
    return pd.DataFrame(out, columns=SLIM_COLS)

def write_slim(in_csv: str, out_csv: str) -> None:
    df = pd.read_csv(in_csv)
    slim = project_slim(df)
    os.makedirs(os.path.dirname(out_csv), exist_ok=True)
    slim.to_csv(out_csv, index=False)
