"""
Phase G Outputs
Writes:
- clusters.json
- movement_escalation_scores.json
- movement_signals.json (normalized events)
"""

from __future__ import annotations
from pathlib import Path
from typing import Any, Dict, List
from phase_g_io import atomic_write_json

def write_signals(out_dir: Path, events: List[Dict[str, Any]]) -> Path:
    p = out_dir / "signals" / "movement_signals.json"
    atomic_write_json(p, events)
    return p

def write_clusters(out_dir: Path, clusters: Dict[str, Any]) -> Path:
    p = out_dir / "clusters" / "clusters.json"
    atomic_write_json(p, clusters)
    return p

def write_scores(out_dir: Path, scores: Dict[str, Any], schema_version: str) -> Path:
    p = out_dir / "scores" / "movement_escalation_scores.json"
    payload = {
        "schema_version": schema_version,
        "scores": scores
    }
    atomic_write_json(p, payload)
    return p
