"""
phase_g_signal_scoring.py
Phase G Signal Scoring (Phase-Next safe wrapper)

Provides backward-compatible execution while allowing Phase-Next wrappers.
Phase G is non-blocking and must never fail the pipeline due to legacy gaps.

Legacy:
- phase_g_signal_scoring_legacy.py
"""

from __future__ import annotations

import importlib

LEGACY = "phase_g_signal_scoring_legacy"


def _load_legacy():
    return importlib.import_module(LEGACY)


def main(*args, **kwargs):
    """
    Phase G is OPTIONAL.
    If the legacy module does not expose main(), we soft-skip safely.
    """
    legacy = _load_legacy()

    if hasattr(legacy, "main") and callable(legacy.main):
        return legacy.main(*args, **kwargs)

    print("[INFO] Phase G legacy has no main(); skipping Phase G safely")
    return 0
