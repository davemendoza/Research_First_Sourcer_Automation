# © 2026 L. David Mendoza
#
# FILE: public_api_day28.py
#
# PURPOSE:
# Define explicit public API boundaries for internal library use.
# This does not publish anything. It only declares what is safe to import.
#
# DESIGN:
# - Import-only
# - No side effects
# - Public surface is explicitly enumerated in __all__
#
# IMPORT-ONLY. NO SIDE EFFECTS.

from __future__ import annotations

from typing import Any, Dict, List, Mapping

# Day 23 binder (external ingestion)
from EXECUTION_CORE.external_ingestion_binder import bind_external_dataset  # noqa: F401

__all__ = [
    "bind_external_dataset",
]
