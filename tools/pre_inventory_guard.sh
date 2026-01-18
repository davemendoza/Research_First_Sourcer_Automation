#!/usr/bin/env bash
# ------------------------------------------------------------
# pre_inventory_guard.sh
# ------------------------------------------------------------
# POSIX-safe inventory guard (macOS compatible)
# Maintainer: L. David Mendoza © 2026
# ------------------------------------------------------------

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
INVENTORY_DIR="${ROOT_DIR}/INVENTORY_FINAL"

echo "▶ Inventory Guard: scanning repo at ${ROOT_DIR}"

if [[ ! -d "${INVENTORY_DIR}" ]]; then
  echo "✖ INVENTORY_FINAL directory missing"
  exit 1
fi

required_files=(
  "AI_Talent_Inventory_Manifest.json"
  "AI_Talent_Repo_Inventory.json"
  "AI_Talent_Schema_Inventory.txt"
)

missing=0

for f in "${required_files[@]}"; do
  if [[ ! -f "${INVENTORY_DIR}/${f}" ]]; then
    echo "✖ Missing inventory artifact: ${f}"
    missing=1
  fi
done

if [[ "${missing}" -ne 0 ]]; then
  echo "✖ Inventory guard failed"
  exit 1
fi

echo "✔ Inventory guard passed"
exit 0
