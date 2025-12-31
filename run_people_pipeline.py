#!/usr/bin/env python3
"""
AI Talent Engine – People Pipeline (Hardened, Bearer Auth)
© 2025 L. David Mendoza

Purpose:
- Enumerate REAL GitHub users per scenario
- Requires GitHub fine-grained PAT
- Uses Authorization: Bearer <token> (MANDATORY)
"""

import os
import sys
import time
import requests
import pandas as pd
from datetime import datetime, timezone

# =========================
# CONFIG
# =========================
SCENARIO_FILE = "scenario_control_matrix.xlsx"
OUTPUT_ROOT = "output/people"
PER_PAGE = 50
MAX_USERS_PER_SCENARIO = 100

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

if not GITHUB_TOKEN:
    sys.exit("❌ GITHUB_TOKEN not set. Run: export GITHUB_TOKEN=github_pat_xxx")

HEADERS = {
    "Authorization": f"Bearer {GITHUB_TOKEN}",
    "Accept": "application/vnd.github+json",
    "User-Agent": "AI-Talent-Engine"
}

SEARCH_URL = "https://api.github.com/search/users"

# =========================
# HELPERS
# =========================
def search_github_users(query, limit):
    users = []
    page = 1

    while len(users) < limit:
        params = {
            "q": query,
            "per_page": PER_PAGE,
            "page": page
        }

        resp = requests.get(
            SEARCH_URL,
            headers=HEADERS,
            params=params,
            timeout=30
        )

        if resp.status_code == 401:
            raise RuntimeError(
                "GitHub API 401 Unauthorized.\n"
                "Fine-grained PATs REQUIRE header:\n"
                "Authorization: Bearer <token>"
            )

        resp.raise_for_status()
        data = resp.json()
        items = data.get("items", [])

        if not items:
            break

        users.extend(items)
        page += 1
        time.sleep(0.4)  # rate-limit safe

    return users[:limit]

# =========================
# MAIN
# =========================
def main():
    scenarios = pd.read_excel(SCENARIO_FILE)

    required_cols = {"scenario", "seed_value", "tier", "category"}
    missing = required_cols - set(cenarios := set(scenarios.columns))
    if missing:
        sys.exit(f"❌ Scenario matrix missing columns: {missing}")

    people = []

    print("🚀 Starting People Enumeration")
    print(f"📄 Scenarios loaded: {len(scenarios)}")

    for _, s in scenarios.iterrows():
        query = s["seed_value"]
        print(f"🔍 Query: {query}")

        users = search_github_users(query, MAX_USERS_PER_SCENARIO)

        for u in users:
            people.append({
                "login": u.get("login"),
                "html_url": u.get("html_url"),
                "scenario": s["scenario"],
                "tier": s["tier"],
                "category": s["category"],
                "source": "github_search",
                "discovered_at_utc": datetime.now(timezone.utc).isoformat()
            })

    df = (
        pd.DataFrame(people)
        .drop_duplicates(subset=["login"])
        .sort_values(["tier", "scenario", "login"])
    )

    ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    outdir = f"{OUTPUT_ROOT}/{ts}"
    os.makedirs(outdir, exist_ok=True)

    csv_path = f"{outdir}/people_master.csv"
    df.to_csv(csv_path, index=False)

    print("\n✅ PEOPLE PIPELINE COMPLETE")
    print(f"👤 Total unique people: {len(df)}")
    print(f"📁 Output: {csv_path}")
    print(f"📂 Open folder: open {outdir}")

if __name__ == "__main__":
    main()
