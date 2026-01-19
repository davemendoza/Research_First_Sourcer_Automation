#!/usr/bin/env python3
"""
EXECUTION_CORE/input_row_adapter.py
============================================================
DAY 15 — INPUT ROW ADAPTER (NORMALIZE + OPTIONAL VALIDATE)

PURPOSE
- Normalize raw input rows into canonical, evaluation-safe rows
- Provide an explicit normalize+validate entrypoint (highest standard)
- No IO, no mutation of input objects

THIS FILE:
- IS import-only
- IS deterministic
- IS in-memory only
"""

from __future__ import annotations
from typing import Any, Dict, Mapping

from EXECUTION_CORE.schema_guard import validate_schema


def normalize_row(raw: Mapping[str, Any]) -> Dict[str, Any]:
    """
    Normalize keys and preserve values (truthful sparsity).
    """
    out: Dict[str, Any] = {}
    for k, v in dict(raw).items():
        key = str(k).strip()
        out[key] = v
    return out


def normalize_and_validate_row(raw: Mapping[str, Any]) -> Dict[str, Any]:
    """
    Highest-standard entrypoint:
    - normalize
    - validate schema
    - return canonical row dict
    """
    row = normalize_row(raw)
    validate_schema(row)
    return row


__all__ = ["normalize_row", "normalize_and_validate_row"]
