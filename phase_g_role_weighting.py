# phase_g_role_weighting.py
# Phase G Role Weighting (Phase-Next safe wrapper)
#
# Adds title variant normalization hooks while preserving legacy behavior.
#
# Legacy:
# - phase_g_role_weighting_legacy.py
#
# © 2025 L. David Mendoza
# Version: v1.1.1-phase-next-safe
# Date: 2025-12-30

from __future__ import annotations

import importlib
from typing import Any, Dict

from modules.phase_next.title_variant_resolver import resolve_title

LEGACY = "phase_g_role_weighting_legacy"

def _load_legacy():
    return importlib.import_module(LEGACY)

def phase_next_title_weight(title: str) -> Dict[str, Any]:
    tr = resolve_title(title or "")
    return {
        "title_normalized": tr.normalized_title,
        "title_family": tr.canonical_family,
        "title_confidence": tr.confidence,
    }

def weight_for_role(*args, **kwargs):
    legacy = _load_legacy()
    if hasattr(legacy, "weight_for_role") and callable(legacy.weight_for_role):
        return legacy.weight_for_role(*args, **kwargs)
    return {}

def main(*args, **kwargs):
    legacy = _load_legacy()
    if hasattr(legacy, "main") and callable(legacy.main):
        return legacy.main(*args, **kwargs)
    print("[INFO] Phase G legacy module has no main(); skipping execution safely")
    return 0
