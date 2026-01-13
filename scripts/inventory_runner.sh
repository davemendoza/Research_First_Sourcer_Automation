#!/usr/bin/env bash
set -euo pipefail

ROOT="/Users/davemendoza/Desktop/Research_First_Sourcer_Automation"
OUT="$ROOT/outputs/inventory"
DL="$HOME/Downloads"
TS="$(date -u +%Y%m%dT%H%M%SZ)"

mkdir -p "$OUT"
mkdir -p "$DL"

echo "📦 AI Talent Engine — Inventory @ $TS"
echo "Repo: $ROOT"
echo

echo "▶ Repo Structure Audit"
python3 "$ROOT/autogen_inventory_audit.py" | tee "$OUT/inventory_console_${TS}.txt"
echo

echo "▶ Canonical Schema Fields"
python3 "$ROOT/inventory_schema_fields.py" > "$OUT/schema_fields_${TS}.txt"
echo

if [ ! -f "$OUT/repo_inventory.json" ]; then
  echo "❌ repo_inventory.json missing"
  exit 1
fi

ZIP_REPO="$OUT/AI_Talent_Repo_Inventory_${TS}.zip"
ZIP_SCHEMA="$OUT/AI_Talent_Schema_Inventory_${TS}.zip"
ZIP_DOWNLOADS="$OUT/AI_Talent_Downloads_Snapshot_${TS}.zip"

zip -j "$ZIP_REPO" \
  "$OUT/repo_inventory.json" \
  "$OUT/inventory_console_${TS}.txt"

zip -j "$ZIP_SCHEMA" \
  "$OUT/schema_fields_${TS}.txt"

zip -j "$ZIP_DOWNLOADS" \
  "$OUT/inventory_console_${TS}.txt"

cp "$ZIP_REPO" "$DL/"
cp "$ZIP_SCHEMA" "$DL/"
cp "$ZIP_DOWNLOADS" "$DL/"

echo
echo "✅ INVENTORY COMPLETE"
echo "📥 Files written to Downloads:"
echo " - $(basename "$ZIP_REPO")"
echo " - $(basename "$ZIP_SCHEMA")"
echo " - $(basename "$ZIP_DOWNLOADS")"
