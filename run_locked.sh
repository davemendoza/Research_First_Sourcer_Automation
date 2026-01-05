#!/bin/bash
set -euo pipefail
cd "$(dirname "$0")"
export PYTHONPATH="$(pwd)/EXECUTION_CORE"
python3 EXECUTION_CORE/run_safe.py "$@"
