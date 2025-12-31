"""
Phase D Diff Engine
"""

import json
from pathlib import Path

DIFF_DIR = Path("outputs/phase_d/diffs")
SNAPSHOT_DIR = Path("outputs/phase_d/snapshots")

def _load_last_two(entity_type: str):
    snaps = sorted(SNAPSHOT_DIR.glob(f"{entity_type}_*.json"))
    if len(snaps) < 2:
        return None, None
    with open(snaps[-2], encoding="utf-8") as f:
        prev = json.load(f)
    with open(snaps[-1], encoding="utf-8") as f:
        curr = json.load(f)
    return prev, curr

def compute_diff(entity_type: str):
    prev, curr = _load_last_two(entity_type)
    if not prev or not curr:
        return None

    DIFF_DIR.mkdir(parents=True, exist_ok=True)
    diffs = {}

    for k, v in curr["records"].items():
        pv = prev["records"].get(k)
        if pv is None:
            diffs[k] = "NEW_SIGNAL"
        elif v != pv:
            diffs[k] = "ACCELERATION"
        else:
            diffs[k] = "STAGNATION"

    out = {
        "entity_type": entity_type,
        "timestamp": curr["timestamp"],
        "diffs": diffs
    }

    path = DIFF_DIR / f"{entity_type}_{curr['timestamp']}.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2)
    return path
