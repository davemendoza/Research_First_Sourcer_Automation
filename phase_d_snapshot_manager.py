"""
Phase D Snapshot Manager
Phase D introduces temporal awareness without altering the point-in-time
guarantees of Tracks A, B, and C.
"""

import json
import hashlib
from datetime import datetime
from pathlib import Path
import shutil

SNAPSHOT_DIR = Path("outputs/phase_d/snapshots")

def _checksum(records: dict) -> str:
    return hashlib.sha256(json.dumps(records, sort_keys=True).encode()).hexdigest()

def write_snapshot(entity_type: str, records: dict) -> Path:
    SNAPSHOT_DIR.mkdir(parents=True, exist_ok=True)
    ts = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    payload = {
        "entity_type": entity_type,
        "timestamp": ts,
        "checksum": _checksum(records),
        "records": records
    }
    tmp = SNAPSHOT_DIR / f"{entity_type}_{ts}.tmp"
    final = SNAPSHOT_DIR / f"{entity_type}_{ts}.json"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)
    shutil.move(tmp, final)
    return final
