#!/usr/bin/env python3
# © 2025 Dave Mendoza, DBA AI Craft, Inc.
# All rights reserved. Proprietary and confidential.
# Governed by the laws of the State of Colorado, USA.

"""
OpenAI Demo Runner
Research_First_Sourcer_Automation

Single-command, deterministic demo entry point.

Python executes.
GPT interprets.

This script is intentionally conservative:
- No live scraping
- No live GPT calls
- No network dependency
- No mutation of source data

Designed for 45–60 minute senior technical demos.
"""

import sys
import subprocess
import platform
import time
from pathlib import Path


# ---------------------------------------------------------------------
# Repo structure (authoritative)
# ---------------------------------------------------------------------

REPO_ROOT = Path(__file__).resolve().parents[1]
PHASE11_SCRIPT = REPO_ROOT / "Phase11" / "phase11_final_merge.py"
INPUT_DIR = REPO_ROOT / "outputs"
OUTPUT_FILE = REPO_ROOT / "final_frontier_radar.xlsx"


# ---------------------------------------------------------------------
# Presentation helpers
# ---------------------------------------------------------------------

def banner() -> None:
    print("\n" + "=" * 78)
    print(" AI TALENT ENGINE — FRONTIER SCIENTIST RADAR DEMO")
    print(" Research_First_Sourcer_Automation")
    print("=" * 78)
    print(" • Deterministic Python execution")
    print(" • GPT used only for reasoning and synthesis")
    print(" • Known-good, demo-locked build")
    print("=" * 78 + "\n")


def check_environment() -> None:
    print("🔎 Environment validation\n")

    print(f" • Python version: {platform.python_version()}")
    if sys.version_info < (3, 9):
        sys.exit("❌ Python 3.9 or newer is required")

    if not PHASE11_SCRIPT.exists():
        sys.exit("❌ Phase 11 script not found")

    if not INPUT_DIR.exists():
        sys.exit("❌ outputs/ directory not found")

    print(" ✅ Environment OK\n")


# ---------------------------------------------------------------------
# Core execution
# ---------------------------------------------------------------------

def run_phase11() -> None:
    print("▶ Running Phase 11 — Final Frontier Radar Merge\n")

    cmd = [
        sys.executable,
        str(PHASE11_SCRIPT),
        "--inputs",
        str(INPUT_DIR),
        "--out",
        str(OUTPUT_FILE),
    ]

    subprocess.run(cmd, check=True)

    if not OUTPUT_FILE.exists():
        sys.exit("❌ Expected output file was not created")

    print("\n✅ Phase 11 complete")
    print(f"📄 Output written to: {OUTPUT_FILE}\n")


# ---------------------------------------------------------------------
# GPT integration explanation (verbal anchor for demo)
# ---------------------------------------------------------------------

def explain_gpt_boundary() -> None:
    print("=" * 78)
    print(" GPT ↔ PYTHON INTEGRATION MODEL")
    print("=" * 78)
    print(
        "Python responsibilities:\n"
        " • Data ingestion\n"
        " • Enrichment\n"
        " • Scoring\n"
        " • Ranking\n"
        " • Artifact generation\n\n"
        "GPT responsibilities:\n"
        " • Interpret ranked outputs\n"
        " • Explain tradeoffs\n"
        " • Generate hiring-manager narratives\n\n"
        "Key principle:\n"
        " Python decides what is true.\n"
        " GPT explains why it matters.\n"
    )
    print("=" * 78 + "\n")


# ---------------------------------------------------------------------
# Convenience: open Excel automatically
# ---------------------------------------------------------------------

def open_excel() -> None:
    print("📊 Opening final artifact\n")
    time.sleep(1)

    system = platform.system()
    if system == "Darwin":
        subprocess.run(["open", str(OUTPUT_FILE)])
    elif system == "Windows":
        subprocess.run(["start", str(OUTPUT_FILE)], shell=True)
    else:
        print("ℹ️ Please open the Excel file manually.")


# ---------------------------------------------------------------------
# Main demo flow
# ---------------------------------------------------------------------

def main() -> None:
    banner()
    check_environment()
    run_phase11()
    explain_gpt_boundary()
    open_excel()

    print("\n🎬 Demo execution complete")
    print("This system is a research collaborator, not a sourcing tool.")
    print("=" * 78 + "\n")


if __name__ == "__main__":
    main()
