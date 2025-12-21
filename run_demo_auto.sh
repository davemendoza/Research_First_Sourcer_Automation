#!/bin/bash
# ==============================================================================
# AI Talent Engine — Demo Autorun (Synthetic-Only, Guaranteed, Interview-Safe)
# Owner: Dave Mendoza
# © 2025 L. David Mendoza
# ==============================================================================

set -euo pipefail
IFS=$'\n\t'

REPO_ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$REPO_ROOT"

# ---------------- ENV ----------------
if [[ -d ".venv" ]]; then
  source .venv/bin/activate
fi
PYTHON=".venv/bin/python"
[[ -x "$PYTHON" ]] || PYTHON="python"

# ---------------- DEMO SAFETY ----------------
export ATE_DEMO_MODE=1
rm -f .git/index.lock 2>/dev/null || true

echo "▶ Running core demo pipeline (non-blocking)…"
if [[ -f demo/Run_Demo.sh ]]; then
  ./demo/Run_Demo.sh || true
fi

echo "▶ Generating SYNTHETIC demo artifacts (authoritative)…"

mkdir -p demo demo/charts

"$PYTHON" - <<'PY'
import csv, math, os
from datetime import datetime, timezone

ts = datetime.now(timezone.utc).isoformat()

# ---------- Synthetic CSVs ----------
applied = [
    {"Name":"Synthetic Applied A","Stack":"GPT-4 + RAG","Score":82,"UTC":ts},
    {"Name":"Synthetic Applied B","Stack":"Claude + VectorDB","Score":76,"UTC":ts},
    {"Name":"Synthetic Applied C","Stack":"Gemini + RAG","Score":70,"UTC":ts},
]

frontier_raw = [
    ("Synthetic Outlier", 350000),
    ("Synthetic Meta-Level", 50000),
    ("Synthetic Strong", 12000),
]

def log10p1(x): return math.log10(x+1)
logs = [log10p1(c) for _,c in frontier_raw]
ranks = sorted(logs)

frontier = []
for (name,c),lv in zip(frontier_raw,logs):
    pct = round(100*(ranks.index(lv)+1)/len(ranks),2)
    tier = "T1" if pct>=99 else "T2" if pct>=95 else "T3"
    frontier.append({
        "Name":name,
        "Citations_Raw":c,
        "Citations_Log10p1":round(lv,4),
        "Influence_Percentile":pct,
        "Influence_Tier":tier,
        "Math":"log10(citations+1) + percentile",
        "UTC":ts
    })

engineer = [
    {"Name":"Synthetic AI Eng 1","Signal":"High","UTC":ts},
    {"Name":"Synthetic AI Eng 2","Signal":"Medium","UTC":ts},
    {"Name":"Synthetic AI Eng 3","Signal":"Medium","UTC":ts},
]

def write(path, rows):
    with open(path,"w",newline="") as f:
        w=csv.DictWriter(f,rows[0].keys())
        w.writeheader(); w.writerows(rows)

write("demo/demo_applied_evaluation.csv", applied)
write("demo/demo_frontier_evaluation.csv", frontier)
write("demo/demo_ai_engineer_evaluation.csv", engineer)
PY

# ---------- Synthetic Charts ----------
"$PYTHON" - <<'PY'
import matplotlib.pyplot as plt, os
os.makedirs("demo/charts", exist_ok=True)

def chart(name,vals,title):
    plt.figure()
    plt.bar(["A","B","C"],vals)
    plt.title(title)
    plt.ylim(0,100)
    plt.tight_layout()
    plt.savefig(name)
    plt.close()

chart("demo/charts/applied_scores.png",[82,76,70],"Applied Demo Scores")
chart("demo/charts/frontier_influence.png",[100,66,33],"Frontier Influence (Outlier-Safe)")
chart("demo/charts/engineer_signal.png",[90,65,60],"AI Engineer Signals")
PY

# ---------- Summary ----------
cat > demo/demo_summary.txt <<EOF_SUM
AI TALENT ENGINE — SYNTHETIC DEMO SUMMARY
Run UTC: $(date -u +"%Y-%m-%dT%H:%M:%SZ")

Artifacts:
- demo/demo_applied_evaluation.csv
- demo/demo_frontier_evaluation.csv
- demo/demo_ai_engineer_evaluation.csv
- demo/charts/*.png

Notes:
- All data is synthetic and interview-safe
- Frontier math uses log-scale + percentile
EOF_SUM

# ---------- AUTO OPEN ----------
if [[ "$OSTYPE" == "darwin"* ]]; then
  open demo/demo_applied_evaluation.csv
  open demo/demo_frontier_evaluation.csv
  open demo/demo_ai_engineer_evaluation.csv
  open demo/charts
  open demo/demo_summary.txt
fi

echo "✅ SYNTHETIC DEMO READY — PRESENTATION SAFE"
