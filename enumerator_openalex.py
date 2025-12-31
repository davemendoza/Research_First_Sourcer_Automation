#!/usr/bin/env python3
"""
AI Talent Engine – OpenAlex Enumerator (People Discovery)
Version: v1.0.0-ultra
Date: 2025-12-30
© 2025 L. David Mendoza. All Rights Reserved.

WHAT IT DOES
- Uses OpenAlex public API to enumerate authors relevant to a scenario strategy.
- Produces candidate people rows with evidence URLs.

No scraping. No hallucinations. Deterministic volume controls.
"""

from __future__ import annotations

import time
import random
import requests
from typing import Dict, List, Tuple, Optional

OPENALEX = "https://api.openalex.org"
UA = "AI-Talent-Engine/PeopleEnumerator (contact: public-source-only)"

def _sleep():
    time.sleep(random.uniform(0.15, 0.45))

def _get(url: str, params: dict, timeout: int = 30, retries: int = 6) -> Optional[dict]:
    headers = {"User-Agent": UA}
    backoff = 0.6
    for i in range(retries):
        try:
            r = requests.get(url, params=params, headers=headers, timeout=timeout)
            if r.status_code == 200:
                return r.json()
            if r.status_code in (429, 500, 502, 503):
                time.sleep(backoff * (i + 1))
                backoff *= 1.6
                continue
        except Exception:
            time.sleep(backoff * (i + 1))
            backoff *= 1.6
    return None

def enumerate_people_from_topics(
    topics: List[str],
    per_scenario_target: int,
    max_pages: int = 10,
) -> List[dict]:
    """
    Strategy:
    - Query works for each topic.
    - Pull authorships from works.
    - Aggregate authors, keep affiliation and evidence.
    """
    people: Dict[str, dict] = {}

    # Use works search to get authors; OpenAlex supports search= for works.
    for topic in topics:
        if len(people) >= per_scenario_target:
            break

        cursor = "*"
        pages = 0

        while pages < max_pages and len(people) < per_scenario_target:
            url = f"{OPENALEX}/works"
            params = {
                "search": topic,
                "per-page": 200,
                "cursor": cursor,
                "select": "id,doi,title,authorships,primary_location,publication_year",
            }
            data = _get(url, params)
            _sleep()
            if not data or "results" not in data:
                break

            for w in data["results"]:
                evidence = []
                if w.get("id"):
                    evidence.append(w["id"])
                if w.get("doi"):
                    evidence.append(f"https://doi.org/{w['doi']}")
                pl = w.get("primary_location") or {}
                if pl.get("landing_page_url"):
                    evidence.append(pl["landing_page_url"])

                for a in (w.get("authorships") or []):
                    auth = a.get("author") or {}
                    aid = auth.get("id")
                    name = auth.get("display_name") or ""
                    if not aid or not name:
                        continue

                    inst = ""
                    insts = a.get("institutions") or []
                    if insts:
                        inst = insts[0].get("display_name") or ""

                    key = aid
                    if key not in people:
                        people[key] = {
                            "source_systems": ["OpenAlex"],
                            "openalex_author_id": aid,
                            "github_login": "",
                            "full_name": name,
                            "primary_affiliation": inst,
                            "role_hint": "Research Author",
                            "evidence_urls": list(dict.fromkeys(evidence))[:5],
                            "raw_signals": {"topics": [topic]},
                        }
                    else:
                        # merge evidence and topic tags
                        people[key]["evidence_urls"] = list(dict.fromkeys(people[key]["evidence_urls"] + evidence))[:10]
                        people[key]["raw_signals"]["topics"] = list(dict.fromkeys(people[key]["raw_signals"]["topics"] + [topic]))

                if len(people) >= per_scenario_target:
                    break

            cursor = data.get("meta", {}).get("next_cursor")
            if not cursor:
                break
            pages += 1

    return list(people.values())[:per_scenario_target]
