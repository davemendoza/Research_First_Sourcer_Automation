"""
Run Phase E — Conference & Emergence Intelligence
"""

import json
from pathlib import Path
from phase_e_conference_parser import parse_conference_program
from phase_e_emergence_detector import detect_emergence
from phase_e_enqueue import enqueue_candidates

HISTORY_PATH = Path("outputs/phase_e/parsed/history.json")

def run(program_path: str):
    records = parse_conference_program(program_path)

    history = []
    if HISTORY_PATH.exists():
        with open(HISTORY_PATH, encoding="utf-8") as f:
            history = json.load(f)

    emergence = detect_emergence(records, history)

    HISTORY_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(HISTORY_PATH, "w", encoding="utf-8") as f:
        json.dump(history + records, f, indent=2)

    enqueue_candidates(emergence)
    print(f"Phase E complete: {len(emergence)} emerging signals")

if __name__ == "__main__":
    print("Phase E ready. Invoke run(program_path)")
