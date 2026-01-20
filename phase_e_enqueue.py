"""
Phase E Enqueue
Prepares candidates for downstream Phases F/G/B.
"""

import json
from pathlib import Path

ENQUEUE_DIR = Path("outputs/phase_e/enqueue")

def enqueue_candidates(records: list):
    ENQUEUE_DIR.mkdir(parents=True, exist_ok=True)
    out = []
    for r in records:
        out.append({
            "name": r["name"],
            "affiliation": r["affiliation"],
            "conference_signal": r["signal"],
            "source": f"{r['conference']} {r['year']}"
        })
    path = ENQUEUE_DIR / "conference_enqueue.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2)
    return path
