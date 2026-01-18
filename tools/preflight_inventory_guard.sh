#!/usr/bin/env bash
# ============================================================
# preflight_inventory_guard.sh
# Version: v2.2.1 (INTERVIEW SAFE)
# Author: © 2026 L. David Mendoza
#
# PURPOSE
# - Enforce execution hygiene
# - Whitelist protocol-level Python entrypoints
# - Prevent unauthorized __main__ blocks
# - Run structural regression tests safely
# ============================================================

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
EXEC="${ROOT}/EXECUTION_CORE"

echo "→ Preflight Inventory Guard"
echo "→ Repo root: ${ROOT}"

# ------------------------------------------------------------
# 1. Executable Python entrypoint whitelist (CRITICAL)
# ------------------------------------------------------------

echo "→ Checking executable Python entrypoints..."

ALLOWED_MAIN_FILES=(
  "EXECUTION_CORE/run_safe.py"
  "EXECUTION_CORE/inventory.py"
  "EXECUTION_CORE/talent_intelligence.py"
  "EXECUTION_CORE/canonical_role_resolver.py"
)

violations="$(grep -R "__name__ == \"__main__\"" "${EXEC}" || true)"

filtered="$(echo "${violations}" | grep -vF "$(printf "%s\n" "${ALLOWED_MAIN_FILES[@]}")" || true)"

if [[ -n "${filtered}" ]]; then
  echo "FAIL: Illegal executable blocks detected (only protocol files may be executable):" >&2
  echo "${filtered}" >&2
  exit 1
fi

echo "✓ Executable Python entrypoint check passed"

# ------------------------------------------------------------
# 2. Multilingual regression test (structural invariant)
# ------------------------------------------------------------

echo "→ Running multilingual regression test..."

TEST_FILE="${ROOT}/test/multilingual_regression_test.py"

if [[ ! -f "${TEST_FILE}" ]]; then
  echo "FAIL: missing test/multilingual_regression_test.py" >&2
  exit 1
fi

# Ensure repo root is importable
export PYTHONPATH="${ROOT}"

python3 "${TEST_FILE}"

echo "✓ Multilingual regression test passed"

# ------------------------------------------------------------
# DONE
# ------------------------------------------------------------

echo "✓ Preflight checks complete"
exit 0
