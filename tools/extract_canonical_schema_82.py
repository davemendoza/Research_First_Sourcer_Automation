#!/usr/bin/env python3
"""
AI Talent Engine — Canonical People Schema Extractor (LOCKED 82)
© 2025 L. David Mendoza
Version: v1.0.0-recovery-pack

Purpose
- Extract the canonical 82-column schema from the authoritative DOCX
- Write schemas/canonical_people_schema_82.json as writer-of-record
- Avoid manual retyping errors and "82 vs 92" drift forever

Input expectation
- A DOCX named exactly:
  1 AI_Talent_Engine_Canonical_People_Schema_LOCKED_82_DETERMINATIVE_FIRST.docx
  located at repo root (same directory as this script is run from)

If missing, fail closed with explicit instructions.
"""

from __future__ import annotations

import json
import os
import re
import sys
from datetime import datetime, timezone

try:
    from docx import Document
except Exception as e:
    raise RuntimeError(
        "Missing dependency: python-docx is required. Install with: pip3 install python-docx"
    ) from e

DOCX_NAME = "1 AI_Talent_Engine_Canonical_People_Schema_LOCKED_82_DETERMINATIVE_FIRST.docx"
OUT_JSON = os.path.join("schemas", "canonical_people_schema_82.json")

LINE_RE = re.compile(r"^\s*(?P<col>[A-Za-z0-9_]+)\s+—\s+(?P<desc>.+?)\s*$")

def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")

def main() -> int:
    if not os.path.exists(DOCX_NAME):
        raise RuntimeError(
            f"Canonical schema DOCX not found at repo root: {DOCX_NAME}\n"
            f"Action: copy the file into:\n  {os.path.abspath('.')}\n"
            "Then rerun:\n  python3 tools/extract_canonical_schema_82.py"
        )

    doc = Document(DOCX_NAME)
    items = []
    for p in doc.paragraphs:
        t = (p.text or "").strip()
        if not t:
            continue
        m = LINE_RE.match(t)
        if m:
            items.append({"name": m.group("col").strip(), "description": m.group("desc").strip()})

    if len(items) != 82:
        raise RuntimeError(
            "Schema extraction count mismatch.\n"
            f"Extracted: {len(items)} columns\n"
            "Expected: 82 columns\n"
            "This means the DOCX content or dash character format does not match the extractor.\n"
            "Do not proceed until this is resolved."
        )

    os.makedirs(os.path.dirname(OUT_JSON), exist_ok=True)
    payload = {
        "schema_name": "AI Talent Engine – Canonical People Schema (LOCKED, 82 Columns, Determinative-First)",
        "version": "locked-82",
        "created_utc": utc_now(),
        "source_docx": DOCX_NAME,
        "count": 82,
        "columns": items,
    }
    with open(OUT_JSON, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, sort_keys=True)

    print("✅ WROTE:", OUT_JSON)
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
