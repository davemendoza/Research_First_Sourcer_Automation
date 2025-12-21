"""
Phase D Escalation Flags

Phase D introduces temporal awareness without altering the point-in-time
guarantees of Tracks A, B, and C. All judgment and prioritization remain downstream.
"""

import json
from pathlib import Path

ESC_DIR = Path("outputs/phase_d/escalations")

def generate_escalations(entity_type: str, diffs: dict):
    ESC_DIR.mkdir(parents=True, exist_ok=True)
    flags = {}
    for k, v in diffs.items():
        if v["flag"] in ("NEW_SIGNAL", "ACCELERATION"):
            flags[k] = v["flag"]

    out = {
        "entity_type": entity_type,
        "flags": flags
    }

    path = ESC_DIR / f"{entity_type}_escalations.json"
    with open(path, "w") as f:
        json.dump(out, f, indent=2)
    return path
