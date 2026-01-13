#!/usr/bin/env bash
set -euo pipefail

CSV="$1"

if [[ ! -f "$CSV" ]]; then
  echo "ERROR: CSV not found: $CSV"
  exit 1
fi

ROWS=$(( $(wc -l < "$CSV") - 1 ))
GH=$(awk -F',' 'NR>1 && tolower($0) ~ /github\.com\/[^,]+/ {c++} END {print c+0}' "$CSV")
GHIO=$(awk -F',' 'NR>1 && tolower($0) ~ /github\.io/ {c++} END {print c+0}' "$CSV")
CV=$(awk -F',' 'NR>1 && tolower($0) ~ /(cv|resume|\.pdf)/ {c++} END {print c+0}' "$CSV")
EMAIL=$(awk -F',' 'NR>1 && $0 ~ /@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}/ {c++} END {print c+0}' "$CSV")
PHONE=$(awk -F',' 'NR>1 && $0 ~ /[0-9]{3}[^0-9][0-9]{3}[^0-9][0-9]{4}/ {c++} END {print c+0}' "$CSV")

echo
echo "================ PEOPLE PIPELINE SUMMARY ================"
echo "Rows:               $ROWS"
echo "GitHub Profiles:    $GH"
echo "GitHub Pages (.io): $GHIO"
echo "CV / Resume Links:  $CV"
echo "Public Emails:      $EMAIL"
echo "Public Phones:      $PHONE"
echo "========================================================="
echo

open "$CSV"
