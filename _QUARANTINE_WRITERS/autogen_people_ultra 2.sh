#!/usr/bin/env bash
set -e

ROOT="$(pwd)"
STAMP="$(date +"%Y%m%d_%H%M%S")"
BACKUP_DIR="$ROOT/backups/$STAMP"
mkdir -p "$BACKUP_DIR"

echo "🧠 AI Talent Engine — People Pipeline ULTRA Autogen"
echo "📍 Root: $ROOT"
echo "🕒 Timestamp: $STAMP"
echo ""

backup() {
  if [ -f "$1" ]; then
    cp "$1" "$BACKUP_DIR/"
    echo "🗂️  Backed up $1"
  fi
}

for f in people_scenario_resolver.py people_quality_guardrails.py people_scorer.py people_report_builder.py run_people_pipeline.py; do
  backup "$f"
done

###############################################################################
# people_scenario_resolver.py
###############################################################################
cat <<'PY' > people_scenario_resolver.py
import pandas as pd
from pathlib import Path

def load_scenarios(xlsx_path: str):
    df = pd.read_excel(xlsx_path)
    required = {"scenario", "seed_type", "seed_value", "tier", "category"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"Scenario matrix missing columns: {missing}")
    return df
PY

###############################################################################
# people_quality_guardrails.py
###############################################################################
cat <<'PY' > people_quality_guardrails.py
def is_valid_person(p):
    if not p.get("person_name"):
        return False
    if not p.get("github_url"):
        return False
    return True

def dedupe_people(people):
    uniq = {}
    for p in people:
        key = p.get("github_url") or p.get("person_name")
        uniq[key] = p
    return list(uniq.values())
PY

###############################################################################
# people_scorer.py
###############################################################################
cat <<'PY' > people_scorer.py
def score_person(p):
    score = 0
    if p.get("followers", 0) >= 100: score += 2
    if p.get("repos", 0) >= 10: score += 2
    if "ai" in (p.get("bio","").lower()): score += 1
    p["signal_score"] = score
    return p
PY

###############################################################################
# people_report_builder.py
###############################################################################
cat <<'PY' > people_report_builder.py
import pandas as pd
from pathlib import Path

def write_outputs(people, outdir):
    Path(outdir).mkdir(parents=True, exist_ok=True)
    df = pd.DataFrame(people)
    csv_path = Path(outdir) / "people_master.csv"
    xlsx_path = Path(outdir) / "people_master.xlsx"
    df.to_csv(csv_path, index=False)
    df.to_excel(xlsx_path, index=False)
    return csv_path, xlsx_path
PY

###############################################################################
# run_people_pipeline.py
###############################################################################
cat <<'PY' > run_people_pipeline.py
import os
import requests
from datetime import datetime
from people_scenario_resolver import load_scenarios
from people_quality_guardrails import is_valid_person, dedupe_people
from people_scorer import score_person
from people_report_builder import write_outputs

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
HEADERS = {"Authorization": f"token {GITHUB_TOKEN}"} if GITHUB_TOKEN else {}

def search_github_users(query, limit=50):
    url = "https://api.github.com/search/users"
    params = {"q": query, "per_page": min(limit, 100)}
    r = requests.get(url, headers=HEADERS, params=params, timeout=30)
    r.raise_for_status()
    return r.json().get("items", [])

def enrich_user(u):
    profile = requests.get(u["url"], headers=HEADERS, timeout=30).json()
    return {
        "person_name": profile.get("name") or u.get("login"),
        "github_url": profile.get("html_url"),
        "followers": profile.get("followers", 0),
        "repos": profile.get("public_repos", 0),
        "bio": profile.get("bio",""),
        "organization": profile.get("company"),
    }

def main():
    scenarios = load_scenarios("scenario_control_matrix.xlsx")
    people = []

    for _, s in scenarios.iterrows():
        query = s["seed_value"]
        users = search_github_users(query, limit=100)
        for u in users:
            try:
                p = enrich_user(u)
                p["scenario"] = s["scenario"]
                if is_valid_person(p):
                    people.append(score_person(p))
            except Exception:
                continue

    people = dedupe_people(people)

    outdir = f"output/people/{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
    csv_path, xlsx_path = write_outputs(people, outdir)

    print("✅ PEOPLE PIPELINE COMPLETE")
    print(f"People (unique): {len(people)}")
    print(f"CSV:  {csv_path}")
    print(f"XLSX: {xlsx_path}")

if __name__ == "__main__":
    main()
PY

chmod +x run_people_pipeline.py
echo ""
echo "✅ ULTRA AUTOGEN COMPLETE"
echo "Next:"
echo "  export GITHUB_TOKEN=github_pat_xxx"
echo "  python3 run_people_pipeline.py"
