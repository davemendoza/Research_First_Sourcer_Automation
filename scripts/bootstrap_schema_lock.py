#!/usr/bin/env python3
"""
Bootstrapper: writes canonical_people_schema.py without shell paste limits.
"""

from pathlib import Path

TARGET = Path("contracts/canonical_people_schema.py")

SCHEMA_TEXT = r'''
# THIS FILE IS AUTO-GENERATED. DO NOT EDIT MANUALLY.
from __future__ import annotations
from typing import List, Dict
import pandas as pd

CANONICAL_COLUMNS: List[str] = [
    "Person_ID","Role_Type","Public_Email","Public_Phone","Talent_Impact_Percentile",
    "Canonical_Full_Name","First_Name","Last_Name","Name_Source",
    "Identity_Status","Identity_Confidence_Score","Identity_Sources",
    "Seed_Hub_Type","Seed_Hub_URL","Seed_Hub_Evidence_Why",
    "Primary_Role_Family","All_Role_Types",
    "GitHub_Username","GitHub_URL","Key_GitHub_Repos","Key_GitHub_AI_Repos",
    "GitHub_Repo_Evidence_Why","GitHub_Repo_Signal_Type","GitHub_IO_URL",
    "HuggingFace_Username","HuggingFace_Profile_URL",
    "LinkedIn_URL","Personal_Website_URL","Portfolio_URL","Blog_or_Website_URL",
    "Resume_or_CV_URL","Resume_File_Type","Resume_Source",
    "Determinative_Skill_Areas","Benchmarks_Worked_On","Determinative_Signals",
    "Model_Families","Inference_Optimization_Signals","Training_Infra_Signals",
    "RLHF_Alignment_Signals","VectorDB_RAG_Signals",
    "Normalized_Citation_Count","Citations_per_Year",
    "Google_Scholar_URL","Semantic_Scholar_URL","OpenAlex_URL","arXiv_URLs",
    "DBLP_URL","IEEE_Xplore_URL","ResearchGate_URL","ORCID_URL","Patent_URLs",
    "Cross_Lab_Collaboration_Evidence",
    "Conference_Talks_URLs","Keynote_Panelist_Presenter_Signals",
    "Slides_URLs","Video_Talks_URLs",
    "Company_XRay_Source_URLs","Company_XRay_Notes",
    "Public_Footprint_URLs",
    "Public_Email_Source","Public_Phone_Source","LinkedIn_Source",
    "Evidence_Limitations_Notes","Lead_Grade",
    "Row_Validity_Status","Rejection_Reason","Missing_Critical_Fields",
    "Manual_Review_Flag","Field_Level_Provenance",
    "Pipeline_Version","Run_ID","Created_At","Updated_At","Output_File_Path"
]

def canonical_min_columns() -> int:
    return len(CANONICAL_COLUMNS)

def enforce_canonical(df: pd.DataFrame) -> pd.DataFrame:
    for c in CANONICAL_COLUMNS:
        if c not in df.columns:
            df[c] = ""
    extras = [c for c in df.columns if c not in CANONICAL_COLUMNS]
    return df[CANONICAL_COLUMNS + extras]
'''

TARGET.write_text(SCHEMA_TEXT, encoding="utf-8")
print("Wrote canonical_people_schema.py with",
      len(SCHEMA_TEXT.splitlines()), "lines")
