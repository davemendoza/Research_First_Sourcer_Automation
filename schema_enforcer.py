#!/usr/bin/env python3
"""
AI Talent Engine — Canonical Schema Enforcer (People)
© 2025 L. David Mendoza

Version: v1.3.0

Purpose
- Load canonical People schema from data/talent_schema_inventory.csv
- Support BOTH formats:
  A) single-line CSV header (comma-separated names)
  B) table CSV with a column name field (Column_Name / Field / Name / first column fallback)
- Enforce exact ordering
- Add missing columns as empty strings
- Optionally fail on unexpected extra columns (strict mode)

Changelog
- v1.3.0: Robust schema loader (single-line or table). Adds strict length check and report helper.

Validation
- python3 - <<'PY'
  import pandas as pd
  from schema_enforcer import load_schema_columns, enforce_schema, schema_report
  cols = load_schema_columns("data/talent_schema_inventory.csv")
  print("cols:", len(cols))
  df = pd.DataFrame([{"Person_ID":"x","Full_Name":"y"}])
  df2 = enforce_schema(df, "data/talent_schema_inventory.csv", strict=False)
  print(len(df2.columns))
  print(schema_report(df2))
  PY

Git
- git add schema_enforcer.py
- git commit -m "Harden schema loader/enforcer for canonical 82-column spine (v1.3.0)"
- git push
"""

from __future__ import annotations

from pathlib import Path
from typing import Dict, List, Optional

import pandas as pd


class SchemaViolation(RuntimeError):
    pass


def load_schema_columns(schema_csv: str | Path) -> List[str]:
    schema_csv = Path(schema_csv)
    if not schema_csv.exists():
        raise SchemaViolation(f"Schema file not found: {schema_csv}")

    raw = schema_csv.read_text(encoding="utf-8", errors="replace").strip()
    if not raw:
        raise SchemaViolation(f"Schema file is empty: {schema_csv}")

    # Case A: single-line header list
    first_line = raw.splitlines()[0].strip()
    # If it looks like a header list (lots of commas), treat it as canonical list
    if first_line.count(",") >= 10:
        cols = [c.strip().strip('"').strip("'") for c in first_line.split(",")]
        cols = [c for c in cols if c]
        return cols

    # Case B: table CSV
    df = pd.read_csv(schema_csv)
    if df.empty:
        raise SchemaViolation(f"Schema table is empty: {schema_csv}")

    candidates = ["Column_Name", "column_name", "Field", "field", "Name", "name", "Column", "column"]
    name_col = None
    for c in candidates:
        if c in df.columns:
            name_col = c
            break
    if not name_col:
        name_col = df.columns[0]  # fallback

    cols = [str(x).strip() for x in df[name_col].tolist()]
    cols = [c for c in cols if c and c.lower() != "nan"]
    return cols


def enforce_schema(
    df: pd.DataFrame,
    schema_csv: str | Path,
    strict: bool = True,
) -> pd.DataFrame:
    """
    Enforce canonical schema on a dataframe.

    - Adds missing columns
    - Reorders columns to canonical order
    - If strict=True, fails if df contains any unknown columns
    """
    cols = load_schema_columns(schema_csv)

    if len(cols) != 82:
        raise SchemaViolation(f"FATAL: schema has {len(cols)} columns, expected 82: {schema_csv}")

    df_cols = list(df.columns)
    extras = [c for c in df_cols if c not in cols]
    if strict and extras:
        raise SchemaViolation(f"Schema drift: unexpected columns present: {extras}")

    # Add missing
    for c in cols:
        if c not in df.columns:
            df[c] = ""

    # Drop extras if not strict (keeps pipeline moving but preserves the canonical spine)
    if not strict and extras:
        df = df.drop(columns=extras)

    df = df[cols]

    if len(df.columns) != 82:
        raise SchemaViolation(f"FATAL: enforced df has {len(df.columns)} cols, expected 82")

    return df


def schema_report(df: pd.DataFrame) -> Dict[str, int]:
    """
    Robust counters that do not depend on one exact column spelling.
    Counts rows with ANY email/phone/resume/github.io present.
    """
    def count_any(columns: List[str]) -> int:
        if not columns:
            return 0
        s = df[columns].fillna("").astype(str).agg(" ".join, axis=1).str.strip()
        return int(s.ne("").sum())

    email_cols = [c for c in df.columns if "email" in c.lower()]
    phone_cols = [c for c in df.columns if "phone" in c.lower()]
    resume_cols = [c for c in df.columns if "resume" in c.lower() or c.lower().endswith("_cv") or c.lower() == "cv_url"]
    githubio_cols = [c for c in df.columns if "github_io" in c.lower() or "github.io" in c.lower()]

    return {
        "rows": int(len(df)),
        "email_rows": count_any(email_cols),
        "phone_rows": count_any(phone_cols),
        "resume_rows": count_any(resume_cols),
        "githubio_rows": count_any(githubio_cols),
        "columns": int(len(df.columns)),
    }
