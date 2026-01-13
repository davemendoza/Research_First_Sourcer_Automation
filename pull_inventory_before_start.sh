#!/usr/bin/env bash
set +H
set -euo pipefail

CONTRACT="INVENTORY_CONTRACT.json"

if [[ ! -f "$CONTRACT" ]]; then
  echo "❌ FATAL: Missing inventory contract: $CONTRACT"
  exit 1
fi

# -------------------------------
# Parse contract safely (jq-free)
# -------------------------------

get_value() {
  local key="$1"
  grep -E "\"$key\"" "$CONTRACT" | sed -E 's/.*: *"([^"]+)".*/\1/'
}

MANIFEST_PATH="$(get_value manifest)"
REPO_PATH="$(get_value repo_inventory)"
SCHEMA_PATH="$(get_value schema_inventory)"
HASH_PATH="$(get_value hash)"

if [[ -z "$MANIFEST_PATH" || -z "$REPO_PATH" || -z "$SCHEMA_PATH" || -z "$HASH_PATH" ]]; then
  echo "❌ FATAL: Inventory contract missing required paths"
  exit 1
fi

# -------------------------------
# Required files must exist
# -------------------------------

require_file() {
  if [[ ! -f "$1" ]]; then
    echo "❌ FATAL: Missing required inventory artifact: $1"
    exit 1
  fi
}

require_file "$MANIFEST_PATH"
require_file "$REPO_PATH"
require_file "$SCHEMA_PATH"
require_file "$HASH_PATH"

# -------------------------------
# Tamper detection (hash)
# -------------------------------

(
  cd "$(dirname "$HASH_PATH")"
  shasum -c "$(basename "$HASH_PATH")" >/dev/null
) || {
  echo "❌ FATAL: Inventory hash mismatch — inventory corrupted or partial"
  exit 1
}

echo "✅ Inventory preflight passed"
