#!/usr/bin/env python3
"""
run_demo_api.py
Pulls candidate intelligence JSON files directly from your GitHub repository
and prints a clean summary.
"""

import requests
import json

# --------------------------------------------------------------------
# CONFIGURATION
# --------------------------------------------------------------------
CONFIG = {
    "repo": "davemendoza/Research_First_Sourcer_Automation",
    "branch": "main",
    "output_path": "output",
    "files": [
        "Ashudeep_Singh.json",
        "Patrick_von_Platen.json",
        "Shubham_Saboo.json"
    ]
}


# --------------------------------------------------------------------
# FUNCTIONS
# --------------------------------------------------------------------
def fetch_candidate_data(filename: str):
    """Fetch JSON file contents from GitHub."""
    base = f"https://raw.githubusercontent.com/{CONFIG['repo']}/{CONFIG['branch']}/{CONFIG['output_path']}"
    url = f"{base}/{filename}"
    print(f"🔗 Loading {filename} ...")

    response = requests.get(url)
    response.raise_for_status()
    return response.json()


def run_demo():
    """Main function to load and summarize candidate intelligence."""
    data = []
    for f in CONFIG["files"]:
        try:
            candidate = fetch_candidate_data(f)
            data.append(candidate)
        except Exception as e:
            print(f"⚠️ Error loading {f}: {e}")

    print(f"\n✅ Loaded {len(data)} candidate files from GitHub\n")

    # Display readable summaries
    print("📊 Candidate Intelligence Summary:\n")
    for c in data:
        name = c.get("name", "[unknown]")
        role = c.get("role", "[no role]")
        org = c.get("organization", "[unknown org]")
        summary = c.get("summary", "[no summary available]")

        print(f"👤 {name} — {role} at {org}")
        print(f"🧠 Summary: {summary}")
        print("-" * 70)

    print("\n🚀 Phase-7 API demo complete — candidate intelligence synced.\n")


# --------------------------------------------------------------------
# MAIN EXECUTION
# --------------------------------------------------------------------
if __name__ == "__main__":
    run_demo()
