#!/usr/bin/env bash
set -euo pipefail

export PHASE_NEXT_READ_ONLY=1
export PHASE_NEXT_EXCEL_WRITE_ENABLED=0
export PHASE_NEXT_GPT_WRITEBACK_ENABLED=0
export PHASE_NEXT_DRY_RUN=1

python3 -m core.phase_next.run_phase_next "$@"
