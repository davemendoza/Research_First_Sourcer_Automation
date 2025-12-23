"""
phase_f_velocity_analyzer.py
Phase F Velocity (Phase-Next extended wrapper)

Adds deterministic momentum and trajectory hooks while preserving legacy behavior.

Legacy:
- phase_f_velocity_analyzer_legacy.py

© 2025 L. David Mendoza
Version: v1.1.0-phase-next
Date: 2025-12-23
"""

from __future__ import annotations
import importlib
from typing import Dict
from modules.phase_next.momentum_scorer import score as momentum_score
from modules.phase_next.trajectory_engine import forecast as trajectory_forecast

LEGACY = "phase_f_velocity_analyzer_legacy"

def _load_legacy():
    return importlib.import_module(LEGACY)

def phase_next_velocity_features(velocity: float, delta: float) -> Dict[str, float]:
    m = momentum_score({"velocity": velocity, "delta": delta})
    t = trajectory_forecast({"velocity": velocity, **m})
    return {**m, **t}

def main(*args, **kwargs):
    legacy = _load_legacy()
    if not hasattr(legacy, "main"):
        raise RuntimeError("Legacy module missing main()")
    return legacy.main(*args, **kwargs)
