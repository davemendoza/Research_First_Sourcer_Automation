"""
Run Phase D — Temporal Signal Intelligence

Phase D introduces temporal awareness without altering the point-in-time
guarantees of Tracks A, B, and C. All judgment and prioritization remain downstream.
"""

from phase_d_snapshot_manager import persist_snapshot
from phase_d_diff_engine import compute_diff
from phase_d_watchlists import load_watchlist, filter_diffs
from phase_d_escalation_flags import generate_escalations

def run(entity_type: str, records: dict):
    print(f"[Phase D] Snapshotting {entity_type}")
    persist_snapshot(entity_type, records)

    print(f"[Phase D] Computing diffs")
    diff_path = compute_diff(entity_type)
    if not diff_path:
        print("[Phase D] No previous snapshot — exiting cleanly")
        return

    with open(diff_path) as f:
        diff_data = f.read()

    watchlist = load_watchlist(entity_type)
    filtered = filter_diffs(eval(diff_data)["diffs"], watchlist)

    print(f"[Phase D] Generating escalation flags")
    generate_escalations(entity_type, filtered)

if __name__ == "__main__":
    print("Phase D requires Track C outputs injected programmatically.")
