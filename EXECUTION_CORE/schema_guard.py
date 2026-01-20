#!/usr/bin/env python3
"""
EXECUTION_CORE/schema_guard.py
============================================================
DAY 15 — SCHEMA GUARD (FAIL-FAST)

PURPOSE
- Enforce minimal required schema invariants for evaluation
- Fail fast on structurally invalid rows
- Never guess or fabricate missing fields

THIS FILE:
- IS import-only
- IS deterministic
- IS in-memory only

THIS FILE IS NOT:
- NOT a CSV reader
- NOT a writer
- NOT a preview
- NOT a scorer
"""

from __future__ import annotations
from typing import Any, Dict, Iterable, Mapping


# Minimal requirements for evaluation pipeline correctness.
# (We intentionally do NOT require Summary/Experience/etc.)
REQUIRED_FIELDS: Iterable[str] = {
    "Role_Type",
}

# Fields that must be scalar if present (prevents weird list/dict injection)
SCALAR_FIELDS: Iterable[str] = {
    "Role_Type",
    "Person_ID",
}


def validate_schema(row: Mapping[str, Any]) -> None:
    """
    Raise AssertionError if row violates schema invariants.
    """
    assert isinstance(row, Mapping), "Row must be a dict-like mapping"

    missing = [f for f in REQUIRED_FIELDS if f not in row or row.get(f) is None]
    if missing:
        raise AssertionError(f"Missing required fields: {missing}")

    role_type = row.get("Role_Type")
    if not isinstance(role_type, str) or not role_type.strip():
        raise AssertionError("Role_Type must be a non-empty string")

    for f in SCALAR_FIELDS:
        if f in row and row[f] is not None and not isinstance(row[f], (str, int, float)):
            raise AssertionError(f"{f} must be scalar (str/int/float) if present")


__all__ = ["REQUIRED_FIELDS", "SCALAR_FIELDS", "validate_schema"]
