#!/usr/bin/env python3
"""
AI Talent Engine - Canonical People Schema (LOCKED 82, Determinative-First)
© 2025 L. David Mendoza

Version: v3.9.0-canonical82-guardrail1
Last updated: 2026-01-02 (UTC)

SOURCE OF TRUTH
- This file is the single source of truth for the ordered canonical people schema.
- Schema evolution is additive-only by policy, but this build locks the canonical set at 82 columns as defined in:
  AI_Talent_Engine_Canonical_People_Schema_LOCKED_82_DETERMINATIVE_FIRST.docx

NON-NEGOTIABLES
- No columns may be renamed, removed, merged, or reordered without explicit human approval.
- All CSV writers must call enforce_canonical(df) immediately before any CSV write.
- This module fails closed on any drift: missing column, extra column, order mismatch, or count mismatch.

Changelog
- v3.9.0-canonical82-guardrail1: Hard-lock CANONICAL_COLUMNS to the 82-field determinative-first order from the locked Word doc.
  Adds CANONICAL_COLUMN_DESCRIPTIONS and a fail-closed enforce_canonical().

Validation
1) python3 -m py_compile contracts/canonical_people_schema.py
2) python3 - <<'PY'
from contracts.canonical_people_schema import CANONICAL_COLUMNS, canonical_column_count
print("canonical_count:", canonical_column_count())
assert canonical_column_count() == 82
print("OK")
PY

Git (SSH)
- git status
- git add contracts/canonical_people_schema.py
- git commit -m "v3.9.0-canonical82-guardrail1: lock canonical people schema to 82 fields and enforce fail-closed"
- git push
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Sequence

import pandas as pd


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
    "Production_vs_Research_Indicator",
    "GitHub_Repo_Evidence_Why",
    "Repo_Topics_Keywords",
    "Downstream_Adoption_Signal",
    "Top_Coauthors",
    "Publication_Count",
    "Citation_Count_Raw",
    "Normalized_Citation_Count",
    "Citations_per_Year",
    "Citation_Velocity_3yr",
    "Citation_Velocity_5yr",
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
    "Seed_Source_Label",
    "Seed_Query_Or_Handle",
    "Seed_Repo_or_Model_URLs",
    "GitHub_IO_URL",
    "GitHub_Username",
    "GitHub_URL",
    "Key_GitHub_AI_Repos",
    "GitHub_Repo_Signal_Type",
    "GitHub_Followers",
    "Open_Source_Impact_Notes",
    "HuggingFace_Username",
    "HuggingFace_Profile_URL",
    "HuggingFace_Models_Datasets",
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
    "Pipeline_Version",
    "Output_File_Path",
]

# Render-only helpers (Word/Excel/GPT mapping). Not a second source of truth.
CANONICAL_COLUMN_DESCRIPTIONS: Dict[str, str] = {
    "Person_ID": "Stable unique identifier for the person across all runs",
    "Talent_Rank_Percentile": "Universal 0–100 rank percentile (role-agnostic)",
    "Full_Name": "Resolved full name (best available)",
    "First_Name": "Parsed first name (nullable)",
    "Last_Name": "Parsed last name (nullable)",
    "AI_Role_Type": "Canonical AI role type classification",
    "Primary_Email": "Publicly published email only (never guessed)",
    "Primary_Phone": "Publicly published phone only (never guessed",
    "Current_Title": "Current or most recent title",
    "Current_Company": "Current or most recent employer",
    "Location_City": "City (normalized when possible)",
    "Location_State": "State/region (normalized when possible)",
    "Location_Country": "Country (normalized when possible)",
    "LinkedIn_Public_URL": "Public LinkedIn URL (if found)",
    "Resume_URL": "Resume link when explicitly published",
    "Determinative_Skill_Areas": "Top determinative skill areas (high confidence)",
    "Benchmarks_Worked_On": "MMLU/HELM/HellaSwag/BIG-bench/Arena/etc.",
    "Primary_Model_Families": "Model families worked with/built (GPT/LLaMA/etc.)",
    "Production_vs_Research_Indicator": "Production, research, or hybrid evidence",
    "GitHub_Repo_Evidence_Why": "Brief rationale tying repo to role fit",
    "Repo_Topics_Keywords": "High-signal repo topics/keywords",
    "Downstream_Adoption_Signal": "Evidence of reuse: forks/stars/citations/users",
    "Top_Coauthors": "Top coauthors list (names/ids)",
    "Publication_Count": "Total publications (best source)",
    "Citation_Count_Raw": "Raw citation count (best source)",
    "Normalized_Citation_Count": "Normalized citation count (cross-source comparable)",
    "Citations_per_Year": "Time-normalized citations",
    "Citation_Velocity_3yr": "Recent velocity (3-year)",
    "Citation_Velocity_5yr": "Recent velocity (5-year)",
    "h_index": "h-index (if available)",
    "i10_index": "i10-index (if available)",
    "Influence_Tier": "Tier label derived from percentile",
    "Influence_Tier_Percentile": "Exact percentile backing the tier",
    "Cross_Lab_Collaboration_Signal": "Cross-org/lab collaboration evidence",
    "Identity_Strength_Score": "0–100 identity strength score",
    "Evidence_Richness_Score": "0–100 evidence richness score",
    "Citation_Provenance": "Which sources contributed to citation metrics",
    "Seed_Source_Type": "Origin surface type used to find the person",
    "Seed_Source_URL": "Exact discovery URL for the lead",
    "Seed_Source_Label": "Human-readable label for the seed surface",
    "Seed_Query_Or_Handle": "Query/handle used to surface the lead",
    "Seed_Repo_or_Model_URLs": "Seed repos/models that led to discovery",
    "GitHub_IO_URL": "GitHub Pages URL candidate (user.github.io)",
    "GitHub_Username": "GitHub handle (primary code anchor)",
    "GitHub_URL": "GitHub profile URL",
    "Key_GitHub_AI_Repos": "Top AI-relevant repo URLs (1–5)",
    "GitHub_Repo_Signal_Type": "Why repo matters (research/infra/applied/etc.)",
    "GitHub_Followers": "GitHub followers count (signal)",
    "Open_Source_Impact_Notes": "Any additional OSS impact notes",
    "HuggingFace_Username": "HF handle (if present)",
    "HuggingFace_Profile_URL": "HF profile URL",
    "HuggingFace_Models_Datasets": "Key HF models/datasets URLs/names",
    "Inference_Training_Infra_Signals": "vLLM/TensorRT/CUDA/Triton/NCCL/etc.",
    "RLHF_Alignment_Signals": "SFT/RM/PPO/DPO/LoRA/QLoRA/etc.",
    "Company_XRay_Source_URLs": "Company research/team/blog author pages scraped",
    "Company_XRay_Notes": "Notes from company public-domain x-ray",
    "Patent_URLs": "Patent URLs (Google Patents/USPTO/WIPO/etc.)",
    "Patent_Count": "Total patents count",
    "Patent_Notes": "Notes about patent relevance/coverage",
    "Google_Scholar_URLs": "Scholar profile URLs",
    "Semantic_Scholar_URLs": "Semantic Scholar author/papers URLs",
    "OpenAlex_URLs": "OpenAlex author/works URLs",
    "ORCID_URLs": "ORCID URLs/IDs",
    "arXiv_URLs": "arXiv paper URLs",
    "Conference_Presentations_URLs": "Talks/slides/videos URLs",
    "Conference_Names": "NeurIPS/ICML/ICLR/etc. names found",
    "Resume_Source": "Surface where resume was found",
    "CV_URL": "CV/Curriculum Vitae link when explicitly published",
    "Portfolio_URLs": "Portfolio links (github.io/personal site/etc.)",
    "Personal_Website_URLs": "Personal website links",
    "Academic_Homepage_URLs": "Academic homepage links",
    "Blog_URLs": "Blog/Substack/Medium author links",
    "Slides_URLs": "Slide deck links",
    "Videos_URLs": "Video/demo links",
    "X_URLs": "X/Twitter profile URLs",
    "YouTube_URLs": "YouTube channel URLs",
    "GPT_Slim_Input_Eligible": "yes|no eligibility for GPT-slim evaluation",
    "GPT_Slim_Rationale": "Why eligible/ineligible; compact rationale",
    "Field_Level_Provenance_JSON": "Per-field provenance map (compact JSON)",
    "Row_Validity_Status": "valid|partial|invalid for downstream gates",
    "Pipeline_Version": "Pipeline version string (locks behavior)",
    "Output_File_Path": "Absolute path to output artifact",
}


def canonical_column_count() -> int:
    return len(CANONICAL_COLUMNS)


@dataclass(frozen=True)
class CanonicalSchemaError(Exception):
    message: str
    details: List[str]

    def __str__(self) -> str:
        if not self.details:
            return self.message
        joined = "\n- " + "\n- ".join(self.details)
        return f"{self.message}{joined}"


def _diff_columns(actual: Sequence[str]) -> List[str]:
    expected = CANONICAL_COLUMNS
    actual_list = list(actual)

    missing = [c for c in expected if c not in actual_list]
    extra = [c for c in actual_list if c not in expected]

    details: List[str] = []
    if missing:
        details.append(f"Missing columns ({len(missing)}): {', '.join(missing)}")
    if extra:
        details.append(f"Extra columns ({len(extra)}): {', '.join(extra)}")

    if not missing and not extra:
        if actual_list != expected:
            mismatches = []
            for i, (a, e) in enumerate(zip(actual_list, expected)):
                if a != e:
                    mismatches.append(f"Index {i}: expected '{e}' but found '{a}'")
                    if len(mismatches) >= 12:
                        break
            details.append("Column order mismatch. First mismatches: " + " | ".join(mismatches))

    if len(actual_list) != len(expected):
        details.append(f"Column count mismatch: expected {len(expected)} but found {len(actual_list)}")

    return details


def enforce_canonical(df: pd.DataFrame) -> pd.DataFrame:
    """
    Fail-closed enforcement for canonical schema.

    Requirements:
    - df must contain exactly the canonical columns
    - df columns must be in the exact canonical order
    - total column count must equal the canonical count (82)

    Returns df unchanged on success.
    Raises CanonicalSchemaError on any drift.
    """
    if not isinstance(df, pd.DataFrame):
        raise TypeError("enforce_canonical expects a pandas.DataFrame")

    details = _diff_columns(df.columns)
    if details:
        raise CanonicalSchemaError(
            message="Canonical People Schema violation. Refusing to write CSV.",
            details=details,
        )

    return df
