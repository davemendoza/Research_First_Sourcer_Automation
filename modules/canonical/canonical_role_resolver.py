#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EXECUTION_CORE/canonical_role_resolver.py
============================================================
CANONICAL ROLE RESOLVER (DETERMINISTIC, FAIL-CLOSED)

Maintainer: L. David Mendoza © 2026
Version: v1.0.0

Purpose
- Provide a single, deterministic resolver for Role_Type in the People schema.
- Enforce that resolved roles must be in data/ai_role_types.locked when available.
- Never invent role types.

Resolution order (LOCKED)
1) If row has Role_Type and it is valid, keep it.
2) If row has AI_Role_Type and it is valid, use it.
3) If env AI_TALENT_ROLE_CANONICAL is set and valid, use it.
4) If data/ai_role_types.locked exists but nothing matches, return "" (fail-closed)

Non-negotiable rules
- No guessing
- No ML
- Deterministic
- If ai_role_types.locked is present, only roles in that list are allowed.

Contract
- resolve_role_type(row: dict) -> str
- load_allowed_roles() -> set[str]

Changelog
- 2026-01-20: Initial deterministic role resolver with allowed-role lock file.

Validation
python3 -m py_compile EXECUTION_CORE/canonical_role_resolver.py
python3 -c "from EXECUTION_CORE.canonical_role_resolver import load_allowed_roles; print(len(load_allowed_roles()))"

Git (SSH)
git add EXECUTION_CORE/canonical_role_resolver.py
git commit -m "Add canonical role resolver (deterministic, locked role list enforcement)"
git push
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Dict, Set


REPO_ROOT = Path(__file__).resolve().parents[1]
LOCKED_ROLE_FILE = REPO_ROOT / "data" / "ai_role_types.locked"


def _norm(x: Any) -> str:
    return str(x or "").strip()


def load_allowed_roles() -> Set[str]:
    """
    Load allowed roles from data/ai_role_types.locked if it exists.
    One role per line. Blank lines and # comments ignored.

    If the file does not exist, returns empty set meaning "no lock enforcement".
    """
    if not LOCKED_ROLE_FILE.exists():
        return set()

    roles: Set[str] = set()
    for raw in LOCKED_ROLE_FILE.read_text(encoding="utf-8").splitlines():
        s = raw.strip()
        if not s:
            continue
        if s.startswith("#"):
            continue
        roles.add(s)
    return roles


def _is_allowed(role: str, allowed: Set[str]) -> bool:
    if not role:
        return False
    if not allowed:
        return True
    return role in allowed


def resolve_role_type(row: Dict[str, Any]) -> str:
    """
    Determine Role_Type deterministically without guessing.
    Returns "" when no valid role can be resolved.
    """
    allowed = load_allowed_roles()

    # 1) Preserve existing Role_Type if valid
    rt = _norm(row.get("Role_Type"))
    if _is_allowed(rt, allowed):
        return rt

    # 2) Use AI_Role_Type if valid
    art = _norm(row.get("AI_Role_Type"))
    if _is_allowed(art, allowed):
        return art

    # 3) Use scenario context if valid
    env_role = _norm(os.environ.get("AI_TALENT_ROLE_CANONICAL"))
    if _is_allowed(env_role, allowed):
        return env_role

    # 4) Fail-closed
    return ""


__all__ = ["resolve_role_type", "load_allowed_roles"]
