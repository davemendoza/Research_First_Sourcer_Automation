"""
AI Talent Engine — Canonical People Schema Contract
Version: v1.0.0-constructive
Author: L. David Mendoza
Purpose:
    Enforce the locked 82-column canonical People schema.
    In constructive mode, missing columns are added as empty.
    Ordering is always enforced.
"""

from typing import List
import pandas as pd

# --- LOCKED CANONICAL COLUMN ORDER (DO NOT EDIT) ---

CANONICAL_COLUMNS: List[str] = [
    "Person_ID",
    "Talent_Rank_Percentile",
    "Full_Name",
    "First_Name",
    "Last_Name",
    "AI_Role_Type",
    "Primary_Email",
    "Primary_Phone",
    "Current_Title",
    "Current_Company",
    "Location_City",
    "Location_State",
    "Location_Country",
    "LinkedIn_Public_URL",
    "Resume_URL",
    "Determinative_Skill_Areas",
    "Benchmarks_Worked_On",
    "Primary_Model_Families",
    "Productions_Research_Indicator",
    "GitHub_Repo_Evidence_Why",
    "Repo_Topics_Keywords",
    "Downstream_Adoption_Signal",
    "Top_Coauthors",
    "Publication_Count",
    "Citation_Count_Raw",
    "Normalized_Citation_Count",
    "Citations_per_Year",
    "Citation_Velocity_3yr",
    "h_index",
    "i10_index",
    "Influence_Tier",
    "Influence_Tier_Percentile",
    "Cross_Lab_Collaboration_Signal",
    "Identity_Strength_Score",
    "Evidence_Richness_Score",
    "Citation_Provenance",
    "Seed_Source_Type",
    "Seed_Source_URL",
    "Seed_Query_or_Handle",
    "Seed_Repo_Model_URLs",
    "GitHub_IO_URL",
    "GitHub_Username",
    "GitHub_URL",
    "Key_GitHub_AI_Repos",
    "GitHub_Repo_Signal_Type",
    "GitHub_Followers",
    "Open_Source_Impact_Notes",
    "Huggingface_Username",
    "Huggingface_Profile_URL",
    "Huggingface_Models_Datasets",
    "Inference_Training_Infra_Signals",
    "RLHF_Alignment_Signals",
    "Company_XRay_Source_URLs",
    "Company_XRay_Notes",
    "Patent_URLs",
    "Patent_Count",
    "Patent_Notes",
    "Google_Scholar_URLs",
    "Semantic_Scholar_URLs",
    "OpenAlex_URLs",
    "ORCID_URLs",
    "arXiv_URLs",
    "Conference_Presentations_URLs",
    "Conference_Names",
    "Resume_Source",
    "CV_URL",
    "Portfolio_URLs",
    "Personal_Website_URLs",
    "Academic_Homepage_URLs",
    "Blog_URLs",
    "Slides_URLs",
    "Videos_URLs",
    "X_URLs",
    "YouTube_URLs",
    "GPT_Slim_Input_Eligible",
    "GPT_Slim_Rationale",
    "Field_Level_Provenance_JSON",
    "Row_Validity_Status",
    "Pipeline_Version"
]

CANONICAL_COLUMN_COUNT = len(CANONICAL_COLUMNS)


# --- CANONICAL ENFORCEMENT ---

def enforce_canonical(df: pd.DataFrame) -> pd.DataFrame:
    """
    Enforce canonical People schema.

    Constructive mode:
        • Missing columns are added as empty strings
        • Column order is enforced
        • Row data is preserved
    """

    if not isinstance(df, pd.DataFrame):
        raise TypeError("enforce_canonical expects a pandas DataFrame")

    # Identify missing columns
    missing = [c for c in CANONICAL_COLUMNS if c not in df.columns]

    # Constructive behavior (Step 2 / Step 3)
    if missing:
        for col in missing:
            df[col] = ""

    # Drop any extra columns not in canonical schema
    df = df[[c for c in CANONICAL_COLUMNS if c in df.columns]]

    # Enforce column order
    df = df.reindex(columns=CANONICAL_COLUMNS)

    # Final sanity check
    if list(df.columns) != CANONICAL_COLUMNS:
        raise RuntimeError("Canonical column ordering failed")

    return df
