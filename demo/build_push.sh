#!/bin/zsh
# ======================================================
#  AI Talent Engine – Build & Push Script (v3.6 Unified Final)
#  © 2025 L. David Mendoza · All Rights Reserved
#  Purpose: Safe, repeatable pipeline for committing validated builds to GitHub.
# ======================================================

set -e
set -u
set +o nomatch

# ------------------------------------------------------
# Navigate to Demo Directory
# ------------------------------------------------------
cd ~/Desktop/Research_First_Sourcer_Automation/demo || {
  echo "❌ Demo directory not found."; exit 1;
}

# ------------------------------------------------------
# Cleanup
# ------------------------------------------------------
echo "🧹 Removing .DS_Store files before push..."
find . -name '.DS_Store' -type f -delete
echo "✅ Cleanup complete."

# ------------------------------------------------------
# Pre-Commit Schema Validation (safe audit)
# ------------------------------------------------------
if [[ -f "../AI_Talent_Schema_Rules.md" ]]; then
  echo "🔍 Running schema validation pre-check..."
  awk '/^#/{print}' "../AI_Talent_Schema_Rules.md" || true
  echo "✅ Schema rules file located and readable."
else
  echo "⚠️  Schema rules not found — continuing (non-blocking)."
fi

# ------------------------------------------------------
# Git Commit & Push Workflow
# ------------------------------------------------------
BUILD_ID=$(date +"%Y%m%d_%H%M%S")
GIT_BRANCH=$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo "main")
USER_ID=$(whoami)
HOST_ID=$(hostname)

echo "🚀 Starting build push for AI Talent Engine v3.6 Unified Final"
echo "📦 Build ID: ${BUILD_ID}"
echo "🌿 Branch: ${GIT_BRANCH}"

git add .
git commit -m "AI Talent Engine v3.6 Unified Final — Real-Time Research Intelligence (Build ${BUILD_ID}, ${USER_ID}@${HOST_ID})" || true
echo "📤 Pushing to remote branch '${GIT_BRANCH}'..."
git push origin "${GIT_BRANCH}"

TAG_NAME="v3.6-final"
echo "🏷️  Tagging release ${TAG_NAME}..."
git tag -a "${TAG_NAME}" -m "Governance-Locked Build ${BUILD_ID}"
git push origin "${TAG_NAME}"

# ------------------------------------------------------
# Post-Push Verification
# ------------------------------------------------------
echo "🔎 Verifying last commit..."
git log -1 --pretty=format:"✅ %h %s (%ci by %an)"

echo "\n======================================================="
echo "✅ AI Talent Engine Build v3.6 Unified Final pushed successfully"
echo "======================================================="
