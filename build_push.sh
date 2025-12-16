#!/bin/zsh
# ======================================================
# AI Talent Engine — Build Push Automation (v3.6 Final)
# © 2025 L. David Mendoza. All Rights Reserved.
# ======================================================

set -euo pipefail
cd ~/Desktop/Research_First_Sourcer_Automation || {
  echo "❌ Repo directory not found. Exiting."; exit 1;
}

BUILD_ID=$(date +"%Y%m%d_%H%M%S")
USER_NAME=$(whoami)
HOST_NAME=$(hostname)
LOG_FILE="logs/build_push_${BUILD_ID}.log"

echo "======================================================="
echo " AI Talent Engine — Automated Git Push (v3.6 Unified)"
echo " $BUILD_ID — User: $USER_NAME@$HOST_NAME"
echo "======================================================="
echo "🔍 Running preflight checks..."

# Ensure git repo is initialized
if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  echo "❌ Not a git repository. Please initialize with: git init"; exit 1;
fi

# Ensure connectivity
if ! ping -c 1 github.com >/dev/null 2>&1; then
  echo "⚠️  Warning: No internet detected — push will fail if remote not cached."
fi

# Log and commit
{
  echo "🧭 Staging all modified and new files..."
  git add .

  echo "🧭 Creating versioned commit..."
  git commit -m "AI Talent Engine v3.6 Unified Final — Real-Time Research Intelligence Build ($BUILD_ID, $USER_NAME@$HOST_NAME)" || echo "ℹ️ Nothing new to commit."

  echo "🧭 Pushing to remote..."
  git push origin main || echo "⚠️ Push may fail if upstream not configured."

  echo "🧭 Creating governance tag..."
  git tag -a v3.6-final -m "Governance-Locked Build $BUILD_ID"
  git push origin v3.6-final || echo "⚠️ Tag push skipped or already exists."

  echo "🔒 Commit verification..."
  git log -1 --pretty=format:'✅ Commit %h by %an on %ad — %s' --date=iso

  echo "✅ All operations completed successfully."
  echo "======================================================="
  echo "Build ID: $BUILD_ID"
  echo "Timestamp: $(date)"
  echo "Logged by: $USER_NAME@$HOST_NAME"
  echo "======================================================="

} | tee -a "$LOG_FILE"
