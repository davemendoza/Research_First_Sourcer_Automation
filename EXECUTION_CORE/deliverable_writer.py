"""
EXECUTION_CORE/deliverable_writer.py
Writes DELIVERABLE.csv in exact Sample.xlsx schema (81 columns).

Version: v1.0.0
Author: Dave Mendoza
Copyright (c) 2025-2026 L. David Mendoza. All rights reserved.

Validation:
- python3 -m py_compile EXECUTION_CORE/deliverable_writer.py

Git:
- git add EXECUTION_CORE/deliverable_writer.py
- git commit -m "Add: deliverable writer enforcing Sample.xlsx schema"
- git push
"""

from __future__ import annotations

import csv
import os
from typing import Dict, List, Any

SAMPLE_81_COLUMNS: List[str] = [
    "Talent_Rank_Percentile","Full_Name","First_Name","Last_Name","AI_Role_Type","Primary_Email","Primary_Phone",
    "Current_Title","Current_Company","Location_City","Location_State","Location_Country","LinkedIn_Public_URL","Resume_URL",
    "Determinative_Skill_Areas","Benchmarks_Worked_On","Primary_Model_Families","Production_vs_Research_Indicator",
    "GitHub_Repo_Evidence_Why","Repo_Topics_Keywords","GitHub_Username","GitHub_Profile_URL","GitHub_Repo_URLs",
    "GitHub_Repo_Topics","GitHub_Repo_Languages","GitHub_Repo_Stars_Summary","GitHub_IO_URL","GitHub_IO_Evidence_URLs",
    "OSS_Contribution_Signal","OSS_Contribution_Provenance","Scholar_Profile_URL","ORCID_URL","Semantic_Scholar_URL",
    "DBLP_URL","Patents_URLs","Publications_URLs","Top_Papers_URLs","Top_Papers_Titles","Conference_Signal",
    "Conference_Signal_Provenance","Citations_per_Year","Citation_Velocity_3yr","Citation_Velocity_5yr","h_index","i10_index",
    "Influence_Tier","Influence_Tier_Percentile","Cross_Lab_Collaboration_Signal","Identity_Strength_Score",
    "Evidence_Richness_Score","Citation_Provenance","Seed_Source_Type","Seed_Source_URL","Seed_Source_Label","Seed_Query_Or_Handle",
    "Strengths","Weaknesses","Hiring_Recommendation","Role_Fit_Justification","Role_Confidence","Signal_Score",
    "Signal_Score_Rationale","Determinant_Tier","Determinant_Tier_Rationale","Resume_Source","CV_URL","Portfolio_URLs",
    "Personal_Website_URLs","Academic_Homepage_URLs","Blog_URLs","Slides_URLs","Videos_URLs","X_URLs","YouTube_URLs",
    "GPT_Slim_Input_Eligible","GPT_Slim_Rationale","Field_Level_Provenance_JSON","Row_Validity_Status","Pipeline_Version","Output_File_Path",
]

# Synonym map from pipeline outputs to Sample schema
SYNONYMS: Dict[str, List[str]] = {
    "AI_Role_Type": ["Role_Type","Primary_Role","AI_Role_Type"],
    "GitHub_Profile_URL": ["Github_URL","GitHub_Profile_URL","GitHub","Github"],
    "GitHub_IO_URL": ["Github_IO_URL","GitHub_IO_URL"],
    "Primary_Email": ["Email","Primary_Email","Work_Email","Home_Email"],
    "Primary_Phone": ["Phone","Primary_Phone","Mobile_Phone"],
    "Current_Title": ["Title","Current_Title"],
    "Current_Company": ["Company","Current_Company"],
    "Strengths": ["Strengths"],
    "Weaknesses": ["Weaknesses"],
    "Signal_Score": ["Signal_Score"],
}

REQUIRED_FOR_DELIVERABLE = ["Full_Name","AI_Role_Type","Strengths","Weaknesses","Signal_Score"]


def _pick(row: Dict[str, Any], keys: List[str]) -> str:
    for k in keys:
        v = (row.get(k) or "")
        v = str(v).strip()
        if v:
            return v
    return ""


def write_deliverable(input_full_csv: str, deliverable_csv: str, pipeline_version: str) -> None:
    with open(input_full_csv, "r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        in_rows = list(reader)

    out_rows: List[Dict[str, str]] = []
    for r in in_rows:
        out: Dict[str, str] = {c: "" for c in SAMPLE_81_COLUMNS}

        # Direct passthrough if present
        for c in SAMPLE_81_COLUMNS:
            if c in r and str(r.get(c) or "").strip():
                out[c] = str(r.get(c) or "").strip()

        # Synonym fills
        for target, keys in SYNONYMS.items():
            if not out[target]:
                out[target] = _pick(r, keys)

        # Pipeline metadata
        out["Pipeline_Version"] = pipeline_version
        out["Output_File_Path"] = os.path.abspath(deliverable_csv)
        out["Row_Validity_Status"] = "OK"

        # Hard requirements for deliverable quality
        missing = [k for k in REQUIRED_FOR_DELIVERABLE if not out.get(k,"").strip()]
        if missing:
            out["Row_Validity_Status"] = f"FAIL_MISSING_{'_'.join(missing)}"

        out_rows.append(out)

    # Fail closed: no deliverable if every row is invalid
    ok_count = sum(1 for r in out_rows if r["Row_Validity_Status"] == "OK")
    if ok_count == 0:
        raise RuntimeError("DELIVERABLE BLOCKED: no rows met required deliverable fields")

    os.makedirs(os.path.dirname(deliverable_csv) or ".", exist_ok=True)
    with open(deliverable_csv, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=SAMPLE_81_COLUMNS)
        w.writeheader()
        for r in out_rows:
            w.writerow(r)
