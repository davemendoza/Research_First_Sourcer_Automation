#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CSV Artifact Validator (Fail-Closed)
AI Talent Engine | Research-First Sourcer Automation

This module enforces post-generation CSV integrity.
It is shared by ALL demo and real scenarios.

Blank is allowed.
Fabricated is fatal.
"""

from __future__ import annotations

from pathlib import Path
import re
import pandas as pd


class CSVArtifactViolation(RuntimeError):
    pass


# -------------------------------------------------
# REQUIRED COLUMN PREFIX (HARD ORDER)
# -------------------------------------------------
REQUIRED_PREFIX_COLUMNS = [
    "Person_ID",
    "Full_Name",
    "Role_Type",
    "Email",
    "Phone",
    "LinkedIn_URL",
    "GitHub_URL",
    "GitHub_IO_URL",
    "Google_Scholar_URL",
    "Resume_or_CV_URL",
]


# -------------------------------------------------
# FORBIDDEN PLACEHOLDER FRAGMENTS (CASE-INSENSITIVE)
# -------------------------------------------------
FORBIDDEN_FRAGMENTS = [
    "example.com",
    "github.com/example",
    "email@example",
    "cv available upon request",
    "resume available upon request",
    "555-555",
    "123-456",
    "lorem ipsum",
    "test@test",
]


URL_PATTERN = re.compile(r"^https?://", re.IGNORECASE)


# -------------------------------------------------
# VALIDATION ENTRY POINT
# -------------------------------------------------
def validate_csv_artifact(
    *,
    csv_path: Path,
    mode: str,
    min_rows: int | None,
    max_rows: int | None,
) -> None:
    if not csv_path.exists():
        raise CSVArtifactViolation(
            f"CSV artifact not found: {csv_path}"
        )

    df = pd.read_csv(csv_path)

    # ---- COLUMN ORDER ENFORCEMENT ----
    missing = [c for c in REQUIRED_PREFIX_COLUMNS if c not in df.columns]
    if missing:
        raise CSVArtifactViolation(
            f"CSV missing required columns: {missing}"
        )

    expected_prefix = REQUIRED_PREFIX_COLUMNS
    actual_prefix = list(df.columns[: len(expected_prefix)])

    if actual_prefix != expected_prefix:
        raise CSVArtifactViolation(
            f"CSV column order violation.\n"
            f"Expected prefix: {expected_prefix}\n"
            f"Found prefix:    {actual_prefix}"
        )

    # ---- ROW COUNT ENFORCEMENT ----
    row_count = len(df)

    if min_rows is not None and row_count < min_rows:
        raise CSVArtifactViolation(
            f"CSV row count {row_count} < required minimum {min_rows}"
        )

    if max_rows is not None and row_count > max_rows:
        raise CSVArtifactViolation(
            f"CSV row count {row_count} > allowed maximum {max_rows}"
        )

    # ---- PLACEHOLDER DETECTION ----
    for col in df.columns:
        series = df[col].dropna().astype(str).str.lower()

        for frag in FORBIDDEN_FRAGMENTS:
            if series.str.contains(frag).any():
                raise CSVArtifactViolation(
                    f"Placeholder detected in column '{col}' containing '{frag}'"
                )

    # ---- URL SANITY CHECKS ----
    url_columns = [
        "LinkedIn_URL",
        "GitHub_URL",
        "GitHub_IO_URL",
        "Google_Scholar_URL",
        "Resume_or_CV_URL",
    ]

    for col in url_columns:
        if col not in df.columns:
            continue

        for val in df[col].dropna().astype(str):
            if not URL_PATTERN.match(val):
                raise CSVArtifactViolation(
                    f"Invalid URL format in column '{col}': {val}"
                )

    # ---- MODE-SPECIFIC GUARANTEES ----
    if mode == "demo" and row_count < 25:
        raise CSVArtifactViolation(
            "Demo output must contain at least 25 real people."
        )
