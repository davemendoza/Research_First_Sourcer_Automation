"""
Phase D Snapshot Manager

Phase D introduces temporal awareness without altering the point-in-time
guarantees of Tracks A, B, and C. All judgment and prioritization remain downstream.
"""

import json
import hashlib
from datetime import datetime
from pathlib import Path
import shutil

OUTPUT_DIR = Path("outputs/phase_d/snapshots")

def _checksum(data: dict) -> str:
    return hashlib.sha256(json.dumps(data, sort_keys=True).encode()).hexdigest()

def persist_snapshot(entity_type: str, data: dict) -> Path:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    ts = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    payload = {
        "entity_type": entity_type,
        "timestamp": ts,
        "checksum": _checksum(data),
        "records": data
    }
    tmp_path = OUTPUT_DIR / f"{entity_type}_{ts}.tmp"
    final_path = OUTPUT_DIR / f"{entity_type}_{ts}.json"
    with open(tmp_path, "w") as f:
        json.dump(payload, f, indent=2)
    shutil.move(tmp_path, final_path)
    return final_path
