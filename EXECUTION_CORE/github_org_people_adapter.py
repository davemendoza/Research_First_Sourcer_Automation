#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EXECUTION_CORE/github_org_people_adapter.py
============================================================
GITHUB ORG PEOPLE ADAPTER (PUBLIC MEMBERS, DETERMINISTIC)

Maintainer: L. David Mendoza © 2026
Version: v1.0.0

Purpose
- Deterministically enumerate PUBLIC GitHub organization members.
- Convert a GitHub org people hub URL (e.g. https://github.com/orgs/openai/people)
  into person candidates:
    - GitHub_Username
    - GitHub_URL (https://github.com/<username>)
    - Seed_Query_Or_Handle

Non-negotiable rules
- Public evidence only
- No guessing / no fabrication
- Deterministic output ordering
- Rate-limited requests
- Optional authentication via env GITHUB_TOKEN for better rate limits
- Works even without token, but may be rate-limited

Important behavior
- GitHub API endpoint /orgs/{org}/members returns ONLY public members.
  That is acceptable and interview-safe.

Contract
- discover_people_from_org(org: str) -> list[dict]
"""

from __future__ import annotations

import json
import time
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

import requests


API_BASE = "https://api.github.com"
PER_PAGE = 100

# LOCKED limits (deterministic)
MAX_ORGS = 25
MAX_PAGES_PER_ORG = 10  # up to 1000 public members per org
REQUEST_TIMEOUT_S = 15
SLEEP_BETWEEN_REQUESTS_S = 0.2


def _norm(x: Any) -> str:
    return str(x or "").strip()


def _headers() -> Dict[str, str]:
    h = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "AI-Talent-Engine/1.0 (public research; contact: none)",
    }
    tok = _norm(__import__("os").environ.get("GITHUB_TOKEN"))
    if tok:
        h["Authorization"] = f"Bearer {tok}"
    return h


def _safe_get(url: str, params: Dict[str, Any]) -> Optional[requests.Response]:
    try:
        r = requests.get(url, headers=_headers(), params=params, timeout=REQUEST_TIMEOUT_S)
        # Handle rate limit politely (fail-closed later if empty)
        if r.status_code in (403, 429):
            # If rate-limited, try to read reset and sleep a tiny deterministic amount.
            # We do NOT sleep for long durations automatically.
            return r
        r.raise_for_status()
        return r
    except Exception:
        return None


def _parse_org_from_url(url: str) -> str:
    """
    Accepts:
      - https://github.com/orgs/<org>/people
      - https://github.com/orgs/<org>/repositories
      - https://github.com/<org> (org root)
    Returns org slug or empty.
    """
    u = (url or "").strip()
    if not u:
        return ""

    lower = u.lower()
    if "github.com/orgs/" in lower:
        # keep original split, but strip query/fragments
        base = u.split("?", 1)[0].split("#", 1)[0]
        parts = base.split("/")
        # ... github.com orgs <org> people
        try:
            idx = [p.lower() for p in parts].index("orgs")
            if idx + 1 < len(parts):
                return parts[idx + 1].strip()
        except Exception:
            return ""

    if "github.com/" in lower:
        base = u.split("?", 1)[0].split("#", 1)[0]
        parts = base.split("/")
        # https: '' github.com <org>
        # ensure last part exists
        if len(parts) >= 4:
            cand = parts[3].strip()
            # filter obvious non-org paths
            if cand and cand.lower() not in {"orgs", "features", "pricing", "topics", "about", "login", "join"}:
                return cand
    return ""


def discover_people_from_org(org: str) -> List[Dict[str, str]]:
    """
    Enumerate PUBLIC org members via GitHub API.

    Returns list of dict rows:
      - GitHub_Username
      - GitHub_URL
      - Seed_Query_Or_Handle
      - Source_Org
      - Source_API_URL
      - Field_Level_Provenance_JSON
    """
    org = _norm(org)
    if not org:
        return []

    out: List[Dict[str, str]] = []

    for page in range(1, MAX_PAGES_PER_ORG + 1):
        url = f"{API_BASE}/orgs/{org}/members"
        params = {"per_page": PER_PAGE, "page": page}

        r = _safe_get(url, params)
        time.sleep(SLEEP_BETWEEN_REQUESTS_S)

        if r is None:
            break

        # If rate limited or forbidden, stop cleanly for this org
        if r.status_code in (403, 429):
            break

        try:
            data = r.json()
        except Exception:
            break

        if not isinstance(data, list) or not data:
            break

        for item in data:
            if not isinstance(item, dict):
                continue
            login = _norm(item.get("login"))
            html_url = _norm(item.get("html_url")) or (f"https://github.com/{login}" if login else "")
            if not login:
                continue

            prov = {
                "GitHub_Username": {"source": url, "method": "github_api_org_members"},
                "GitHub_URL": {"source": url, "method": "github_api_org_members"},
                "Seed_Query_Or_Handle": {"source": "GitHub_Username", "method": "assign_handle"},
            }

            out.append({
                "GitHub_Username": login,
                "GitHub_URL": html_url,
                "Seed_Query_Or_Handle": login,
                "Source_Org": org,
                "Source_API_URL": url,
                "Field_Level_Provenance_JSON": json.dumps(prov, sort_keys=True),
            })

    # Deterministic de-dupe + sort
    seen = set()
    deduped: List[Dict[str, str]] = []
    for r in out:
        k = _norm(r.get("GitHub_Username")).lower()
        if not k or k in seen:
            continue
        seen.add(k)
        deduped.append(r)

    deduped.sort(key=lambda d: (_norm(d.get("Source_Org")).lower(), _norm(d.get("GitHub_Username")).lower()))
    return deduped


def discover_people_from_hub_rows(hub_rows: List[Dict[str, str]]) -> List[Dict[str, str]]:
    """
    Given anchor rows, enumerate members for GitHub Org People hubs.
    Returns unified person rows with GitHub usernames.
    """
    orgs: List[str] = []
    for r in hub_rows:
        u = _norm(r.get("Seed_Hub_URL") or r.get("URL") or "")
        org = _parse_org_from_url(u)
        if org:
            orgs.append(org)

    # deterministic de-dupe
    seen = set()
    uniq: List[str] = []
    for o in orgs:
        lo = o.lower()
        if lo in seen:
            continue
        seen.add(lo)
        uniq.append(o)

    uniq = uniq[:MAX_ORGS]

    people: List[Dict[str, str]] = []
    for org in uniq:
        try:
        people.extend(discover_people_from_org(org))
    except Exception as e:
        print(f"[WARN] GitHub org discovery failed: {e}")

    # global deterministic de-dupe
    seen_u = set()
    out: List[Dict[str, str]] = []
    for p in people:
        k = _norm(p.get("GitHub_Username")).lower()
        if not k or k in seen_u:
            continue
        seen_u.add(k)
        out.append(p)

    out.sort(key=lambda d: (_norm(d.get("Source_Org")).lower(), _norm(d.get("GitHub_Username")).lower()))
    return out


__all__ = ["discover_people_from_org", "discover_people_from_hub_rows"]
