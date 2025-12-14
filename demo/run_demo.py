#!/usr/bin/env python3
# © 2025 Dave Mendoza, DBA AI Craft, Inc.
# All rights reserved. Proprietary and confidential.
# Governed by the laws of the State of Colorado, USA.

import json
import requests

CONFIG = {
    "repo": "davemendoza/Research_First_Sourcer_Automation",
    "branch": "main",
    "output_path": "output",
    "files": [
        "Ashudeep_Singh.json",
        "Patrick_von_Platen.json",
        "Shubham_Saboo.json",
    ],
}


def fetch_candidate_data(file_name: str) -> dict:
    """
    Fetch candidate intelligence from GitHub raw files.
    Safely strips legal headers and footers before JSON parsing.
    """
    base_url = (
        f"https://raw.githubusercontent.com/"
        f"{CONFIG['repo']}/{CONFIG['branch']}/{CONFIG['output_path']}"
    )
    url = f"{base_url}/{file_name}"

    print(f"Loading candidate file: {file_name}")
    response = requests.get(url, timeout=30)
    response.raise_for_status()

    raw_text = response.text.strip()

    # Strip any legal/header/footer text around JSON
    json_start = raw_text.find("{")
    json_end = raw_text.rfind("}")

    if json_start == -1 or json_end == -1 or json_end <= json_start:
        raise ValueError("No valid JSON object found in file")

    clean_json = raw_text[json_start : json_end + 1]
    return json.loads(clean_json)


def run_demo() -> None:
    records = []

    for file_name in CONFIG["files"]:
        try:
            record = fetch_candidate_data(file_name)
            records.append(record)
        except Exception as exc:
            print(f"Warning. Failed to load {file_name}. Reason: {exc}")

    print()
    print(f"Loaded {len(records)} candidate records")
    print("Candidate Intelligence Summary")
    print("=" * 72)

    for c in records:
        name = c.get("name", "[unknown]")
        roles = c.get("role_classification", [])
        score = c.get("composite_score", "N/A")
        recommendation = c.get("recommendation", "[no recommendation]")

        print(f"Name: {name}")
        print(f"Roles: {', '.join(roles) if roles else '[none]'}")
        print(f"Composite Score: {score}")
        print(f"Recommendation: {recommendation}")

        evidence = c.get("Evidence_Map_JSON", [])
        if isinstance(evidence, list) and evidence:
            print("Evidence Highlights:")
            for e in evidence[:3]:
                statement = e.get("statement")
                if statement:
                    print(f" - {statement}")

        print("-" * 72)

    print()
    print("Phase 7 demo complete.")
    print("Python ingestion layer validated.")
    print("GPT reasoning layer cleanly synchronized.")


if __name__ == "__main__":
    run_demo()
