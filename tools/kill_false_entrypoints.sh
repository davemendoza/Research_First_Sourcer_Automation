#!/usr/bin/env bash
# AI Talent Engine — Research_First_Sourcer_Automation
# EntryPoint Lockdown — QUARANTINE MODE (FAIL-CLOSED)
#
# Maintainer: L. David Mendoza © 2025
# Date: 2026-01-12
#
# Purpose:
#   Identify and quarantine all Python files that are executable entrypoints
#   except for an explicit allowlist.
#
# Safety:
#   - Uses git mv (reversible)
#   - No deletions
#   - Dry-run by default
#
# Usage:
#   Dry run:
#     bash tools/kill_false_entrypoints.sh
#
#   Apply:
#     APPLY=1 bash tools/kill_false_entrypoints.sh
#
#   Force with dirty tree (not recommended):
#     APPLY=1 FORCE=1 bash tools/kill_false_entrypoints.sh

set -euo pipefail

APPLY="${APPLY:-0}"
FORCE="${FORCE:-0}"

ALLOWLIST="run_safe.py orchestrator.py shell/menu.zsh"
QUAR_DIR="tools/_QUARANTINE_ENTRYPOINTS"
REPORT_DIR="outputs/audit"
TS="$(date +"%Y%m%dT%H%M%S")"
REPORT="${REPORT_DIR}/entrypoint_lockdown_${TS}.txt"

die() { echo "ERROR: $*" >&2; exit 1; }

git rev-parse --show-toplevel >/dev/null 2>&1 || die "Not in git repo"
ROOT="$(git rev-parse --show-toplevel)"
cd "$ROOT"

mkdir -p "$QUAR_DIR" "$REPORT_DIR"

if [[ "$FORCE" != "1" && -n "$(git status --porcelain)" ]]; then
  die "Dirty git tree. Commit or stash first (or FORCE=1)."
fi

echo "EntryPoint Lockdown — $(date -Is)" | tee "$REPORT"
echo "APPLY=$APPLY FORCE=$FORCE" | tee -a "$REPORT"
echo | tee -a "$REPORT"

# Enumerate entrypoints
mapfile -t ENTRYPOINTS < <(
  rg -l 'if __name__ == "__main__"' . \
  && find . -maxdepth 2 -name "*.py" -perm +111
)

echo "Discovered entrypoints:" | tee -a "$REPORT"
for f in "${ENTRYPOINTS[@]}"; do
  echo "  $f" | tee -a "$REPORT"
done
echo | tee -a "$REPORT"

is_allowed() {
  local f="$1"
  for a in $ALLOWLIST; do
    [[ "$f" == "./$a" || "$f" == "$a" ]] && return 0
  done
  return 1
}

for f in "${ENTRYPOINTS[@]}"; do
  [[ ! -f "$f" ]] && continue
  if is_allowed "$f"; then
    echo "KEEP: $f" | tee -a "$REPORT"
    continue
  fi

  base="$(basename "$f")"
  dest="${QUAR_DIR}/${base}"

  if [[ "$APPLY" == "1" ]]; then
    echo "QUARANTINE: $f -> $dest" | tee -a "$REPORT"
    git mv "$f" "$dest"
  else
    echo "WOULD QUARANTINE: $f" | tee -a "$REPORT"
  fi
done

echo | tee -a "$REPORT"
echo "Done. Report: $REPORT" | tee -a "$REPORT"
