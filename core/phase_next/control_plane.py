"""
Phase-Next Control Plane (READ-ONLY default)

This module intentionally defaults to READ-ONLY operation.
No Excel writes and no GPT writeback are performed unless explicitly enabled.

Flags can be overridden via environment variables:
  PHASE_NEXT_READ_ONLY=1|0
  PHASE_NEXT_EXCEL_WRITE_ENABLED=1|0
  PHASE_NEXT_WATCHLIST_RULES_ENABLED=1|0
  PHASE_NEXT_GPT_WRITEBACK_ENABLED=1|0
  PHASE_NEXT_ADAPTIVE_CADENCE_ENABLED=1|0
"""

from __future__ import annotations

import os
from dataclasses import dataclass


def _env_bool(name: str, default: bool) -> bool:
    v = os.getenv(name)
    if v is None:
        return default
    v = v.strip().lower()
    if v in {"1", "true", "yes", "y", "on"}:
        return True
    if v in {"0", "false", "no", "n", "off"}:
        return False
    return default


@dataclass(frozen=True)
class ControlFlags:
    read_only: bool
    excel_write_enabled: bool
    watchlist_rules_enabled: bool
    gpt_writeback_enabled: bool
    adaptive_cadence_enabled: bool


def status() -> ControlFlags:
    # Safe defaults:
    # - read_only True
    # - excel_write_enabled False
    # - watchlist_rules_enabled True (evaluation only; no writes)
    # - gpt_writeback_enabled False (payload generation only)
    # - adaptive_cadence_enabled True (planning only; no writes)
    flags = ControlFlags(
        read_only=_env_bool("PHASE_NEXT_READ_ONLY", True),
        excel_write_enabled=_env_bool("PHASE_NEXT_EXCEL_WRITE_ENABLED", False),
        watchlist_rules_enabled=_env_bool("PHASE_NEXT_WATCHLIST_RULES_ENABLED", True),
        gpt_writeback_enabled=_env_bool("PHASE_NEXT_GPT_WRITEBACK_ENABLED", False),
        adaptive_cadence_enabled=_env_bool("PHASE_NEXT_ADAPTIVE_CADENCE_ENABLED", True),
    )

    # Guardrails: if read_only, force-disable writes
    if flags.read_only:
        return ControlFlags(
            read_only=True,
            excel_write_enabled=False,
            watchlist_rules_enabled=flags.watchlist_rules_enabled,
            gpt_writeback_enabled=flags.gpt_writeback_enabled,
            adaptive_cadence_enabled=flags.adaptive_cadence_enabled,
        )

    return flags


# Convenience booleans (common import pattern)
FLAGS = status()
READ_ONLY = FLAGS.read_only
EXCEL_WRITE_ENABLED = FLAGS.excel_write_enabled
WATCHLIST_RULES_ENABLED = FLAGS.watchlist_rules_enabled
GPT_WRITEBACK_ENABLED = FLAGS.gpt_writeback_enabled
ADAPTIVE_CADENCE_ENABLED = FLAGS.adaptive_cadence_enabled
