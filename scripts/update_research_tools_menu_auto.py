#!/usr/bin/env python3
"""
Automated Phase Extension Committer for AI Talent Engine
Appends new agents to AI_Talent_Engine_Research_Tools_Menu_Extended.md,
then stages, commits, and pushes automatically to origin/main.
Maintainer: L. David Mendoza © 2025
"""

from datetime import date
from pathlib import Path
import subprocess

# --- Configuration ---
REPO_ROOT = Path("/Users/davemendoza/Desktop/Research_First_Sourcer_Automation")
MENU_FILE = REPO_ROOT / "AI_Talent_Engine_Research_Tools_Menu_Extended.md"
DATE = date.today().strftime("%B %d %Y")

# --- Phase 8 Agents (example template) ---
AGENTS = [
    (33, "Predictive Career Trajectory Agent", "Predictive Analytics",
     "Career Velocity, Seniority Modeling",
     "Forecasts researcher career velocity and seniority progression using multi-year publication, citation, and repository data.",
     "Predictive Career Intelligence"),
    (34, "Emerging Talent Detector", "Predictive Analytics",
     "Early-Career Detection",
     "Identifies rising early-career contributors through velocity-adjusted citation and contribution patterns.",
     "High-Velocity Talent Detection"),
    (35, "Influence Trajectory Forecaster", "Predictive Analytics",
     "Influence Forecasting",
     "Projects 12-month influence deltas based on collaboration graph centrality and recent citation momentum.",
     "Predictive Influence Analytics"),
    (36, "Governance Integrity Agent", "Governance Analytics",
     "Schema, Responsible-AI Checks",
     "Audits schema compliance, provenance integrity, and Responsible-AI governance standards across all agent outputs.",
     "Integrity & Fairness Validation"),
    (37, "Predictive Hiring Signal Integrator", "Predictive Analytics",
     "Hiring Readiness Scoring",
     "Combines predictive career, influence, and compliance signals into a unified hiring-readiness index.",
     "Predictive Hiring Intelligence"),
]

PHASE = 8
START_AGENT = AGENTS[0][0]
END_AGENT = AGENTS[-1][0]

# --- Markdown Table Renderer ---
def render_table(rows):
    header = (
        "| # | Tool Name | Classification | Domain Focus | Description | Domain Niche |\n"
        "|:--:|:-----------|:----------------|:---------------|:---------------|:---------------|\n"
    )
    body = "\n".join(
        f"| {a[0]} | **{a[1]}** | {a[2]} | {a[3]} | {a[4]} | {a[5]} |" for a in rows
    )
    return header + body

SECTION = f"""
---

## VII. PREDICTIVE & GOVERNANCE ANALYTICS

{render_table(AGENTS)}

---

**Menu Version:** v3.3 (Extended – Phase {PHASE})  
**Last Updated:** {DATE}  
**Maintainer:** L. David Mendoza © 2025  
**Project:** Research-First Sourcer Automation
"""

# --- Append the section ---
if MENU_FILE.exists():
    with MENU_FILE.open("a", encoding="utf-8") as f:
        f.write("\n" + SECTION + "\n")
    print(f"✅ Section VII appended to {MENU_FILE.name}")
else:
    print(f"❌ File not found: {MENU_FILE}")
    exit(1)

# --- Git Automation ---
print("🔄 Running Git auto-push sequence...")
try:
    subprocess.run(["git", "-C", str(REPO_ROOT), "add", str(MENU_FILE)], check=True)
    commit_msg = f"Phase {PHASE} Extension – Agents {START_AGENT}–{END_AGENT} Auto-Generated"
    subprocess.run(["git", "-C", str(REPO_ROOT), "commit", "-m", commit_msg], check=True)
    subprocess.run(["git", "-C", str(REPO_ROOT), "push", "origin", "main"], check=True)
    print(f"🚀 Successfully pushed update to GitHub with commit: {commit_msg}")
except subprocess.CalledProcessError as e:
    print(f"❌ Git operation failed: {e}")
