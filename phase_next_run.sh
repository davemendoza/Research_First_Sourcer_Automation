#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$REPO_ROOT"

echo "Repo Root: $REPO_ROOT"
echo "Using python3:"
command -v python3 >/dev/null 2>&1 || { echo "ERROR: python3 not found"; exit 1; }
python3 --version

echo ""
echo "Running Phase-Next activation (C/D/E) READ-ONLY, no writes"
python3 -c "from core.phase_next.phase_next_activation import main; main()"
