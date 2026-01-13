#!/usr/bin/env bash
set -euo pipefail

CONTRACT="INVENTORY_CONTRACT.json"

if [[ ! -f "$CONTRACT" ]]; then
  echo "❌ FATAL: Missing inventory contract: $CONTRACT"
  exit 1
fi

py_get() {
  python3 - <<PY
import json, sys
p = sys.argv[1]
key = sys.argv[2]
with open(p, "r", encoding="utf-8") as f:
    d = json.load(f)
parts = key.split(".")
cur = d
for part in parts:
    if part not in cur:
        print("")
        sys.exit(0)
    cur = cur[part]
print(cur if isinstance(cur, str) else json.dumps(cur))
PY
}

MANIFEST_PATH="$(py_get "$CONTRACT" "required_artifacts.manifest")"
REPO_PATH="$(py_get "$CONTRACT" "required_artifacts.repo_inventory")"
SCHEMA_PATH="$(py_get "$CONTRACT" "required_artifacts.schema_inventory")"
HASH_PATH="$(py_get "$CONTRACT" "required_artifacts.hash")"
MAX_MINUTES="$(py_get "$CONTRACT" "fail_if_stale_minutes")"

if [[ -z "$MANIFEST_PATH" || -z "$REPO_PATH" || -z "$SCHEMA_PATH" || -z "$HASH_PATH" ]]; then
  echo "❌ FATAL: Contract missing required_artifacts keys"
  exit 1
fi

require_file() {
  local f="$1"
  if [[ ! -f "$f" ]]; then
    echo "❌ FATAL: Missing required inventory artifact: $f"
    exit 1
  fi
}

require_file "$MANIFEST_PATH"
require_file "$REPO_PATH"
require_file "$SCHEMA_PATH"
require_file "$HASH_PATH"

# Freshness check (fail closed)
NOW="$(date +%s)"
fresh_check() {
  local f="$1"
  local mod
  mod="$(stat -f %m "$f" 2>/dev/null || true)"
  if [[ -z "$mod" ]]; then
    echo "❌ FATAL: Unable to stat file: $f"
    exit 1
  fi
  local age_min=$(( (NOW - mod) / 60 ))
  if (( age_min > MAX_MINUTES )); then
    echo "❌ FATAL: Inventory stale: $f (${age_min} minutes old, max ${MAX_MINUTES})"
    exit 1
  fi
}

fresh_check "$MANIFEST_PATH"
fresh_check "$REPO_PATH"
fresh_check "$SCHEMA_PATH"
fresh_check "$HASH_PATH"

# Tamper check (fail closed)
(
  cd "$(dirname "$HASH_PATH")"
  shasum -c "$(basename "$HASH_PATH")" >/dev/null
) || {
  echo "❌ FATAL: Inventory hash mismatch. Inventory was modified or partial."
  exit 1
}

echo "✅ Inventory preflight passed"
