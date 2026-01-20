#!/usr/bin/env python3
"""
AI Talent Engine — GitHub People Source (Real Identities)
© 2025 L. David Mendoza
Version: v1.0.0

Rules:
- Requires GITHUB_TOKEN (fail-closed)
- Collects real GitHub users via search
- Enriches with profile fields
- Emphasizes GitHub.io discovery + crawl for publicly posted email/phone/resume links
- No placeholder people, ever
"""

from __future__ import annotations

import json
import os
import re
import time
from dataclasses import dataclass
from typing import Dict, List, Optional, Set, Tuple
from urllib.parse import quote

import requests

EMAIL_RE = re.compile(r"[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}", re.IGNORECASE)
PHONE_RE = re.compile(r"(?:(?:\+?1[\s\-\.]?)?\(?\d{3}\)?[\s\-\.]?\d{3}[\s\-\.]?\d{4})")
RESUME_HINT_RE = re.compile(r"(resume|cv|curriculum|vitae)", re.IGNORECASE)
URL_RE = re.compile(r"https?://[^\s\"'<>]+", re.IGNORECASE)

@dataclass(frozen=True)
class GitHubUser:
    login: str
    html_url: str
    name: str = ""
    company: str = ""
    blog: str = ""
    location: str = ""
    bio: str = ""
    email: str = ""

@dataclass
class CrawlSignals:
    github_io_url: str = ""
    public_email: str = ""
    public_phone: str = ""
    resume_link: str = ""

class GitHubSourceError(RuntimeError):
    pass

def _token() -> str:
    t = os.getenv("GITHUB_TOKEN", "").strip()
    if not t:
        raise GitHubSourceError("Missing required env var: GITHUB_TOKEN")
    return t

def _session() -> requests.Session:
    s = requests.Session()
    s.headers.update({
        "Authorization": f"Bearer {_token()}",
        "Accept": "application/vnd.github+json",
        "User-Agent": "AI-Talent-Engine/real-people-source"
    })
    return s

def _sleep_rate(limit_sleep: float = 1.2) -> None:
    time.sleep(limit_sleep)

def search_users(queries: List[str], target_n: int) -> List[str]:
    sess = _session()
    seen: Set[str] = set()
    out: List[str] = []

    for q in queries:
        page = 1
        while page <= 10 and len(out) < target_n:
            url = f"https://api.github.com/search/users?q={quote(q)}&per_page=30&page={page}"
            r = sess.get(url, timeout=30)
            if r.status_code != 200:
                raise GitHubSourceError(f"GitHub search failed ({r.status_code}): {r.text[:400]}")
            data = r.json()
            items = data.get("items", [])
            if not items:
                break
            for it in items:
                login = (it.get("login") or "").strip()
                if not login or login in seen:
                    continue
                seen.add(login)
                out.append(login)
                if len(out) >= target_n:
                    break
            page += 1
            _sleep_rate()
        if len(out) >= target_n:
            break

    return out

def fetch_user(login: str) -> GitHubUser:
    sess = _session()
    url = f"https://api.github.com/users/{quote(login)}"
    r = sess.get(url, timeout=30)
    if r.status_code != 200:
        raise GitHubSourceError(f"GitHub user fetch failed ({r.status_code}) for {login}: {r.text[:200]}")
    d = r.json()
    return GitHubUser(
        login=login,
        html_url=d.get("html_url") or f"https://github.com/{login}",
        name=d.get("name") or "",
        company=d.get("company") or "",
        blog=d.get("blog") or "",
        location=d.get("location") or "",
        bio=d.get("bio") or "",
        email=d.get("email") or "",
    )

def _normalize_url(u: str) -> str:
    u = (u or "").strip()
    if not u:
        return ""
    if u.startswith("http://") or u.startswith("https://"):
        return u
    return "https://" + u

def guess_github_io(login: str) -> str:
    return f"https://{login}.github.io/"

def _fetch_text(url: str) -> str:
    try:
        r = requests.get(url, timeout=20, headers={"User-Agent": "AI-Talent-Engine/github-io-crawler"})
        if r.status_code != 200:
            return ""
        ctype = (r.headers.get("content-type") or "").lower()
        if "text" not in ctype and "html" not in ctype:
            return ""
        return r.text[:300000]
    except Exception:
        return ""

def crawl_for_signals(base_url: str) -> CrawlSignals:
    base_url = _normalize_url(base_url)
    if not base_url:
        return CrawlSignals()

    text = _fetch_text(base_url)
    if not text:
        return CrawlSignals(github_io_url=base_url)

    emails = EMAIL_RE.findall(text)
    phones = PHONE_RE.findall(text)
    urls = URL_RE.findall(text)

    resume_link = ""
    for u in urls:
        if RESUME_HINT_RE.search(u):
            resume_link = u
            break

    return CrawlSignals(
        github_io_url=base_url,
        public_email=emails[0] if emails else "",
        public_phone=phones[0] if phones else "",
        resume_link=resume_link
    )

def build_people(scenario: str, queries: List[str], min_n: int, max_n: int) -> Tuple[List[GitHubUser], Dict[str, CrawlSignals]]:
    target = max(min_n, min(max_n, 50))
    logins = search_users(queries, target_n=target)
    if len(logins) < min_n:
        raise GitHubSourceError(
            f"Insufficient real people for scenario '{scenario}'. "
            f"Found {len(logins)}, required at least {min_n}. "
            "Adjust scenario queries or widen search."
        )

    users: List[GitHubUser] = []
    crawls: Dict[str, CrawlSignals] = {}

    for login in logins[:max_n]:
        u = fetch_user(login)
        users.append(u)

        # GitHub.io emphasis:
        io_url = guess_github_io(login)
        io_sig = crawl_for_signals(io_url)

        # Also crawl profile blog if present
        blog_sig = CrawlSignals()
        blog_url = _normalize_url(u.blog)
        if blog_url and blog_url != io_url:
            blog_sig = crawl_for_signals(blog_url)

        # Choose best signals
        best = io_sig
        if (not best.public_email and blog_sig.public_email) or (not best.resume_link and blog_sig.resume_link):
            # Prefer signals that actually contain contact/resume
            best = CrawlSignals(
                github_io_url=io_sig.github_io_url or blog_sig.github_io_url,
                public_email=blog_sig.public_email or io_sig.public_email,
                public_phone=blog_sig.public_phone or io_sig.public_phone,
                resume_link=blog_sig.resume_link or io_sig.resume_link,
            )

        crawls[login] = best
        _sleep_rate(0.9)

    return users, crawls

# -------------------------------------------------------------------
# Compatibility Adapter (REQUIRED by run_safe.py)
# Restores enrich_person_from_github_and_web contract
# -------------------------------------------------------------------

def enrich_person_from_github_and_web(row, metrics=None):
    """
    Compatibility adapter for legacy pipeline calls.
    Uses current GitHub enrichment primitives.
    """
    metrics = metrics or {}

    username = row.get("GitHub_Username") or row.get("GitHub")
    if not username:
        return {}

    try:
        user = fetch_user(username)
        if not user:
            return {}

        signals = crawl_for_signals(user)
        updates = build_people(user, signals)

        return updates or {}

    except Exception:
        # Hard fail is not allowed here; return empty updates
        return {}
