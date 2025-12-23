#!/usr/bin/env python3
"""
Track F — Ranking & Scoring (Multi-Signal, Hardened)
v2.1 | Dec 22, 2025
© 2025 L. David Mendoza. All Rights Reserved.

Fix v2.1:
- Safely handles empty / malformed numeric fields
- No runtime crashes on real-world data
- Deterministic scoring preserved
"""

import csv
import os
import sys
import math

INPUT = "outputs/track_e/people_enriched.csv"
OUTDIR = "outputs/track_f"

if not os.path.exists(INPUT):
    sys.exit("❌ HARD FAIL: Track E output missing")

os.makedirs(OUTDIR, exist_ok=True)

def safe_float(v):
    try:
        if v is None:
            return 0.0
        if isinstance(v, str) and v.strip() == "":
            return 0.0
        return float(v)
    except Exception:
        return 0.0

rows = list(csv.DictReader(open(INPUT, encoding="utf-8")))

def score(r):
    contributions = safe_float(r.get("contributions"))
    followers = safe_float(r.get("github_followers"))
    acct_age = safe_float(r.get("github_account_age_years"))

    activity = math.log1p(contributions)
    influence = math.log1p(followers)
    longevity = math.log1p(acct_age)

    final = round(activity * 2.0 + influence * 1.5 + longevity, 3)

    r.update({
        "activity_score": round(activity, 3),
        "influence_score": round(influence, 3),
        "longevity_score": round(longevity, 3),
        "final_signal_score": final
    })

    return final

for r in rows:
    score(r)

rows.sort(key=lambda x: x["final_signal_score"], reverse=True)

def write(name, cutoff):
    path = os.path.join(OUTDIR, f"{name}.csv")
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=rows[0].keys())
        w.writeheader()
        for r in rows:
            if r["final_signal_score"] >= cutoff:
                w.writerow(r)
    print(f"✅ Wrote {path}")

write("frontier_ranked", 6.0)
write("inference_ranked", 4.5)
write("infra_ranked", 3.5)

print("✅ Track F v2.1 complete — hardened & stable")
