#!/usr/bin/env python3
"""
Track E — Identity Enrichment (Expanded, Public GitHub Only)
v2.0 | Dec 22, 2025
© 2025 L. David Mendoza. All Rights Reserved.
"""

import csv, os, sys, time, math, requests
from datetime import datetime

INPUT = "outputs/track_d/people.csv"
OUTDIR = "outputs/track_e"
OUTPUT = f"{OUTDIR}/people_enriched.csv"

if not os.path.exists(INPUT):
    sys.exit("❌ HARD FAIL: Track D people.csv missing")

os.makedirs(OUTDIR, exist_ok=True)

API = "https://api.github.com"

def gh(url):
    r = requests.get(url, timeout=20)
    return r.json() if r.status_code == 200 else {}

def enrich(username):
    p = gh(f"{API}/users/{username}")
    repos = gh(f"{API}/users/{username}/repos?per_page=100")

    langs = {}
    for r in repos:
        l = r.get("language")
        if l:
            langs[l] = langs.get(l, 0) + 1

    top_langs = ",".join(sorted(langs, key=langs.get, reverse=True)[:3])
    created = p.get("created_at")

    acct_age = None
    if created:
        acct_age = round((datetime.utcnow() - datetime.fromisoformat(created.replace("Z",""))).days / 365, 2)

    return {
        "github_name": p.get("name"),
        "github_company": p.get("company"),
        "github_location": p.get("location"),
        "github_followers": p.get("followers", 0),
        "github_public_repos": p.get("public_repos", 0),
        "github_top_languages": top_langs,
        "github_account_age_years": acct_age,
    }

rows = list(csv.DictReader(open(INPUT, encoding="utf-8")))
fields = list(rows[0].keys()) + [
    "github_name","github_company","github_location",
    "github_followers","github_public_repos",
    "github_top_languages","github_account_age_years"
]

with open(OUTPUT,"w",newline="",encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=fields)
    w.writeheader()
    for r in rows:
        u = r.get("github_username") or r.get("github")
        if u:
            r.update(enrich(u.strip()))
            time.sleep(0.25)
        w.writerow(r)

print(f"✅ Track E v2 complete → {OUTPUT}")
