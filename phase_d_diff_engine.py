"""
phase_d_diff_engine.py
Phase D Diff Engine (Phase-Next extended wrapper)

Adds multi-language diff hooks while preserving legacy behavior.

Legacy:
- phase_d_diff_engine_legacy.py

© 2025 L. David Mendoza
Version: v1.1.0-phase-next
Date: 2025-12-23
"""

from __future__ import annotations
import importlib
from modules.phase_next.multilang_diff import diff_text, detect_language_hint

LEGACY = "phase_d_diff_engine_legacy"

def _load_legacy():
    return importlib.import_module(LEGACY)

def phase_next_diff(old: str, new: str):
    return diff_text(old, new)

def phase_next_lang(text: str) -> str:
    return detect_language_hint(text)

def main(*args, **kwargs):
    legacy = _load_legacy()
    if not hasattr(legacy, "main"):
        raise RuntimeError("Legacy module missing main()")
    return legacy.main(*args, **kwargs)
