#!/usr/bin/env python3
"""
AI Talent Engine – People Enrichment Pass
© 2025 L. David Mendoza

Enriches GitHub users with:
- bio
- company
- followers
- public repos
- repo language signals
- LLM / Infra keyword detection
"""

import os
import time
import requests
import pandas as pd
from datetime import datetime

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
HEADERS = {
    "Accept": "application/vnd.github+json",
    "Authorization": f"Bearer {GITHUB_TOKEN}"
}

KEYWORDS = {
    "llm": ["llm", "language model", "transformer", "gpt", "bert", "llama"],
    "rlhf": ["rlhf", "reward model", "alignment"],
    "infra": ["cuda", "distributed", "inference", "kernel", "systems"],
}

def get_user(login):
    url = f"https://api.github.com/users/{login}"
    r = requests.get(url, headers=HEADERS, timeout=20)
    r.raise_for_status()
    return r.json()

def get_repos(login, limit=20):
    url = f"https://api.github.com/users/{login}/repos"
    r = requests.get(url, headers=HEADERS, params={"per_page": limit}, timeout=20)
    r.raise_for_status()
    return r.json()

def detect_signals(text):
    text = (text or "").lower()
    return {
        "llm_signal": any(k in text for k in KEYWORDS["llm"]),
        "rlhf_signal": any(k in text for k in KEYWORDS["rlhf"]),
        "infra_signal": any(k in text for k in KEYWORDS["infra"]),
    }

def main():
    input_path = sorted([
        os.path.join("output/people", d, "people_master.csv")
        for d in os.listdir("output/people")
    ])[-1]

    df = pd.read_csv(input_path)
    enriched = []

    print("🧠 Starting enrichment pass")
    for _, row in df.iterrows():
        try:
            user = get_user(row["login"])
            repos = get_repos(row["login"])

            repo_text = " ".join(
                (r.get("description") or "") + " " + (r.get("language") or "")
                for r in repos
            )

            signals = detect_signals(
                (user.get("bio") or "") + " " + repo_text
            )

            enriched.append({
                **row.to_dict(),
                "bio": user.get("bio"),
                "company": user.get("company"),
                "followers": user.get("followers"),
                "public_repos": user.get("public_repos"),
                **signals
            })

            time.sleep(0.3)

        except Exception:
            continue

    outdir = os.path.dirname(input_path)
    outpath = os.path.join(outdir, "people_enriched.csv")
    pd.DataFrame(enriched).to_csv(outpath, index=False)

    print("✅ ENRICHMENT COMPLETE")
    print(f"Output: {outpath}")
    print(f"Rows: {len(enriched)}")

if __name__ == "__main__":
    main()
