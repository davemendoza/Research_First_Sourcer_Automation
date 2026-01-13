#!/usr/bin/env bash
set -euo pipefail

DL="$HOME/Downloads"

latest_console="$(ls -t "$DL"/AI_Talent_Inventory_*_console.txt | head -n 1)"
latest_txt="$(ls -t "$DL"/AI_Talent_Inventory_*_downloads.txt | head -n 1)"
latest_csv="$(ls -t "$DL"/AI_Talent_Inventory_*_downloads.csv | head -n 1)"
latest_manifest="$(ls -t "$DL"/AI_Talent_Inventory_*_manifest.json | head -n 1)"

cp -f "$latest_console"  "$DL/AI_Talent_Inventory_LATEST_console.txt"
cp -f "$latest_txt"      "$DL/AI_Talent_Inventory_LATEST_downloads.txt"
cp -f "$latest_csv"      "$DL/AI_Talent_Inventory_LATEST_downloads.csv"
cp -f "$latest_manifest" "$DL/AI_Talent_Inventory_LATEST_manifest.json"

open "$DL/AI_Talent_Inventory_LATEST_console.txt"
