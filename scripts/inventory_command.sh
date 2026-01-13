#!/usr/bin/env bash
# ============================================================
# AI TALENT ENGINE — CANONICAL INVENTORY COMMAND (LOCKED)
# Author: Dave Mendoza
# Goal: One command -> Always produces exactly THREE canonical
#       files in INVENTORY_FINAL, every time, with loud failures.
#
# Outputs (stable names, always overwritten):
#   1) INVENTORY_FINAL/AI_Talent_Inventory_Manifest.json
#   2) INVENTORY_FINAL/AI_Talent_Repo_Inventory.json
#   3) INVENTORY_FINAL/AI_Talent_Schema_Inventory.txt
#
# This script is intentionally additive and non-destructive:
# - Never deletes your terminal menu bindings
# - Never requires manual unzip
# - Never silent
# ============================================================

set -euo pipefail

REPO_ROOT="/Users/davemendoza/Desktop/Research_First_Sourcer_Automation"
FINAL_DIR="${REPO_ROOT}/INVENTORY_FINAL"
DOWNLOADS_DIR="${HOME}/Downloads"
RUNNER="${REPO_ROOT}/scripts/inventory_runner.sh"

echo "📦 AI Talent Engine — Inventory (CANONICAL)"
echo "Repo root: ${REPO_ROOT}"
echo "Final dir: ${FINAL_DIR}"
echo

# Preflight: repo root
if [[ ! -d "${REPO_ROOT}" ]]; then
  echo "❌ FATAL: Repo root not found: ${REPO_ROOT}"
  exit 1
fi

cd "${REPO_ROOT}"

# Preflight: runner exists and executable
if [[ ! -f "${RUNNER}" ]]; then
  echo "❌ FATAL: Missing inventory runner: ${RUNNER}"
  exit 1
fi
if [[ ! -x "${RUNNER}" ]]; then
  echo "❌ FATAL: inventory_runner.sh not executable"
  echo "Fix: chmod +x ${RUNNER}"
  exit 1
fi

# Ensure output dir exists and is writable
mkdir -p "${FINAL_DIR}"
if [[ ! -w "${FINAL_DIR}" ]]; then
  echo "❌ FATAL: Final dir not writable: ${FINAL_DIR}"
  echo "Fix: chmod u+rwx ${FINAL_DIR}"
  exit 1
fi

# Run generator
echo "▶ Running generator: ${RUNNER}"
"${RUNNER}"
echo "▶ Generator completed"
echo

# Find newest artifacts in Downloads
LATEST_REPO_ZIP="$(ls -t "${DOWNLOADS_DIR}/AI_Talent_Repo_Inventory_"*.zip 2>/dev/null | head -1 || true)"
LATEST_SCHEMA_ZIP="$(ls -t "${DOWNLOADS_DIR}/AI_Talent_Schema_Inventory_"*.zip 2>/dev/null | head -1 || true)"
LATEST_DL_ZIP="$(ls -t "${DOWNLOADS_DIR}/AI_Talent_Downloads_Snapshot_"*.zip 2>/dev/null | head -1 || true)"

if [[ -z "${LATEST_REPO_ZIP}" || -z "${LATEST_SCHEMA_ZIP}" || -z "${LATEST_DL_ZIP}" ]]; then
  echo "❌ FATAL: Expected inventory ZIPs not found in ${DOWNLOADS_DIR}"
  echo "Expected patterns:"
  echo "  AI_Talent_Repo_Inventory_*.zip"
  echo "  AI_Talent_Schema_Inventory_*.zip"
  echo "  AI_Talent_Downloads_Snapshot_*.zip"
  exit 1
fi

echo "✔ Latest ZIPs detected:"
echo "  Repo ZIP:   $(basename "${LATEST_REPO_ZIP}")"
echo "  Schema ZIP: $(basename "${LATEST_SCHEMA_ZIP}")"
echo "  DL ZIP:     $(basename "${LATEST_DL_ZIP}")"
echo

# Extract into temp workspace
TMP_DIR="$(mktemp -d)"
cleanup() { rm -rf "${TMP_DIR}"; }
trap cleanup EXIT

unzip -oq "${LATEST_REPO_ZIP}" -d "${TMP_DIR}"
unzip -oq "${LATEST_SCHEMA_ZIP}" -d "${TMP_DIR}"
unzip -oq "${LATEST_DL_ZIP}" -d "${TMP_DIR}"

# Locate internal artifacts
REPO_JSON="$(find "${TMP_DIR}" -type f -name 'repo_inventory.json' | head -1 || true)"
SCHEMA_TXT="$(find "${TMP_DIR}" -type f -name 'schema_fields_*.txt' | head -1 || true)"
CONSOLE_TXT="$(find "${TMP_DIR}" -type f -name 'inventory_console_*.txt' | head -1 || true)"

if [[ -z "${REPO_JSON}" ]]; then
  echo "❌ FATAL: repo_inventory.json not found inside extracted ZIPs"
  exit 1
fi
if [[ -z "${SCHEMA_TXT}" ]]; then
  echo "❌ FATAL: schema_fields_*.txt not found inside extracted ZIPs"
  exit 1
fi

# Normalize into canonical names (always overwritten)
cp -f "${REPO_JSON}"  "${FINAL_DIR}/AI_Talent_Repo_Inventory.json"
cp -f "${SCHEMA_TXT}" "${FINAL_DIR}/AI_Talent_Schema_Inventory.txt"

# Build canonical manifest (stable name)
NOW_UTC="$(date -u +"%Y-%m-%dT%H:%M:%SZ")"
GIT_SHA="$(git rev-parse HEAD 2>/dev/null || echo "unknown")"

# Optional: include a short console log indicator only
HAS_CONSOLE_LOG="false"
if [[ -n "${CONSOLE_TXT}" ]]; then
  HAS_CONSOLE_LOG="true"
fi

cat > "${FINAL_DIR}/AI_Talent_Inventory_Manifest.json" <<MANIFEST
{
  "generated_utc": "${NOW_UTC}",
  "repo_root": "${REPO_ROOT}",
  "git_sha": "${GIT_SHA}",
  "source_zips": {
    "repo_inventory_zip": "$(basename "${LATEST_REPO_ZIP}")",
    "schema_inventory_zip": "$(basename "${LATEST_SCHEMA_ZIP}")",
    "downloads_snapshot_zip": "$(basename "${LATEST_DL_ZIP}")"
  },
  "outputs": {
    "inventory_manifest_json": "AI_Talent_Inventory_Manifest.json",
    "repo_inventory_json": "AI_Talent_Repo_Inventory.json",
    "schema_inventory_txt": "AI_Talent_Schema_Inventory.txt"
  },
  "diagnostics": {
    "console_log_present": ${HAS_CONSOLE_LOG}
  }
}
MANIFEST

# Hard success criteria: the three canonical files must exist and be non-empty
for f in \
  "${FINAL_DIR}/AI_Talent_Inventory_Manifest.json" \
  "${FINAL_DIR}/AI_Talent_Repo_Inventory.json" \
  "${FINAL_DIR}/AI_Talent_Schema_Inventory.txt"
do
  if [[ ! -s "${f}" ]]; then
    echo "❌ FATAL: Expected output missing or empty: ${f}"
    exit 1
  fi
done

echo "✅ INVENTORY COMPLETE (canonical outputs)"
ls -lh \
  "${FINAL_DIR}/AI_Talent_Inventory_Manifest.json" \
  "${FINAL_DIR}/AI_Talent_Repo_Inventory.json" \
  "${FINAL_DIR}/AI_Talent_Schema_Inventory.txt"
echo
