"""
phase_e_emergence_detector.py
Phase E Emergence Detector (Phase-Next extended wrapper)

Adds social/community signal ingestion hooks while preserving legacy behavior.

Legacy:
- phase_e_emergence_detector_legacy.py

© 2025 L. David Mendoza
Version: v1.1.0-phase-next
Date: 2025-12-23
"""

from __future__ import annotations
import importlib
from modules.phase_next.social_signal_ingest import ingest as social_ingest, SocialArtifact

LEGACY = "phase_e_emergence_detector_legacy"

def _load_legacy():
    return importlib.import_module(LEGACY)

def phase_next_social_summary(artifacts):
    return social_ingest(artifacts)

def main(*args, **kwargs):
    legacy = _load_legacy()
    if not hasattr(legacy, "main"):
        raise RuntimeError("Legacy module missing main()")
    return legacy.main(*args, **kwargs)
