#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EXECUTION_CORE/people_discovery_from_hubs.py
============================================================
PEOPLE DISCOVERY FROM HUBS (ADAPTER-FIRST + CONTRIBUTORS FALLBACK + WEB FALLBACK)

Maintainer: L. David Mendoza © 2026
Version: v1.2.0

Purpose
- Convert hub/org anchor output into candidate PEOPLE rows.

Key reality
- Many frontier orgs have zero public members via /orgs/{org}/members.
- Correct fallback is: org public repos -> contributors.

Order (LOCKED)
1) GitHub Org People adapter (public members)
2) If empty: GitHub Org Repo Contributors adapter (public repos -> contributors)
3) Web fallback for non-GitHub hubs (1 hop link extraction)

Non-negotiable
- Public sources only
- Deterministic ordering + de-dupe
- Fail-closed if total discovered people = 0
"""

from __future__ import annotations

import csv
import json
import re
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple
from urllib.parse import urljoin, urlparse

import requests

from EXECUTION_CORE.github_org_people_adapter import discover_people_from_hub_rows
from EXECUTION_CORE.github_org_repo_contributors_adapter import discover_contributors_from_hub_rows


URL_RE = re.compile(r"https?://[^\s\"'<>]+", re.IGNORECASE)
HREF_RE = re.compile(r'href=[\'"]([^\'"]+)[\'"]', re.IGNORECASE)

GITHUB_USER_RE = re.compile(r"^https?://(www\.)?github\.com/([^/\s?#]+)(?:[/?#].*)?$", re.IGNORECASE)
GITHUB_REPO_RE = re.compile(r"^https?://(www\.)?github\.com/[^/\s?#]+/[^/\s?#]+(?:[/?#].*)?$", re.IGNORECASE)

LINKEDIN_IN_RE = re.compile(r"^https?://(www\.)?linkedin\.com/in/([^/?#]+)(?:[/?#].*)?$", re.IGNORECASE)
SCHOLAR_USER_RE = re.compile(r"^https?://(www\.)?scholar\.google\.com/citations\?(?:[^#]*&)?user=([^&#]+)", re.IGNORECASE)
SEMANTIC_AUTHOR_RE = re.compile(r"^https?://(www\.)?semanticscholar\.org/author/([^/?#]+)", re.IGNORECASE)
ORCID_RE = re.compile(r"^https?://(www\.)?orcid\.org/(\d{4}-\d{4}-\d{4}-\d{3}[\dX])", re.IGNORECASE)

TEAM_HINT_RE = re.compile(r"(team|people|researchers|staff|about|leadership|members|faculty|lab|group)", re.IGNORECASE)

GITHUB_IGNORE = {
    "topics", "orgs", "organizations", "site", "features", "pricing", "about",
    "login", "join", "explore", "marketplace", "settings", "pulls", "issues",
}

MAX_HUBS = 25
MAX_PAGES_PER_HUB = 6
REQUEST_TIMEOUT_S = 10
SLEEP_BETWEEN_REQUESTS_S = 0.15


def _norm(x: Any) -> str:
    return str(x or "").strip()


def _stable_dedupe(seq: List[str]) -> List[str]:
    out: List[str] = []
    seen: Set[str] = set()
    for s in seq:
        t = (s or "").strip()
        if not t:
            continue
        k = t.lower()
        if k in seen:
            continue
        seen.add(k)
        out.append(t)
    return out


def _extract_urls_from_text(text: str) -> List[str]:
    return _stable_dedupe(URL_RE.findall(text or ""))


def _extract_hrefs(html: str) -> List[str]:
    return _stable_dedupe(HREF_RE.findall(html or ""))


def _to_absolute(base_url: str, maybe_url: str) -> Optional[str]:
    u = (maybe_url or "").strip()
    if not u:
        return None
    if u.startswith("#") or u.lower().startswith("mailto:") or u.lower().startswith("javascript:"):
        return None
    absu = urljoin(base_url, u)
    if not absu.lower().startswith(("http://", "https://")):
        return None
    return absu


def _same_domain(a: str, b: str) -> bool:
    try:
        na = urlparse(a).netloc.lower()
        nb = urlparse(b).netloc.lower()
        return bool(na) and na == nb
    except Exception:
        return False


def _is_github_repo(url: str) -> bool:
    return bool(GITHUB_REPO_RE.match(url or ""))


def _classify_person_url(url: str) -> Tuple[str, str]:
    u = (url or "").strip()

    m = LINKEDIN_IN_RE.match(u)
    if m:
        return ("linkedin", m.group(2).strip())

    m = ORCID_RE.match(u)
    if m:
        return ("orcid", m.group(2).strip())

    m = SCHOLAR_USER_RE.match(u)
    if m:
        return ("scholar", m.group(2).strip())

    m = SEMANTIC_AUTHOR_RE.match(u)
    if m:
        return ("semantic_scholar", m.group(2).strip())

    m = GITHUB_USER_RE.match(u)
    if m and not _is_github_repo(u):
        handle = m.group(2).strip()
        if handle.lower() in GITHUB_IGNORE:
            return ("unknown", "")
        return ("github", handle)

    return ("unknown", "")


def _candidate_internal_pages(base_url: str, abs_links: List[str]) -> List[str]:
    base = (base_url or "").strip()
    links = [u for u in abs_links if _same_domain(base, u)]
    links = _stable_dedupe(links)

    scored: List[Tuple[int, str]] = []
    for u in links:
        path = urlparse(u).path or ""
        score = 0
        if TEAM_HINT_RE.search(path):
            score += 2
        if "people" in path.lower():
            score += 2
        if "team" in path.lower():
            score += 2
        if "research" in path.lower():
            score += 1
        scored.append((score, u))

    scored.sort(key=lambda t: (-t[0], t[1].lower()))
    candidates = [u for (s, u) in scored if s > 0]
    return candidates


@dataclass(frozen=True)
class DiscoveryRow:
    source_hub_url: str
    source_page_url: str
    discovered_person_url: str
    kind: str
    handle_or_id: str
    provenance: Dict[str, Any]


def _fetch(url: str) -> str:
    headers = {
        "User-Agent": "AI-Talent-Engine/1.0 (public research; contact: none)",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    }
    r = requests.get(url, headers=headers, timeout=REQUEST_TIMEOUT_S)
    r.raise_for_status()
    return r.text or ""


def process_csv(input_csv: str | Path, output_csv: str | Path) -> None:
    inp = Path(input_csv)
    outp = Path(output_csv)

    if not inp.exists():
        raise FileNotFoundError(f"people_discovery_from_hubs: input CSV not found: {inp}")
    outp.parent.mkdir(parents=True, exist_ok=True)

    with inp.open(newline="", encoding="utf-8") as fin:
        reader = csv.DictReader(fin)
        fieldnames = list(reader.fieldnames or [])
        rows: List[Dict[str, str]] = list(reader)

    if not fieldnames:
        raise RuntimeError(f"people_discovery_from_hubs: input CSV has no header: {inp}")

    # Partition GitHub hubs
    github_people_rows: List[Dict[str, str]] = []
    github_repo_rows: List[Dict[str, str]] = []
    other_rows: List[Dict[str, str]] = []

    for r in rows:
        t = _norm(r.get("Seed_Hub_Type") or r.get("Seed_Hub_Class") or "")
        u = _norm(r.get("Seed_Hub_URL") or r.get("URL") or "")
        tl = t.lower()
        ul = u.lower()

        if "github org people" in tl or ("github.com/orgs/" in ul and "/people" in ul):
            github_people_rows.append(r)
        elif "github org repos" in tl or ("github.com/orgs/" in ul and "/repositories" in ul):
            github_repo_rows.append(r)
        else:
            other_rows.append(r)

    discoveries: List[DiscoveryRow] = []
    seen_person: Set[str] = set()

    # 1) GitHub Org People adapter (public members)
    gh_people = []
    if github_people_rows:
        gh_people = discover_people_from_hub_rows(github_people_rows)

    # 2) If empty, fallback to repo contributors adapter
    gh_contrib = []
    if not gh_people and github_repo_rows:
        gh_contrib = discover_contributors_from_hub_rows(github_repo_rows)

    # Ingest adapter results into discoveries
    for p in (gh_people or []):
        gh_url = _norm(p.get("GitHub_URL"))
        gh_user = _norm(p.get("GitHub_Username"))
        org = _norm(p.get("Source_Org"))
        api = _norm(p.get("Source_API_URL"))
        if not gh_url or not gh_user:
            continue
        lk = gh_url.lower()
        if lk in seen_person:
            continue
        seen_person.add(lk)
        prov = {
            "Discovered_Person_URL": {"source": api, "method": "github_api_org_members"},
            "Kind": {"source": "classifier", "method": "github_org_people_adapter"},
            "Handle_Or_ID": {"source": api, "method": "parse_login"},
            "Seed_Query_Or_Handle": {"source": "GitHub_Username", "method": "assign_handle"},
            "Source_Org": {"source": "anchors_row_fields", "method": "parse_org"},
        }
        discoveries.append(DiscoveryRow(f"https://github.com/orgs/{org}/people" if org else "", api, gh_url, "github", gh_user, prov))

    for p in (gh_contrib or []):
        gh_url = _norm(p.get("GitHub_URL"))
        gh_user = _norm(p.get("GitHub_Username"))
        org = _norm(p.get("Source_Org"))
        api = _norm(p.get("Source_API_URL"))
        repo_full = _norm(p.get("Source_Repo_FullName"))
        if not gh_url or not gh_user:
            continue
        lk = gh_url.lower()
        if lk in seen_person:
            continue
        seen_person.add(lk)
        prov = {
            "Discovered_Person_URL": {"source": api, "method": "github_api_repo_contributors"},
            "Kind": {"source": "classifier", "method": "github_org_repo_contributors_adapter"},
            "Handle_Or_ID": {"source": api, "method": "parse_login"},
            "Seed_Query_Or_Handle": {"source": "GitHub_Username", "method": "assign_handle"},
            "Source_Org": {"source": "anchors_row_fields", "method": "parse_org"},
            "Source_Repo_FullName": {"source": api, "method": f"repo_context:{repo_full}"},
        }
        discoveries.append(DiscoveryRow(f"https://github.com/orgs/{org}/repositories" if org else "", api, gh_url, "github", gh_user, prov))

    # 3) Web fallback for non-GitHub hubs (unchanged)
    hub_candidates: List[str] = []
    for r in other_rows:
        for k in ("URL", "Seed_Hub_URL", "Hub_URL", "Source_Hub_URL"):
            v = _norm(r.get(k))
            if v.lower().startswith(("http://", "https://")):
                hub_candidates.append(v)
        blob = " ".join(_norm(v) for v in r.values())
        hub_candidates.extend(_extract_urls_from_text(blob))

    hub_candidates = _stable_dedupe(hub_candidates)

    def hub_sort_key(u: str) -> Tuple[int, str]:
        lu = u.lower()
        penalty = 0
        if "linkedin.com" in lu:
            penalty += 3
        if "github.com" in lu:
            penalty += 2
        if "scholar.google.com" in lu or "semanticscholar.org" in lu or "orcid.org" in lu:
            penalty += 2
        return (penalty, lu)

    hub_candidates.sort(key=hub_sort_key)
    hub_candidates = hub_candidates[:MAX_HUBS]

    for hub_url in hub_candidates:
        pages_fetched = 0

        try:
            html = _fetch(hub_url)
            pages_fetched += 1
            time.sleep(SLEEP_BETWEEN_REQUESTS_S)
        except Exception:
            continue

        raw_links = _extract_hrefs(html) + _extract_urls_from_text(html)
        abs_links: List[str] = []
        for l in raw_links:
            a = _to_absolute(hub_url, l)
            if a:
                abs_links.append(a)
        abs_links = _stable_dedupe(abs_links)

        for u in abs_links:
            kind, hid = _classify_person_url(u)
            if kind == "unknown":
                continue
            lk = u.lower()
            if lk in seen_person:
                continue
            seen_person.add(lk)
            prov = {
                "Discovered_Person_URL": {"source": hub_url, "method": "html_link_extract"},
                "Kind": {"source": "classifier", "method": "regex_classify"},
                "Handle_Or_ID": {"source": "classifier", "method": "regex_parse"},
                "Seed_Query_Or_Handle": {"source": "Handle_Or_ID", "method": "assign_handle"},
            }
            discoveries.append(DiscoveryRow(hub_url, hub_url, u, kind, hid, prov))

        internal_pages = _candidate_internal_pages(hub_url, abs_links)
        internal_pages = internal_pages[: max(0, MAX_PAGES_PER_HUB - pages_fetched)]

        for page_url in internal_pages:
            if pages_fetched >= MAX_PAGES_PER_HUB:
                break
            try:
                html2 = _fetch(page_url)
                pages_fetched += 1
                time.sleep(SLEEP_BETWEEN_REQUESTS_S)
            except Exception:
                continue

            raw2 = _extract_hrefs(html2) + _extract_urls_from_text(html2)
            abs2: List[str] = []
            for l in raw2:
                a = _to_absolute(page_url, l)
                if a:
                    abs2.append(a)
            abs2 = _stable_dedupe(abs2)

            for u in abs2:
                kind, hid = _classify_person_url(u)
                if kind == "unknown":
                    continue
                lk = u.lower()
                if lk in seen_person:
                    continue
                seen_person.add(lk)
                prov = {
                    "Discovered_Person_URL": {"source": page_url, "method": "html_link_extract"},
                    "Kind": {"source": "classifier", "method": "regex_classify"},
                    "Handle_Or_ID": {"source": "classifier", "method": "regex_parse"},
                    "Seed_Query_Or_Handle": {"source": "Handle_Or_ID", "method": "assign_handle"},
                }
                discoveries.append(DiscoveryRow(hub_url, page_url, u, kind, hid, prov))

    if not discoveries:
        raise RuntimeError(
            "people_discovery_from_hubs: ZERO people discovered from anchors.\n"
            f"Input: {inp}\n"
            "GitHub org members may be hidden AND repos may have limited public contributors.\n"
            "Adjust anchor sources (HF orgs, conference pages) if needed."
        )

    # deterministic sort
    discoveries.sort(key=lambda d: (d.kind, d.handle_or_id.lower(), d.discovered_person_url.lower()))

    out_fields = [
        "Source_Hub_URL",
        "Source_Page_URL",
        "Discovered_Person_URL",
        "Kind",
        "Handle_Or_ID",
        "Seed_Query_Or_Handle",
        "GitHub_Username",
        "GitHub_URL",
        "LinkedIn_Public_URL",
        "Google_Scholar_URL",
        "Semantic_Scholar_URL",
        "ORCID_URL",
        "Field_Level_Provenance_JSON",
    ]

    with outp.open("w", newline="", encoding="utf-8") as fout:
        w = csv.DictWriter(fout, fieldnames=out_fields)
        w.writeheader()
        for d in discoveries:
            row = {k: "" for k in out_fields}
            row["Source_Hub_URL"] = d.source_hub_url
            row["Source_Page_URL"] = d.source_page_url
            row["Discovered_Person_URL"] = d.discovered_person_url
            row["Kind"] = d.kind
            row["Handle_Or_ID"] = d.handle_or_id
            row["Seed_Query_Or_Handle"] = d.handle_or_id

            if d.kind == "github":
                row["GitHub_Username"] = d.handle_or_id
                row["GitHub_URL"] = d.discovered_person_url
            elif d.kind == "linkedin":
                row["LinkedIn_Public_URL"] = d.discovered_person_url
            elif d.kind == "scholar":
                row["Google_Scholar_URL"] = d.discovered_person_url
            elif d.kind == "semantic_scholar":
                row["Semantic_Scholar_URL"] = d.discovered_person_url
            elif d.kind == "orcid":
                row["ORCID_URL"] = d.discovered_person_url

            row["Field_Level_Provenance_JSON"] = json.dumps(d.provenance, sort_keys=True)
            w.writerow(row)


__all__ = ["process_csv"]
