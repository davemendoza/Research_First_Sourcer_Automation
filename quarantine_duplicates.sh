#!/usr/bin/env bash
set -euo pipefail

QDIR="_QUARANTINE/duplicates"

echo "🔒 Quarantining duplicate '* 2.py' execution artifacts (macOS-safe)"
mkdir -p "$QDIR"

find . -type f \
  -name "* 2.py" \
  ! -path "./.venv/*" \
  ! -path "./venv/*" \
  ! -path "./_QUARANTINE/*" \
  | while IFS= read -r f; do
      rel="${f#./}"
      target="$QDIR/$rel"
      mkdir -p "$(dirname "$target")"
      mv "$f" "$target"
      echo "→ moved $rel"
    done

echo "✅ Duplicate quarantine complete"
