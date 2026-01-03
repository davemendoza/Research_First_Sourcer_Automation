#!/usr/bin/env bash
# ==========================================================
#  AI Talent Engine – Integrity Audit Script
#  Verifies existence and SHA256 hashes of all key modules.
#  Outputs to logs/integrity_audit_<timestamp>.txt
# ==========================================================

set -euo pipefail

REPO_ROOT="$(pwd)"
LOG_DIR="$REPO_ROOT/logs"
mkdir -p "$LOG_DIR"

STAMP=$(date '+%Y%m%d_%H%M%S')
LOG_FILE="$LOG_DIR/integrity_audit_${STAMP}.txt"

echo "===============================================" | tee "$LOG_FILE"
echo " AI Talent Engine – Repository Integrity Audit " | tee -a "$LOG_FILE"
echo " Timestamp: $(date '+%Y-%m-%d %H:%M:%S')" | tee -a "$LOG_FILE"
echo "===============================================" | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"

FILES_TO_CHECK=(
  "master_phase11_12_autobuild.sh"
  "scripts/auto_inject_legal.py"
  "core/gpt_agent.py"
  "core/orchestrator.py"
  "Legal_Proprietary_Notice.txt"
  "requirements.txt"
  "README.md"
)

DIRS_TO_CHECK=(
  "core"
  "scripts"
  "enrichers"
  "outputs"
  "logs"
  "inputs"
  "docs"
  "dashboards"
)

echo ">>> Checking directory structure..." | tee -a "$LOG_FILE"
for d in "${DIRS_TO_CHECK[@]}"; do
  if [ -d "$d" ]; then
    echo "✅ $d directory exists" | tee -a "$LOG_FILE"
  else
    echo "❌ MISSING DIRECTORY: $d" | tee -a "$LOG_FILE"
  fi
done
echo "" | tee -a "$LOG_FILE"

echo ">>> Computing SHA256 hashes for core files..." | tee -a "$LOG_FILE"
for f in "${FILES_TO_CHECK[@]}"; do
  if [ -f "$f" ]; then
    HASH=$(shasum -a 256 "$f" | awk '{print $1}')
    echo "✅ $f  —  SHA256: $HASH" | tee -a "$LOG_FILE"
  else
    echo "❌ MISSING FILE: $f" | tee -a "$LOG_FILE"
  fi
done
echo "" | tee -a "$LOG_FILE"

echo ">>> Searching for stray copies under /Users/davemendoza ..." | tee -a "$LOG_FILE"
find /Users/davemendoza -maxdepth 2 -type f \( \
  -name "gpt_agent.py" -o -name "orchestrator.py" -o -name "master_phase11_12_autobuild.sh" \
\) 2>/dev/null | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"

echo "===============================================" | tee -a "$LOG_FILE"
echo " Integrity audit completed successfully.        " | tee -a "$LOG_FILE"
echo " Log saved to: $LOG_FILE                        " | tee -a "$LOG_FILE"
echo "===============================================" | tee -a "$LOG_FILE"
