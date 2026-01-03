#!/usr/bin/env bash
set -euo pipefail

# AI Talent Engine — Import Scope Lockdown
# © 2025 L. David Mendoza
# Version: v1.0.0-recovery-pack
#
# Purpose:
# - Move non-canonical duplicate-prone directories out of import scope
# - Idempotent: safe to run repeatedly
#
# This script does NOT delete anything.
# It archives into: _ARCHIVE/lockdown_<timestamp>/

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$REPO_ROOT"

TS="$(date +%Y%m%d_%H%M%S)"
DEST="_ARCHIVE/lockdown_${TS}"
mkdir -p "$DEST"

move_if_exists () {
  local p="$1"
  if [[ -e "$p" ]]; then
    echo "[MOVE] $p -> $DEST/"
    mv "$p" "$DEST/"
  else
    echo "[SKIP] $p (not found)"
  fi
}

echo "============================================"
echo "Lockdown import scope"
echo "Repo: $REPO_ROOT"
echo "Archive: $DEST"
echo "============================================"

# High-risk directories commonly containing duplicates/variants
move_if_exists "_QUARANTINE"
move_if_exists "backups"
move_if_exists "backup"
move_if_exists "Phase11"
move_if_exists "modules"
move_if_exists "core"

echo "Done."
echo "Next: run ./preflight_duplicate_guard.py"
