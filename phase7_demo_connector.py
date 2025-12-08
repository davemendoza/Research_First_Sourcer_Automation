# ==============================================================
#  AI Talent Engine | Phase-7 Demo Connector
#  --------------------------------------------------------------
#  Purpose:
#     • Fetch Phase-7 demo dossiers and summary report directly
#       from the public GitHub repo.
#     • Parse JSON dossiers for the 3 candidate examples.
#     • Display an analytic dashboard (Citation Intelligence)
#       plus a preview of the Hiring Intelligence summary.
#
#  Version: 1.2 (future-ready baseline)
#  Maintainer: AI Talent Engine | Research-First Sourcer Automation
#  Last Updated: 2025-12-08
# ==============================================================

import requests
import pandas as pd
import json
from io import StringIO
from datetime import datetime
from textwrap import shorten

# ----------------------------------------------------------------
#  Repo configuration (update here if repo or branch changes)
# ----------------------------------------------------------------
REPO_OWNER = "davemendoza"
REPO_NAME = "Research_First_Sourcer_Automation"
BRANCH = "main"

RAW_BASE = (
    f"https://raw.githubusercontent.com/{REPO_OWNER}/{REPO_NAME}/{BRANCH}/output/"
)

FILES = [
    "Ashudeep_Singh.json",
    "Patrick_von_Platen.json",
    "Shubham_Saboo.json",
    "Hiring_Intelligence_Summary_Report.md",
]

# ----------------------------------------------------------------
#  Utility functions
# ----------------------------------------------------------------
def fetch_file(fname: str) -> str:
    """Download a file’s raw text from GitHub."""
    url = RAW_BASE + fname
    r = requests.get(url, timeout=15)
    if r.status_code == 200:
        return r.text
    raise RuntimeError(f"❌ Could not fetch {fname}: HTTP {r.status_code}")


def parse_json_safe(text: str, fname: str) -> dict:
    """Gracefully parse JSON with error handling."""
    try:
        return json.loads(text)
    except json.JSONDecodeError as e:
        print(f"⚠️  JSON parse error in {fname}: {e}")
        return {}


# ----------------------------------------------------------------
#  Core demo function
# ----------------------------------------------------------------
def run_phase7_demo(preview_chars: int = 2000):
    """
    Fetch and render the Phase-7 Citation Intelligence dashboard.

    Parameters
    ----------
    preview_chars : int
        How many characters of the summary report to show inline.
    """

    print("\n🚀 [AI Talent Engine] Phase-7 Demo Connector Initiated")
    print("==============================================================")
    print(f"📅 Run timestamp: {datetime.utcnow().isoformat()} UTC")
    print(f"📂 Source repo: {REPO_OWNER}/{REPO_NAME} ({BRANCH})\n")

    # --- Load JSON dossiers ---
    dossiers = []
    for f in FILES[:-1]:
        text = fetch_file(f)
        data = parse_json_safe(text, f)
        if data:
            dossiers.append(data)
            print(f"✅ Loaded {f} ({len(data)} keys)")

    # --- Display summary Markdown ---
    summary_md = fetch_file(FILES[-1])

    # --- Combine simple metrics table ---
    df = pd.DataFrame(
        [
            {
                "Name": d.get("Full_Name"),
                "Affiliation": d.get("Company"),
                "Citation_Velocity_Score": d.get("Citation_Velocity_Score"),
                "Influence_Tier": d.get("Influence_Tier"),
                "Collaboration_Count": d.get("Collaboration_Count"),
            }
            for d in dossiers
        ]
    )

    print("\n📊 PHASE-7 CITATION INTELLIGENCE DASHBOARD")
    print("--------------------------------------------------------------")
    if df.empty:
        print("⚠️  No data available — check JSON structure or paths.")
    else:
        print(df.to_markdown(index=False))

    print("\n---\n🧠 HIRING INTELLIGENCE SUMMARY PREVIEW\n")
    print(shorten(summary_md, width=preview_chars, placeholder="..."))
    print("\n(Full report available in repo → /output/Hiring_Intelligence_Summary_Report.md)")
    print("🏁 Demo complete.\n")

    return df


# ----------------------------------------------------------------
#  Future expansion hooks
# ----------------------------------------------------------------
def plot_influence_chart(df: pd.DataFrame):
    """(Optional) Render a bar plot of Citation Velocity Scores."""
    try:
        import matplotlib.pyplot as plt

        df = df.dropna(subset=["Name", "Citation_Velocity_Score"])
        df.plot(
            x="Name",
            y="Citation_Velocity_Score",
            kind="barh",
            legend=False,
            figsize=(6, 3),
            title="Citation Velocity by Candidate",
        )
        plt.xlabel("Citation Velocity Score")
        plt.tight_layout()
        plt.show()
    except Exception as e:
        print(f"⚠️  Could not render chart: {e}")


# ----------------------------------------------------------------
#  CLI entry point
# ----------------------------------------------------------------
if __name__ == "__main__":
    df = run_phase7_demo()
    # Optional visual analytics (comment out if not needed)
    # plot_influence_chart(df)
