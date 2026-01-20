#!/usr/bin/env python3
"""
AI Talent Engine – GitHub Enumerator (People Discovery)
Version: v1.0.0-ultra
Date: 2025-12-30
© 2025 L. David Mendoza. All Rights Reserved.

WHAT IT DOES
- Uses GitHub Search API to enumerate developer accounts related to scenario topics.
- Requires a token for scale: export GITHUB_TOKEN=...

HARDENING
- Rate limit awareness
- Retries with backoff
- Deterministic caps
"""

from __future__ import annotations

import os
import time
import random
import requests
from typing import Dict, List, Optional

API = "https://api.github.com"
UA = "AI-Talent-Engine/GitHubEnumerator (public-only)"

def _sleep():
    time.sleep(random.uniform(0.2, 0.6))

def _headers() -> dict:
    h = {"User-Agent": UA, "Accept": "application/vnd.github+json"}
    tok = os.getenv("GITHUB_TOKEN", "").strip()
    if tok:
        h["Authorization"] = f"Bearer {tok}"
    return h

def _get(url: str, params: dict, timeout: int = 30, retries: int = 6) -> Optional[dict]:
    backoff = 0.8
    for i in range(retries):
        r = requests.get(url, headers=_headers(), params=params, timeout=timeout)
        if r.status_code == 200:
            return r.json()
        if r.status_code in (403, 429):
            # rate limit; sleep longer
            time.sleep(backoff * (i + 2))
            backoff *= 1.9
            continue
        if r.status_code in (500, 502, 503):
            time.sleep(backoff * (i + 1))
            backoff *= 1.6
            continue
        time.sleep(backoff * (i + 1))
        backoff *= 1.5
    return None

def enumerate_people_from_topics(topics: List[str], per_scenario_target: int) -> List[dict]:
    people: Dict[str, dict] = {}

    # Search users by topic in repos (proxy): query users with repos mentioning keywords.
    # Example: q="cuda repos:>5"
    for t in topics:
        if len(people) >= per_scenario_target:
            break

        q = f"{t} repos:>5"
        page = 1
        while page <= 10 and len(people) < per_scenario_target:
            url = f"{API}/search/users"
            params = {"q": q, "per_page": 50, "page": page}
            data = _get(url, params)
            _sleep()
            if not data or "items" not in data:
                break

            for u in data["items"]:
                login = u.get("login") or ""
                html = u.get("html_url") or ""
                if not login:
                    continue

                if login not in people:
                    people[login] = {
                        "source_systems": ["GitHub"],
                        "openalex_author_id": "",
                        "github_login": login,
                        "full_name": login,  # resolved later if desired (public profile name)
                        "primary_affiliation": "",
                        "role_hint": "Software Engineer (GitHub)",
                        "evidence_urls": [html],
                        "raw_signals": {"topics": [t]},
                    }
                else:
                    people[login]["raw_signals"]["topics"] = list(dict.fromkeys(people[login]["raw_signals"]["topics"] + [t]))

                if len(people) >= per_scenario_target:
                    break

            page += 1

    return list(people.values())[:per_scenario_target]
