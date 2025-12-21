"""
Run Phase D — Temporal Signal Intelligence
"""

import json
from phase_d_snapshot_manager import write_snapshot
from phase_d_diff_engine import compute_diff
from phase_d_watchlists import load_watchlist, apply_watchlist
from phase_d_escalation_flags import generate_flags

def run(entity_type: str, records: dict):
    write_snapshot(entity_type, records)
    diff_path = compute_diff(entity_type)
    if not diff_path:
        print("Phase D: first snapshot only")
        return
    with open(diff_path, encoding="utf-8") as f:
        diff_data = json.load(f)
    watch = load_watchlist(entity_type)
    filtered = apply_watchlist(diff_data["diffs"], watch)
    generate_flags(entity_type, filtered)

if __name__ == "__main__":
    print("Phase D ready. Invoke run(entity_type, records)")
