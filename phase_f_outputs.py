"""
Phase F Outputs
- Writes timelines + flags
- Schema locked
"""

from __future__ import annotations
from pathlib import Path
from typing import Dict, Any
from phase_f_io import atomic_write_json

def write_timelines(out_dir: Path, timelines: Dict[str, Any]) -> Path:
    p = out_dir / "timelines" / "timelines.json"
    atomic_write_json(p, timelines)
    return p

def write_velocity(out_dir: Path, velocity: Dict[str, Any]) -> Path:
    p = out_dir / "velocity" / "velocity.json"
    atomic_write_json(p, velocity)
    return p

def write_flags(out_dir: Path, transitions: Dict[str, Any], velocity: Dict[str, Any], schema_version: str) -> Path:
    p = out_dir / "flags" / "career_flags.json"
    merged = {}
    all_names = sorted(set(transitions.keys()) | set(velocity.keys()), key=lambda s: s.lower())
    for name in all_names:
        merged[name] = {
            "schema_version": schema_version,
            "transition": transitions.get(name),
            "velocity": velocity.get(name),
        }
    atomic_write_json(p, merged)
    return p
