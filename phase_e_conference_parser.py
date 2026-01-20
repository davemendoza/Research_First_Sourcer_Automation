"""
Phase E Conference Parser
Parses provided conference program JSON/CSV into normalized records.
"""

import json
from pathlib import Path

def parse_conference_program(path: str):
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(path)

    if p.suffix == ".json":
        with open(p, encoding="utf-8") as f:
            data = json.load(f)
    else:
        raise ValueError("Only JSON programs supported in Phase E")

    records = []
    for entry in data.get("entries", []):
        records.append({
            "name": entry.get("name"),
            "role": entry.get("role"),  # speaker | author
            "affiliation": entry.get("affiliation"),
            "session": entry.get("session"),
            "conference": data.get("conference"),
            "year": data.get("year")
        })
    return records
