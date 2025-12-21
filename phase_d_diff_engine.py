"""
Phase D Diff Engine

Phase D introduces temporal awareness without altering the point-in-time
guarantees of Tracks A, B, and C. All judgment and prioritization remain downstream.
"""

import json
from pathlib import Path

DIFF_DIR = Path("outputs/phase_d/diffs")

def load_snapshots(entity_type: str):
    snap_dir = Path("outputs/phase_d/snapshots")
    snaps = sorted(snap_dir.glob(f"{entity_type}_*.json"))
    if len(snaps) < 2:
        return None, None
    with open(snaps[-2]) as f:
        prev = json.load(f)
    with open(snaps[-1]) as f:
        curr = json.load(f)
    return prev, curr

def compute_diff(entity_type: str):
    prev, curr = load_snapshots(entity_type)
    DIFF_DIR.mkdir(parents=True, exist_ok=True)
    if not prev or not curr:
        return None

    diffs = {}
    for k, v in curr["records"].items():
        pv = prev["records"].get(k)
        if pv is None:
            diffs[k] = {"flag": "NEW_SIGNAL"}
        elif v != pv:
            diffs[k] = {"flag": "ACCELERATION"}
        else:
            diffs[k] = {"flag": "STAGNATION"}

    out = {
        "entity_type": entity_type,
        "timestamp": curr["timestamp"],
        "diffs": diffs
    }

    path = DIFF_DIR / f"{entity_type}_{curr['timestamp']}_diff.json"
    with open(path, "w") as f:
        json.dump(out, f, indent=2)
    return path
