#!/usr/bin/env python3
"""
AI Talent Engine — Canonical Schema Loader
© 2025 L. David Mendoza
Version: v1.0.0

Loads locked canonical people schema from:
  schemas/canonical_people_schema_82.json

Fail-closed if missing or malformed.
"""
from __future__ import annotations
import json
import os
from typing import List, Dict, Any

SCHEMA_PATH = os.path.join("schemas", "canonical_people_schema_82.json")

class SchemaError(RuntimeError):
    pass

def load_schema() -> Dict[str, Any]:
    if not os.path.exists(SCHEMA_PATH):
        raise SchemaError(
            f"Canonical schema JSON missing: {SCHEMA_PATH}\n"
            "Action: run:\n"
            "  python3 tools/extract_canonical_schema_82.py"
        )
    with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    if data.get("count") != 82 or "columns" not in data:
        raise SchemaError(f"Canonical schema JSON invalid: expected count=82, got {data.get('count')}")
    cols = data["columns"]
    if not isinstance(cols, list) or len(cols) != 82:
        raise SchemaError("Canonical schema JSON 'columns' must be a list of length 82.")
    names = [c.get("name") for c in cols]
    if any((not isinstance(n, str) or not n.strip()) for n in names):
        raise SchemaError("Canonical schema column names must be non-empty strings.")
    if len(set(names)) != 82:
        raise SchemaError("Canonical schema contains duplicate column names.")
    return data

def canonical_column_names() -> List[str]:
    data = load_schema()
    return [c["name"] for c in data["columns"]]
