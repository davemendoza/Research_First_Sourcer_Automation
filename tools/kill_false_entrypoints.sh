#!/usr/bin/env bash
# EntryPoint Lockdown — macOS SAFE VERSION
# Maintainer: L. David Mendoza © 2025
# Date: 2026-01-12

set -e

APPLY="${APPLY:-0}"
FORCE="${FORCE:-0}"

ALLOWLIST="run_safe.py orchestrator.py shell/menu.zsh"
QUAR_DIR="tools/_QUARANTINE_ENTRYPOINTS"
REPORT_DIR="outputs/audit"
TS="$(date +"%Y-%m-%d_%H-%M-%S")"
REPORT="${REPORT_DIR}/entrypoint_lockdown_${TS}.txt"

die() { echo "ERROR: $*" >&2; exit 1; }

git rev-parse --show-toplevel >/dev/null 2>&1 || die "Not in git repo"
ROOT="$(git rev-parse --show-toplevel)"
cd "$ROOT"

mkdir -p "$QUAR_DIR" "$REPORT_DIR"

if [ "$FORCE" != "1" ] && [ -n "$(git status --porcelain)" ]; then
  die "Dirty git tree. Commit or stash first (or FORCE=1)."
fi

echo "EntryPoint Lockdown — $(date)" | tee "$REPORT"
echo "APPLY=$APPLY FORCE=$FORCE" | tee -a "$REPORT"
echo | tee -a "$REPORT"

is_allowed() {
  for a in $ALLOWLIST; do
    [ "$1" = "./$a" ] || [ "$1" = "$a" ] && return 0
  done
  return 1
}

echo "Scanning for executable Python entrypoints..." | tee -a "$REPORT"

find . -maxdepth 2 -type f -name "*.py" | while read -r f; do
  # skip git internals
  echo "$f" | grep -q "^./.git/" && continue

  # detect __main__ OR executable bit
  if grep -q 'if __name__ == "__main__"' "$f" || [ -x "$f" ]; then
    if is_allowed "$f"; then
      echo "KEEP: $f" | tee -a "$REPORT"
    else
      base="$(basename "$f")"
      dest="${QUAR_DIR}/${base}"

      if [ "$APPLY" = "1" ]; then
        echo "QUARANTINE: $f -> $dest" | tee -a "$REPORT"
        git mv "$f" "$dest"
      else
        echo "WOULD QUARANTINE: $f" | tee -a "$REPORT"
      fi
    fi
  fi
done

echo | tee -a "$REPORT"
echo "Done. Report: $REPORT" | tee -a "$REPORT"
