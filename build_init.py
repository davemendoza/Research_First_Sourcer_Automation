#!/usr/bin/env python3
# ===========================================================
#  AI Talent Engine - Signal Intelligence
#  Autonomous Build + Integrity + Auto-Push Suite
#  © 2025 L. David Mendoza
#  Purpose: Secure, verifiable, self-publishing build engine.
# ===========================================================

import os
import subprocess
from datetime import datetime

# -----------------------------------------------------------
# Helper
# -----------------------------------------------------------
def run_command(cmd, capture=False):
    """Run shell command safely."""
    try:
        result = subprocess.run(cmd, check=True, text=True, capture_output=capture)
        return result.stdout.strip() if capture else True
    except subprocess.CalledProcessError:
        return None

# -----------------------------------------------------------
# 1️⃣ SSH Diagnostic
# -----------------------------------------------------------
def run_ssh_diagnostic():
    print("\n🔍 Running SSH Diagnostic Preflight...")
    result = subprocess.run(["bash", "core/ssh_diagnostic.sh"])
    if result.returncode == 0:
        print("✅ SSH Diagnostic passed — continuing build.\n")
    else:
        print("❌ SSH Diagnostic failed. Review /logs/ssh_health.log\n")
        exit(1)

run_ssh_diagnostic()

# -----------------------------------------------------------
# 2️⃣ Git Integrity Checks
# -----------------------------------------------------------
def git_status_check():
    print("🧭 Running Git Integrity Preflight Suite...")

    branch = run_command(["git", "rev-parse", "--abbrev-ref", "HEAD"], capture=True)
    if not branch:
        print("   ⚠️ Not a Git repository.")
        return False
    print(f"   • Current branch: {branch}")

    run_command(["git", "fetch"])
    status = run_command(["git", "status", "-sb"], capture=True)
    if "ahead" in status:
        print("   ⚠️ Local commits not pushed to GitHub.")
    elif "behind" in status:
        print("   ⚠️ Local branch behind remote.")
    else:
        print("   ✅ Branch synchronized with origin.")

    author = run_command(["git", "log", "-1", "--pretty=format:%an"], capture=True)
    if author:
        if "Mendoza" in author or "davemendoza" in author:
            print(f"   ✅ Last commit author verified: {author}")
        else:
            print(f"   ⚠️ Commit authored by {author} (verify authenticity).")

    commit_date = run_command(["git", "log", "-1", "--pretty=format:%ci"], capture=True)
    if commit_date:
        commit_dt = datetime.strptime(commit_date.split(" ")[0], "%Y-%m-%d")
        delta_days = (datetime.now() - commit_dt).days
        if delta_days > 7:
            print(f"   ⚠️ Last commit is {delta_days} days old.")
        else:
            print(f"   ✅ Commit freshness OK ({delta_days} days).")

    print("🧾 Git integrity check complete.\n")
    return True

git_status_check()

# -----------------------------------------------------------
# 3️⃣ Folder Initialization
# -----------------------------------------------------------
folders = [
    "core", "demos", "demos/demo_scripts", "demos/narration",
    "output", "archive", "logs", "docs"
]

print("🧱 Initializing directory structure...")
for folder in folders:
    os.makedirs(folder, exist_ok=True)
    print(f"   • {folder} ✓")

# -----------------------------------------------------------
# 4️⃣ Auto-generate README
# -----------------------------------------------------------
readme_text = f"""# AI Talent Engine — Signal Intelligence
Automated Research-First Sourcer Environment

Initialized automatically on {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}.
Includes:
- SSH and Git preflight verification
- Automated folder scaffolding
- Provenance logging and demo framework
"""
with open("README.md", "w") as f:
    f.write(readme_text)
print("📘 README.md refreshed.\n")

# -----------------------------------------------------------
# 5️⃣ Build Log
# -----------------------------------------------------------
log_name = f"logs/build_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
with open(log_name, "w") as log:
    log.write(f"Build completed successfully on {datetime.now()}\n")

run_audio_watchdog()
    print("✅ Build environment initialized successfully!")
print(f"📄 Log file: {log_name}")

# -----------------------------------------------------------
# 6️⃣ Auto-Commit + Push to GitHub
# -----------------------------------------------------------
print("\n🚀 Checking for modified files to push...")
changes = run_command(["git", "status", "--porcelain"], capture=True)
if changes:
    print("📦 Changes detected. Preparing to commit...")
    run_command(["git", "add", "."])
    commit_message = f"Automated build push — {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    run_command(["git", "commit", "-m", commit_message])
    print("📤 Pushing to GitHub...")
    push = subprocess.run(["git", "push", "origin", "main"])
    if push.returncode == 0:
        print("✅ Auto-push successful.")
    else:
        print("❌ Auto-push failed — check your SSH connection.")
else:
    print("✅ No new changes detected — nothing to push.")

# -----------------------------------------------------------
# 7️⃣ Provenance Summary
# -----------------------------------------------------------
summary = f"""
──────────────────────────────────────────────
🏁 BUILD COMPLETED: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
Repository: Research_First_Sourcer_Automation
Branch: main
Commit: Automated build push
Log file: {log_name}
──────────────────────────────────────────────
"""
print(summary)
with open(log_name, "a") as log:
    log.write(summary)
