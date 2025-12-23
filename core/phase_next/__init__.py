"""
core.phase_next package

Import-safe by design. This package is used in read-only mode by default.
"""

from .control_plane import (
    status,
    FLAGS,
    READ_ONLY,
    EXCEL_WRITE_ENABLED,
    WATCHLIST_RULES_ENABLED,
    GPT_WRITEBACK_ENABLED,
    ADAPTIVE_CADENCE_ENABLED,
)

from .adaptive_cadence import plan_from_tier
from .watchlist_rules import evaluate_watchlist, evaluate_watchlist_candidate
from .gpt_writeback import prepare_gpt_writeback_payload, writeback
