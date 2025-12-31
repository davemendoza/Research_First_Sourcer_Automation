#!/usr/bin/env python3
"""
AI Talent Engine – People Resolver (Identity Merge)
Version: v1.0.0-ultra
Date: 2025-12-30
© 2025 L. David Mendoza. All Rights Reserved.

PURPOSE
Merge and deduplicate people across enumerators into stable person_id rows.

Identity keys (highest to lowest):
1) OpenAlex author id
2) GitHub login
3) Normalized full name + affiliation (fallback)
"""

from __future__ import annotations

import hashlib
import re
from typing import Dict, List, Tuple

def _stable_id(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8", errors="ignore")).hexdigest()[:16]

def _norm_name(name: str) -> str:
    n = (name or "").strip().lower()
    n = re.sub(r"\s+", " ", n)
    n = re.sub(r"[^a-z0-9 \-']", "", n)
    return n

def resolve_people(raw_people: List[dict]) -> List[dict]:
    merged: Dict[str, dict] = {}

    for p in raw_people:
        oa = (p.get("openalex_author_id") or "").strip()
        gh = (p.get("github_login") or "").strip().lower()
        name = (p.get("full_name") or "").strip()
        aff = (p.get("primary_affiliation") or "").strip()

        if oa:
            key = f"openalex:{oa}"
        elif gh:
            key = f"github:{gh}"
        else:
            key = f"nameaff:{_norm_name(name)}|{_norm_name(aff)}"

        if key not in merged:
            merged[key] = {
                "person_id": "P-" + _stable_id(key),
                "full_name": name or gh or "Unknown",
                "primary_affiliation": aff,
                "role_hint": p.get("role_hint", ""),
                "source_systems": list(dict.fromkeys(p.get("source_systems", []))),
                "evidence_urls": list(dict.fromkeys(p.get("evidence_urls", []))),
                "raw_signals": p.get("raw_signals", {}),
                "openalex_author_id": oa,
                "github_login": gh,
                "scenario_tags": [],
            }
        else:
            m = merged[key]
            m["source_systems"] = list(dict.fromkeys(m["source_systems"] + p.get("source_systems", [])))
            m["evidence_urls"] = list(dict.fromkeys(m["evidence_urls"] + p.get("evidence_urls", [])))[:25]

            # prefer richer name/aff if missing
            if (not m["full_name"] or m["full_name"] == m.get("github_login")) and name:
                m["full_name"] = name
            if not m["primary_affiliation"] and aff:
                m["primary_affiliation"] = aff

            # merge signals shallowly
            rs = m.get("raw_signals") or {}
            prs = p.get("raw_signals") or {}
            for k, v in prs.items():
                if isinstance(v, list):
                    rs[k] = list(dict.fromkeys((rs.get(k) or []) + v))
                else:
                    rs[k] = v
            m["raw_signals"] = rs

    return list(merged.values())
