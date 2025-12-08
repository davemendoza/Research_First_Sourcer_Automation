#!/usr/bin/env python3
import requests, json

CONFIG = {
    "repo": "davemendoza/Research_First_Sourcer_Automation",
    "branch": "main",
    "output_path": "output",
    "files": ["Ashudeep_Singh.json", "Patrick_von_Platen.json", "Shubham_Saboo.json"],
}

def fetch_candidate_data(file_name):
    base = f"https://raw.githubusercontent.com/{CONFIG['repo']}/{CONFIG['branch']}/{CONFIG['output_path']}"
    url = f"{base}/{file_name}"
    print(f"🔗 Loading {file_name} ...")
    r = requests.get(url)
    r.raise_for_status()
    return r.json()

def run_demo():
    data = []
    for f in CONFIG["files"]:
        try:
            data.append(fetch_candidate_data(f))
        except Exception as e:
            print(f"⚠️ Error loading {f}: {e}")

    print(f"\n✅ Loaded {len(data)} candidate files from GitHub\n")
    print("📊 Candidate Intelligence Summary:\n")
    for c in data:
        print(f"👤 {c.get('name','[unknown]')} — {c.get('role','[no role]')} at {c.get('organization','[unknown org]')}")
        print(f"🧠 Summary: {c.get('summary','[no summary available]')}")
        print("-"*70)
    print("\n🚀 Phase-7 demo complete — candidate intelligence synced.\n")

if __name__ == "__main__":
    run_demo()
