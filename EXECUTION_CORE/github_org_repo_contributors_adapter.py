#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EXECUTION_CORE/github_org_repo_contributors_adapter.py
============================================================
GITHUB ORG REPO CONTRIBUTORS ADAPTER (PUBLIC, DETERMINISTIC, CAPPED)

Maintainer: L. David Mendoza © 2026
Version: v1.0.0

Purpose
- When /orgs/<org>/members (public members) returns empty, enumerate people by:
  org repositories -> contributors
- This is the correct fallback for orgs with hidden members.

Public-only
- Uses GitHub REST API public endpoints.
- If org has no public repos or contributors are hidden, results may still be limited.

Deterministic and safe
- Capped enumeration, stable sorting, strict de-dupe.
- Optional auth token via env GITHUB_TOKEN (recommended for rate limits).
- Never guesses, never fabricates.

Outputs rows compatible with downstream identity pipeline
- GitHub_Username
- GitHub_URL
- Seed_Query_Or_Handle
- Source_Org
- Source_Repo_FullName
- Source_API_URL
- Field_Level_Provenance_JSON
"""

from __future__ import annotations

import json
import os
import time
from typing import Any, Dict, List, Optional, Set, Tuple
from urllib.parse import urlparse

import requests


API_BASE = "https://api.github.com"
REQUEST_TIMEOUT_S = 12
SLEEP_BETWEEN_REQUESTS_S = 0.2

# LOCKED caps (deterministic)
MAX_ORGS = 20
MAX_REPOS_PER_ORG = 25
MAX_CONTRIB_PAGES_PER_REPO = 2  # 2*100 = 200 contributors max per repo
PER_PAGE = 100


def _norm(x: Any) -> str:
    return str(x or "").strip()


def _headers() -> Dict[str, str]:
    h = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "AI-Talent-Engine/1.0 (public research; contact: none)",
    }
    tok = _norm(os.environ.get("GITHUB_TOKEN"))
    if tok:
        h["Authorization"] = f"Bearer {tok}"
    return h


def _parse_org_from_url(url: str) -> str:
    """
    Accepts:
      - https://github.com/orgs/<org>/repositories
      - https://github.com/orgs/<org>/people
      - https://github.com/<org>
    Returns org slug or empty.
    """
    u = _norm(url)
    if not u:
        return ""

    lower = u.lower()
    if "github.com/orgs/" in lower:
        base = u.split("?", 1)[0].split("#", 1)[0]
        parts = base.split("/")
        try:
            idx = [p.lower() for p in parts].index("orgs")
            if idx + 1 < len(parts):
                return parts[idx + 1].strip()
        except Exception:
            return ""

    if "github.com/" in lower:
        base = u.split("?", 1)[0].split("#", 1)[0]
        parts = base.split("/")
        if len(parts) >= 4:
            cand = parts[3].strip()
            if cand and cand.lower() not in {"orgs", "features", "pricing", "topics", "about", "login", "join"}:
                return cand
    return ""


def _safe_get(url: str, params: Dict[str, Any]) -> Optional[requests.Response]:
    try:
        r = requests.get(url, headers=_headers(), params=params, timeout=REQUEST_TIMEOUT_S)
        # do not raise for 403/429; caller handles
        if r.status_code not in (403, 429):
            r.raise_for_status()
        return r
    except Exception:
        return None


def _list_org_repos(org: str) -> List[Dict[str, Any]]:
    """
    List public repos for org. Deterministically select up to MAX_REPOS_PER_ORG.
    Uses sort=pushed to bias toward active repos, but final order is deterministic.
    """
    out: List[Dict[str, Any]] = []
    for page in range(1, 6):  # up to 500 repos scanned, then capped
        url = f"{API_BASE}/orgs/{org}/repos"
        params = {
            "per_page": PER_PAGE,
            "page": page,
            "type": "public",
            "sort": "pushed",
            "direction": "desc",
        }
        r = _safe_get(url, params)
        time.sleep(SLEEP_BETWEEN_REQUESTS_S)

        if r is None:
            break
        if r.status_code in (403, 429):
            break

        try:
            data = r.json()
        except Exception:
            break

        if not isinstance(data, list) or not data:
            break

        for item in data:
            if isinstance(item, dict):
                out.append(item)

        if len(out) >= MAX_REPOS_PER_ORG:
            break

    # Deterministic trim + sort by full_name
    repos = []
    for item in out:
        full_name = _norm(item.get("full_name"))
        name = _norm(item.get("name"))
        if full_name and name:
            repos.append({"full_name": full_name, "name": name})
    repos = sorted(repos, key=lambda d: d["full_name"].lower())
    return repos[:MAX_REPOS_PER_ORG]


def _list_repo_contributors(full_name: str) -> List[str]:
    """
    Enumerate contributors for a repo via /repos/{full_name}/contributors.
    Public-only. Deterministic de-dupe and sort.
    """
    org_repo = _norm(full_name)
    if not org_repo or "/" not in org_repo:
        return []

    org, repo = org_repo.split("/", 1)
    logins: List[str] = []

    for page in range(1, MAX_CONTRIB_PAGES_PER_REPO + 1):
        url = f"{API_BASE}/repos/{org}/{repo}/contributors"
        params = {"per_page": PER_PAGE, "page": page, "anon": "false"}
        r = _safe_get(url, params)
        time.sleep(SLEEP_BETWEEN_REQUESTS_S)

        if r is None:
            break
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
            if login:
                logins.append(login)

    # deterministic de-dupe + sort
    seen = set()
    uniq = []
    for l in logins:
        k = l.lower()
        if k in seen:
            continue
        seen.add(k)
        uniq.append(l)
    uniq.sort(key=lambda s: s.lower())
    return uniq


def discover_contributors_from_org(org: str) -> List[Dict[str, str]]:
    org = _norm(org)
    if not org:
        return []

    repos = _list_org_repos(org)
    people_rows: List[Dict[str, str]] = []

    for repo in repos:
        full_name = repo["full_name"]
        logins = _list_repo_contributors(full_name)

        for login in logins:
            gh_url = f"https://github.com/{login}"
            prov = {
                "GitHub_Username": {"source": f"{API_BASE}/repos/{full_name}/contributors", "method": "github_api_repo_contributors"},
                "GitHub_URL": {"source": f"{API_BASE}/repos/{full_name}/contributors", "method": "github_api_repo_contributors"},
                "Seed_Query_Or_Handle": {"source": "GitHub_Username", "method": "assign_handle"},
                "Source_Repo_FullName": {"source": "github_api", "method": "repo_context"},
            }
            people_rows.append({
                "GitHub_Username": login,
                "GitHub_URL": gh_url,
                "Seed_Query_Or_Handle": login,
                "Source_Org": org,
                "Source_Repo_FullName": full_name,
                "Source_API_URL": f"{API_BASE}/repos/{full_name}/contributors",
                "Field_Level_Provenance_JSON": json.dumps(prov, sort_keys=True),
            })

    # deterministic de-dupe by username
    seen_u: Set[str] = set()
    out: List[Dict[str, str]] = []
    for r in people_rows:
        k = _norm(r.get("GitHub_Username")).lower()
        if not k or k in seen_u:
            continue
        seen_u.add(k)
        out.append(r)

    out.sort(key=lambda d: (_norm(d.get("Source_Org")).lower(), _norm(d.get("GitHub_Username")).lower()))
    return out


def discover_contributors_from_hub_rows(hub_rows: List[Dict[str, str]]) -> List[Dict[str, str]]:
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
        people.extend(discover_contributors_from_org(org))

    # global deterministic de-dupe
    seen_u: Set[str] = set()
    out: List[Dict[str, str]] = []
    for p in people:
        k = _norm(p.get("GitHub_Username")).lower()
        if not k or k in seen_u:
            continue
        seen_u.add(k)
        out.append(p)

    out.sort(key=lambda d: (_norm(d.get("Source_Org")).lower(), _norm(d.get("GitHub_Username")).lower()))
    return out


__all__ = ["discover_contributors_from_org", "discover_contributors_from_hub_rows"]
