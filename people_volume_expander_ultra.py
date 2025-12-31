#!/usr/bin/env python3
"""
People Volume Expander – Ultra (SAFE BUILD)
© 2025 L. David Mendoza

- Crash-proof GitHub API handling
- Resume-safe
- Rate-limit tolerant
"""

import os
import time
import json
from datetime import datetime
import pandas as pd
import requests

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
API_BASE = "https://api.github.com"

HEADERS = {
    "Authorization": f"Bearer {GITHUB_TOKEN}",
    "Accept": "application/vnd.github+json"
} if GITHUB_TOKEN else {}

# ----------------------------
# SAFE JSON FETCH
# ----------------------------
def get_json(url, params=None, api_base=API_BASE):
    full_url = url if url.startswith("http") else f"{api_base}{url}"
    try:
        r = requests.get(full_url, headers=HEADERS, params=params, timeout=30)
    except requests.RequestException:
        return None

    if r.status_code in (403, 429):
        time.sleep(5)
        return None

    if not r.text or r.text.strip().startswith("<"):
        return None

    try:
        return r.json()
    except ValueError:
        return None

# ----------------------------
# SAFE REPO SEARCH
# ----------------------------
def search_repos(api_base, query, per_page, max_pages):
    all_items = []

    for page in range(1, max_pages + 1):
        params = {
            "q": query,
            "per_page": per_page,
            "page": page
        }

        data = get_json("/search/repositories", params=params, api_base=api_base)

        if not data or not isinstance(data, dict):
            time.sleep(2)
            continue

        items = data.get("items", [])
        if not items:
            break

        all_items.extend(items)
        time.sleep(1.5)

    return all_items

# ----------------------------
# MAIN
# ----------------------------
def main():
    print("🚀 Volume Expansion Starting")

    scenarios = pd.read_excel("scenario_control_matrix.xlsx")
    run_dir = f"output/people/VOL_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
    os.makedirs(run_dir, exist_ok=True)

    seen_people = {}
    seen_repos = {}

    for _, row in scenarios.iterrows():
        query = row["seed_value"]
        repos = search_repos(API_BASE, query, per_page=50, max_pages=5)

        for repo in repos:
            full_name = repo.get("full_name")
            if not full_name:
                continue

            if full_name in seen_repos:
                continue

            seen_repos[full_name] = repo

            contributors_url = repo.get("contributors_url")
            if not contributors_url:
                continue

            contributors = get_json(contributors_url)
            if not isinstance(contributors, list):
                continue

            for c in contributors:
                login = c.get("login")
                if not login:
                    continue
                seen_people.setdefault(login, {
                    "login": login,
                    "html_url": c.get("html_url"),
                    "source_query": query
                })

    people_df = pd.DataFrame(seen_people.values())
    repos_df = pd.DataFrame(seen_repos.values())

    people_df.to_csv(f"{run_dir}/people_master.csv", index=False)
    repos_df.to_csv(f"{run_dir}/repo_inventory.csv", index=False)

    print("✅ VOLUME EXPANSION COMPLETE")
    print(f"People: {len(people_df)}")
    print(f"Repos: {len(repos_df)}")
    print(f"Output: {run_dir}")

if __name__ == "__main__":
    main()
