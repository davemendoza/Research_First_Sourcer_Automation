"""
AI Talent Engine — Output Generator
Maintainer: L. David Mendoza © 2025
Status: Phase-1 (Enumeration-Validated Output Layer)

Purpose
-------
Generate CSV and Excel outputs ONLY after successful enumeration.

This module is responsible for:
- Writing deterministic CSV and Excel artifacts
- Enforcing column order stability
- Eliminating NaN / null leakage
- Preventing silent field drops
- Emitting a sidecar manifest for auditability

This module MUST NEVER:
- Fabricate data
- Infer missing fields
- Write PASS / FAIL markers into data files
- Execute if enumeration produced zero individuals
"""

import json
import os
from datetime import datetime
from typing import List, Dict, Any

import pandas as pd


# -------------------------------------------------------------------
# Phase-1 Canonical Column Order (Subset, NOT full 81-field schema)
# -------------------------------------------------------------------
PHASE1_COLUMN_ORDER = [
    "Full_Name",
    "Primary_Handle",
    "AI_Role_Type",
    "Role_Confidence",
    "Source_Provenance",
    "GitHub_Profile_URL",
    "GitHub_Repo_URLs",
    "GitHub_Pages_URL",
    "Kaggle_Profile_URL",
    "Kaggle_Notebook_URLs",
    "Google_Scholar_URL",
    "Semantic_Scholar_URL",
    "OpenAlex_URL",
    "Publication_URLs",
    "Patent_URLs",
    "CV_URL",
    "Personal_Website_URL",
    "LinkedIn_URL",
    "Email",
    "Phone",
    "City",
    "State",
    "Country",
    "Citation_Count_3yr",
    "Citation_Count_5yr",
    "Citation_Velocity",
    "Evidence_Summary",
]


# -------------------------------------------------------------------
# Internal Safety Utilities
# -------------------------------------------------------------------
def _normalize_empty(value: Any) -> Any:
    """
    Convert NaN / None / string-null variants into true empty values.
    """
    if value is None:
        return ""
    if isinstance(value, float) and pd.isna(value):
        return ""
    if isinstance(value, str) and value.strip().lower() in {"nan", "none"}:
        return ""
    return value


def _sanitize_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """
    Enforce a no-NaN guarantee across the entire DataFrame.
    """
    return df.applymap(_normalize_empty)


def _assert_no_silent_drops(
    input_records: List[Dict[str, Any]],
    df: pd.DataFrame,
) -> None:
    """
    Abort if any input field disappears during DataFrame construction.
    """
    input_fields = set()
    for record in input_records:
        input_fields.update(record.keys())

    output_fields = set(df.columns)
    dropped_fields = input_fields - output_fields

    if dropped_fields:
        raise RuntimeError(
            "Output generation aborted due to silent field loss. "
            f"Dropped fields: {sorted(dropped_fields)}"
        )


def _order_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Deterministic column ordering:
    1. Phase-1 known columns (in fixed order)
    2. Remaining columns sorted alphabetically
    """
    ordered = [c for c in PHASE1_COLUMN_ORDER if c in df.columns]
    remaining = sorted(c for c in df.columns if c not in ordered)
    return df[ordered + remaining]


# -------------------------------------------------------------------
# Public API
# -------------------------------------------------------------------
def generate_outputs(
    records: List[Dict[str, Any]],
    output_dir: str,
    mode: str,
    run_id: str,
    seed_count: int,
) -> Dict[str, Any]:
    """
    Generate CSV, Excel, and a sidecar manifest.

    Preconditions (ENFORCED):
    - records MUST be non-empty
    - Enumeration MUST have succeeded upstream

    Returns:
    - Metadata dictionary for orchestration / logging layers
      (This function is pipeline-oriented, not script-oriented)
    """

    if not records:
        raise RuntimeError(
            "Output generation aborted: zero records provided. "
            "Enumeration failure must halt execution before this stage."
        )

    os.makedirs(output_dir, exist_ok=True)

    timestamp = datetime.utcnow().strftime("%Y-%m-%d_%H-%M-%S")

    csv_path = os.path.join(
        output_dir, f"AI_Talent_{mode.upper()}_{timestamp}_{run_id}.csv"
    )
    xlsx_path = os.path.join(
        output_dir, f"AI_Talent_{mode.upper()}_{timestamp}_{run_id}.xlsx"
    )
    manifest_path = os.path.join(
        output_dir,
        f"AI_Talent_{mode.upper()}_{timestamp}_{run_id}_manifest.json",
    )

    # Build DataFrame
    df = pd.DataFrame(records)

    # Safety checks
    _assert_no_silent_drops(records, df)
    df = _order_columns(df)
    df = _sanitize_dataframe(df)

    # Final NaN guard
    if df.isna().any().any():
        raise RuntimeError(
            "NaN detected after sanitization. "
            "Output aborted to prevent data corruption."
        )

    # Write outputs
    df.to_csv(csv_path, index=False)
    df.to_excel(xlsx_path, index=False)

    # Sidecar manifest (metadata ONLY, no data duplication)
    manifest = {
        "run_id": run_id,
        "mode": mode,
        "timestamp_utc": timestamp,
        "seed_sources_parsed": seed_count,
        "records_emitted": len(df),
        "column_count": len(df.columns),
        "csv_path": csv_path,
        "excel_path": xlsx_path,
    }

    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)

    # Return metadata for pipeline orchestration, logging, and preview layers
    return {
        "csv": csv_path,
        "excel": xlsx_path,
        "manifest": manifest_path,
        "rows": len(df),
        "columns": list(df.columns),
    }
