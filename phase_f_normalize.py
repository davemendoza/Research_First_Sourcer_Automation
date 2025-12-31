"""
phase_f_normalize.py
Phase F Normalization (Phase-Next extended wrapper)

This file is a full replacement that preserves legacy behavior and extends it with:
- Lemma/tense normalization
- Title variant resolution hooks

Legacy file:
- phase_f_normalize_legacy.py

Hard rule:
- No silent success. If legacy module cannot be loaded, this fails.

© 2025 L. David Mendoza
Version: v1.1.0-phase-next
Date: 2025-12-23
Changelog:
- Wrapped legacy implementation.
- Added lemma and title resolution hooks.
"""

from __future__ import annotations
import importlib
from typing import Any, Dict
from modules.phase_next.lemma_normalizer import normalize_fields
from modules.phase_next.title_variant_resolver import resolve_title

LEGACY = "phase_f_normalize_legacy"

def _load_legacy():
    return importlib.import_module(LEGACY)

def phase_next_normalize_row(row: Dict[str, Any]) -> Dict[str, Any]:
    out = dict(row or {})
    title = str(out.get("Title") or out.get("Current Title") or "")
    tr = resolve_title(title)
    out["Title_Normalized"] = tr.normalized_title
    out["Title_Canonical_Family"] = tr.canonical_family
    out["Title_Resolution_Confidence"] = tr.confidence

    fields = {
        "Title": title,
        "Summary": str(out.get("Summary") or ""),
        "Skills": str(out.get("Skills") or out.get("Skills2") or ""),
        "Experience": str(out.get("Experience") or ""),
    }
    norms = normalize_fields(fields)
    out["Lemma_Title"] = norms["Title"].normalized
    out["Lemma_Summary"] = norms["Summary"].normalized
    out["Lemma_Skills"] = norms["Skills"].normalized
    out["Lemma_Experience"] = norms["Experience"].normalized
    return out

def main(*args, **kwargs):
    legacy = _load_legacy()
    if not hasattr(legacy, "main"):
        raise RuntimeError("Legacy module missing main()")
    return legacy.main(*args, **kwargs)

