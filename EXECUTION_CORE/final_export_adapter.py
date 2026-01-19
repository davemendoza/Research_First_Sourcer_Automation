#!/usr/bin/env python3
"""
DAY 20 — FINAL EXPORT ADAPTER

Prepare results for CSV/JSON export (no file writing).
"""

from typing import Dict, Any


def to_exportable(evaluation: Dict[str, Any]) -> Dict[str, Any]:
    """
    Return a flat, export-safe dict.
    """
    return dict(evaluation)


__all__ = ["to_exportable"]
