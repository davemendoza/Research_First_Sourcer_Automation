#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
adapter_contracts.py
------------------------------------------------------------
Day 4 – Adapter Contract Enforcement (Fail Closed)

Purpose:
- Centralize adapter output contract enforcement
- Prevent silent partial returns
- Provide deterministic diagnostics for demos and audits

Design Rules:
- Deterministic
- No scraping
- No mutation (validation only)
"""

from typing import Any, Dict, Tuple


PERSONAL_ARTIFACT_REQUIRED_KEYS = (
    "row_updates",
    "blank_explanations",
    "provenance_path",
    "evidence_summary",
)


def assert_personal_artifact_adapter_contract(out: Any) -> Dict[str, Any]:
    """
    Enforces the personal artifact adapter contract.

    Returns:
        out (dict) if valid

    Raises:
        ValueError with explicit reason if invalid
    """

    if not isinstance(out, dict):
        raise ValueError("Personal artifact adapter contract violated: expected dict.")

    missing = [k for k in PERSONAL_ARTIFACT_REQUIRED_KEYS if k not in out]
    if missing:
        raise ValueError(
            "Personal artifact adapter contract violated: missing keys: "
            + ", ".join(missing)
        )

    if not isinstance(out.get("row_updates"), dict):
        raise ValueError("Personal artifact adapter contract violated: row_updates must be dict.")

    if not isinstance(out.get("blank_explanations"), dict):
        raise ValueError("Personal artifact adapter contract violated: blank_explanations must be dict.")

    # provenance_path can be None or str-like
    prov = out.get("provenance_path")
    if prov is not None and not isinstance(prov, (str,)):
        # allow Path-like objects via __fspath__
        if not hasattr(prov, "__fspath__"):
            raise ValueError("Personal artifact adapter contract violated: provenance_path must be str/Path or None.")

    # evidence_summary can be None or str
    summ = out.get("evidence_summary")
    if summ is not None and not isinstance(summ, str):
        raise ValueError("Personal artifact adapter contract violated: evidence_summary must be str or None.")

    return out


def safe_validate_personal_artifact_adapter(out: Any) -> Tuple[bool, str]:
    """
    Returns (ok, reason). Does not raise.
    """
    try:
        assert_personal_artifact_adapter_contract(out)
        return True, ""
    except Exception as e:
        return False, str(e)
