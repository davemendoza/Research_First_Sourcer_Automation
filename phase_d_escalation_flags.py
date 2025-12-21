"""
Phase D Escalation Flags
"""

import json
from pathlib import Path

ESC_DIR = Path("outputs/phase_d/escalations")

def generate_flags(entity_type: str, diffs: dict):
    ESC_DIR.mkdir(parents=True, exist_ok=True)
    flags = {k: v for k, v in diffs.items() if v in ("NEW_SIGNAL", "ACCELERATION")}
    out = {"entity_type": entity_type, "flags": flags}
    path = ESC_DIR / f"{entity_type}_escalations.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2)
    return path
