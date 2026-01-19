#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI Talent Engine — Deep Personal Artifact Scrape (Day 1 MVP)
Maintainer: L. David Mendoza © 2025
Module: EXECUTION_CORE/deep_personal_artifact_scrape.py
Version: v0.1.0-day1
Created: 2026-01-13

PURPOSE
Implements a deterministic, demo-safe deep scraping MVP that:
- Discovers GitHub Pages (github.io) for a GitHub username
- Discovers one personal domain from known profile URLs (if provided)
- Crawls same-domain pages with strict depth + page caps
- Extracts:
  - Full name (best-effort from page title / h1)
  - Public email addresses (including basic obfuscation)
  - CV/Resume URLs (PDF/HTML)
- Emits provenance per extracted field
- Emits crawl log (visited/skipped/stop reason)
- Produces non-overwrite updates only (never overwrites existing values)

NON-GOALS (Day 1 MVP)
- No patents, conferences, scholar scraping
- No phone extraction
- No multi-domain hop beyond one selected personal domain
- No ranking logic, no scoring logic

CHANGELOG
- v0.1.0-day1: Initial MVP implementation

SECURITY / SAFETY
- Only follows http(s) links
- Same-domain only per crawl root
- Depth-limited BFS (deterministic ordering)
- Hard cap on pages visited
- Timeouts and size caps to avoid stalls
"""

from __future__ import annotations

import hashlib
import html
import json
import re
import time
import urllib.parse
import urllib.request
from dataclasses import dataclass, field
from typing import Dict, Iterable, List, Optional, Set, Tuple


DEFAULT_UA = (
    "AI-Talent-Engine/DeepScrapeDay1 (public-evidence-only; "
    "contact-discovery=published-only)"
)

EMAIL_REGEX = re.compile(
    r"""(?ix)
    (?<![A-Z0-9._%+-])
    ([A-Z0-9._%+-]{1,64})
    \s*
    (?:@|\(at\)|\[at\]|\sat\s|\s*\{at\}\s*)
    \s*
    ([A-Z0-9.-]{1,255})
    \s*
    (?:\.|\(dot\)|\[dot\]|\sdot\s|\s*\{dot\}\s*)
    \s*
    ([A-Z]{2,63})
    (?![A-Z0-9._%+-])
    """
)

# Explicit mailto handler (often simplest / highest precision)
MAILTO_REGEX = re.compile(r"(?i)mailto:([^\s\"\'<>]+)")

# CV / Resume link heuristics
CV_HINT_REGEX = re.compile(r"(?i)\b(cv|resume|résumé|curriculum|vitae)\b")
PDF_REGEX = re.compile(r"(?i)\.pdf(?:$|\?)")

# Simple HTML link extraction without external deps
HREF_REGEX = re.compile(r'(?is)\bhref\s*=\s*["\']([^"\']+)["\']')


@dataclass
class ExtractedValue:
    value: str
    source_url: str
    method: str  # e.g., "mailto", "regex", "link_heuristic", "title", "h1"


@dataclass
class CrawlLog:
    pages_visited: List[str] = field(default_factory=list)
    pages_skipped: List[str] = field(default_factory=list)
    stop_reason: str = ""  # depth_limit | page_cap | no_links | error


@dataclass
class PersonDeepScrapeResult:
    person_id: str
    github_username: Optional[str] = None
    discovered_github_io_url: Optional[str] = None
    discovered_personal_domain: Optional[str] = None
    full_name: Optional[ExtractedValue] = None
    emails: List[ExtractedValue] = field(default_factory=list)
    cv_urls: List[ExtractedValue] = field(default_factory=list)
    crawl_log: CrawlLog = field(default_factory=CrawlLog)

    def to_json(self) -> Dict:
        return {
            "person_id": self.person_id,
            "github_username": self.github_username,
            "discovered": {
                "github_io_url": self.discovered_github_io_url,
                "personal_domain": self.discovered_personal_domain,
                "full_name": (
                    None
                    if self.full_name is None
                    else {
                        "value": self.full_name.value,
                        "source_url": self.full_name.source_url,
                        "method": self.full_name.method,
                    }
                ),
                "emails": [
                    {"value": e.value, "source_url": e.source_url, "method": e.method}
                    for e in self.emails
                ],
                "cv_urls": [
                    {"value": c.value, "source_url": c.source_url, "method": c.method}
                    for c in self.cv_urls
                ],
            },
            "crawl_log": {
                "pages_visited": self.crawl_log.pages_visited,
                "pages_skipped": self.crawl_log.pages_skipped,
                "stop_reason": self.crawl_log.stop_reason,
            },
        }


def _stable_dedupe(items: Iterable[str]) -> List[str]:
    seen: Set[str] = set()
    out: List[str] = []
    for x in items:
        if x not in seen:
            seen.add(x)
            out.append(x)
    return out


def _normalize_url(url: str, base: Optional[str] = None) -> Optional[str]:
    url = (url or "").strip()
    if not url:
        return None

    # Handle relative URLs
    if base:
        url = urllib.parse.urljoin(base, url)

    # Remove fragments
    parsed = urllib.parse.urlparse(url)
    if parsed.scheme not in ("http", "https"):
        return None

    # Normalize: lowercase scheme/host, keep path/query
    host = (parsed.hostname or "").lower()
    if not host:
        return None

    norm = urllib.parse.urlunparse(
        (
            parsed.scheme.lower(),
            host if parsed.port in (None, 80, 443) else f"{host}:{parsed.port}",
            parsed.path or "/",
            "",  # params unused
            parsed.query or "",
            "",  # fragment removed
        )
    )
    return norm


def _same_domain(url: str, domain: str) -> bool:
    try:
        host = urllib.parse.urlparse(url).hostname or ""
    except Exception:
        return False
    host = host.lower()
    domain = domain.lower()
    return host == domain or host.endswith("." + domain)


def _get_domain(url: str) -> Optional[str]:
    try:
        host = urllib.parse.urlparse(url).hostname
        return host.lower() if host else None
    except Exception:
        return None


def _fetch_url(
    url: str,
    timeout_s: float = 10.0,
    max_bytes: int = 2_000_000,
    user_agent: str = DEFAULT_UA,
) -> Tuple[Optional[str], Optional[str]]:
    """
    Returns (text, content_type). Text is decoded as utf-8 with errors replaced.
    Hard caps bytes for safety.
    """
    req = urllib.request.Request(url, headers={"User-Agent": user_agent})
    try:
        with urllib.request.urlopen(req, timeout=timeout_s) as resp:
            ctype = resp.headers.get("Content-Type", "") or ""
            raw = resp.read(max_bytes + 1)
            if len(raw) > max_bytes:
                return None, ctype  # too large, treat as skipped
            try:
                txt = raw.decode("utf-8", errors="replace")
            except Exception:
                txt = raw.decode(errors="replace")
            return txt, ctype
    except Exception:
        return None, None


def _extract_links(html_text: str, base_url: str) -> List[str]:
    links: List[str] = []
    for m in HREF_REGEX.finditer(html_text or ""):
        href = m.group(1)
        norm = _normalize_url(href, base=base_url)
        if norm:
            links.append(norm)
    # Deterministic ordering
    links = sorted(_stable_dedupe(links))
    return links


def _extract_title(html_text: str) -> Optional[str]:
    m = re.search(r"(?is)<title[^>]*>(.*?)</title>", html_text or "")
    if not m:
        return None
    title = re.sub(r"(?is)<[^>]+>", " ", m.group(1))
    title = html.unescape(title)
    title = re.sub(r"\s+", " ", title).strip()
    return title or None


def _extract_h1(html_text: str) -> Optional[str]:
    m = re.search(r"(?is)<h1[^>]*>(.*?)</h1>", html_text or "")
    if not m:
        return None
    h1 = re.sub(r"(?is)<[^>]+>", " ", m.group(1))
    h1 = html.unescape(h1)
    h1 = re.sub(r"\s+", " ", h1).strip()
    return h1 or None


def _extract_emails(html_text: str, source_url: str) -> List[ExtractedValue]:
    out: List[ExtractedValue] = []

    # mailto first (high precision)
    for mm in MAILTO_REGEX.finditer(html_text or ""):
        addr = mm.group(1).strip()
        addr = addr.split("?")[0]
        addr = addr.replace("%40", "@").replace("%2B", "+")
        if "@" in addr and len(addr) <= 320:
            out.append(ExtractedValue(value=addr, source_url=source_url, method="mailto"))

    # de-obfuscation regex (basic)
    for em in EMAIL_REGEX.finditer(html_text or ""):
        local, dom, tld = em.group(1), em.group(2), em.group(3)
        candidate = f"{local}@{dom}.{tld}".lower()
        candidate = re.sub(r"\s+", "", candidate)
        if len(candidate) <= 320 and "." in dom and "@" in candidate:
            out.append(ExtractedValue(value=candidate, source_url=source_url, method="regex_obfus"))

    # stable dedupe by value+source
    seen: Set[Tuple[str, str]] = set()
    dedup: List[ExtractedValue] = []
    for e in out:
        key = (e.value.lower(), e.source_url)
        if key not in seen:
            seen.add(key)
            dedup.append(e)
    return dedup


def _extract_cv_links(links: List[str], source_url: str) -> List[ExtractedValue]:
    out: List[ExtractedValue] = []
    for u in links:
        path = urllib.parse.urlparse(u).path or ""
        if PDF_REGEX.search(u) or CV_HINT_REGEX.search(path) or CV_HINT_REGEX.search(u):
            out.append(ExtractedValue(value=u, source_url=source_url, method="link_heuristic"))
    # stable dedupe by url
    seen: Set[str] = set()
    dedup: List[ExtractedValue] = []
    for c in out:
        if c.value not in seen:
            seen.add(c.value)
            dedup.append(c)
    return dedup


def discover_github_io_url(github_username: str, timeout_s: float = 6.0) -> Optional[str]:
    """
    Deterministically checks https://{username}.github.io
    """
    if not github_username:
        return None
    candidate = f"https://{github_username.strip().lower()}.github.io/"
    txt, ctype = _fetch_url(candidate, timeout_s=timeout_s, max_bytes=250_000)
    if txt is None:
        return None
    # If we got a response body, we treat as exists.
    return candidate


def select_one_personal_domain(
    candidate_urls: Iterable[str],
) -> Optional[str]:
    """
    Given an iterable of URLs (from profile fields), pick ONE personal domain.
    Excludes obvious social / aggregator domains.
    """
    deny = {
        "linkedin.com",
        "twitter.com",
        "x.com",
        "medium.com",
        "substack.com",
        "scholar.google.com",
        "github.com",
        "huggingface.co",
    }
    normed: List[str] = []
    for u in candidate_urls or []:
        nu = _normalize_url(u)
        if nu:
            normed.append(nu)

    # Deterministic selection: first valid domain after sorting
    normed = sorted(_stable_dedupe(normed))
    for u in normed:
        dom = _get_domain(u)
        if not dom:
            continue
        if any(dom == d or dom.endswith("." + d) for d in deny):
            continue
        return dom
    return None


def crawl_domain_extract(
    start_urls: List[str],
    root_domain: str,
    max_depth: int = 2,
    max_pages: int = 20,
    timeout_s: float = 10.0,
    politeness_delay_s: float = 0.2,
) -> Tuple[List[ExtractedValue], List[ExtractedValue], Optional[ExtractedValue], CrawlLog]:
    """
    BFS crawl within root_domain. Deterministic ordering (sorted links).
    Extract emails + CV urls + best-effort name (title/h1).
    """
    log = CrawlLog()
    emails: List[ExtractedValue] = []
    cvs: List[ExtractedValue] = []
    best_name: Optional[ExtractedValue] = None

    # BFS queue: (url, depth)
    q: List[Tuple[str, int]] = []
    seen: Set[str] = set()

    # normalize + filter same-domain
    normalized_starts: List[str] = []
    for u in start_urls:
        nu = _normalize_url(u)
        if nu and _same_domain(nu, root_domain):
            normalized_starts.append(nu)

    for u in sorted(_stable_dedupe(normalized_starts)):
        if u not in seen:
            seen.add(u)
            q.append((u, 0))

    if not q:
        log.stop_reason = "no_links"
        return emails, cvs, best_name, log

    while q:
        url, depth = q.pop(0)
        if len(log.pages_visited) >= max_pages:
            log.stop_reason = "page_cap"
            break

        if depth > max_depth:
            log.stop_reason = "depth_limit"
            break

        txt, ctype = _fetch_url(url, timeout_s=timeout_s, max_bytes=2_000_000)
        if txt is None:
            log.pages_skipped.append(url)
            continue

        # Skip non-HTML by content-type heuristic
        ctype_l = (ctype or "").lower()
        if "text/html" not in ctype_l and "<html" not in (txt[:500].lower()):
            log.pages_skipped.append(url)
            continue

        log.pages_visited.append(url)

        # Extract name candidate
        if best_name is None:
            title = _extract_title(txt)
            h1 = _extract_h1(txt)
            # Prefer h1 if reasonably short
            candidate = h1 if (h1 and 2 <= len(h1) <= 80) else title
            if candidate and 2 <= len(candidate) <= 80:
                best_name = ExtractedValue(value=candidate, source_url=url, method="h1/title")

        # Extract emails
        emails.extend(_extract_emails(txt, url))

        # Extract links
        links = _extract_links(txt, url)
        cvs.extend(_extract_cv_links(links, url))

        # Enqueue next URLs
        if depth < max_depth:
            for lk in links:
                if not _same_domain(lk, root_domain):
                    continue
                if lk in seen:
                    continue
                # Skip obvious asset types
                if re.search(r"(?i)\.(png|jpg|jpeg|gif|webp|svg|css|js|ico|mp4|mov|zip)$", lk):
                    continue
                seen.add(lk)
                q.append((lk, depth + 1))

        time.sleep(politeness_delay_s)

    if not log.stop_reason:
        log.stop_reason = "no_links"

    # Stable dedupe emails/cvs
    emails = _stable_dedupe_extracted(emails)
    cvs = _stable_dedupe_extracted(cvs)
    return emails, cvs, best_name, log


def _stable_dedupe_extracted(items: List[ExtractedValue]) -> List[ExtractedValue]:
    seen: Set[Tuple[str, str]] = set()
    out: List[ExtractedValue] = []
    for it in items:
        key = (it.value.strip().lower(), it.source_url)
        if key not in seen:
            seen.add(key)
            out.append(it)
    return out


def deep_scrape_person(
    person_id: str,
    github_username: Optional[str],
    candidate_profile_urls: Optional[List[str]] = None,
    existing_emails: Optional[List[str]] = None,
    existing_cv_urls: Optional[List[str]] = None,
    enable_github_io: bool = True,
    max_depth: int = 2,
    max_pages: int = 20,
) -> PersonDeepScrapeResult:
    """
    Core API for Day 1 MVP. Returns a PersonDeepScrapeResult containing discovered artifacts
    plus crawl logs and provenance. Does NOT overwrite existing values. Instead, caller can
    apply non-overwrite merge using merge_non_overwrite_updates().
    """
    res = PersonDeepScrapeResult(person_id=person_id, github_username=github_username)

    existing_emails_l = set((e or "").strip().lower() for e in (existing_emails or []) if e)
    existing_cv_l = set((u or "").strip() for u in (existing_cv_urls or []) if u)

    start_urls: List[str] = []
    personal_domain: Optional[str] = None

    # 1) github.io discovery
    if enable_github_io and github_username:
        ghio = discover_github_io_url(github_username)
        if ghio:
            res.discovered_github_io_url = ghio
            start_urls.append(ghio)

    # 2) select one personal domain (if provided)
    personal_domain = select_one_personal_domain(candidate_profile_urls or [])
    if personal_domain:
        res.discovered_personal_domain = personal_domain
        start_urls.append(f"https://{personal_domain}/")

    # 3) crawl each root independently (same-domain enforced per root)
    # For Day 1 MVP: crawl github.io domain first if exists, then personal domain.
    extracted_emails: List[ExtractedValue] = []
    extracted_cvs: List[ExtractedValue] = []
    best_name: Optional[ExtractedValue] = None
    combined_log = CrawlLog()

    for root in _stable_dedupe(start_urls):
        dom = _get_domain(root)
        if not dom:
            continue
        e, c, n, log = crawl_domain_extract(
            start_urls=[root],
            root_domain=dom,
            max_depth=max_depth,
            max_pages=max_pages,
        )
        combined_log.pages_visited.extend(log.pages_visited)
        combined_log.pages_skipped.extend(log.pages_skipped)
        combined_log.stop_reason = log.stop_reason or combined_log.stop_reason

        extracted_emails.extend(e)
        extracted_cvs.extend(c)
        if best_name is None and n is not None:
            best_name = n

    # Apply non-overwrite filtering (we keep only new values)
    for e in _stable_dedupe_extracted(extracted_emails):
        if e.value.strip().lower() not in existing_emails_l:
            res.emails.append(e)

    for c in _stable_dedupe_extracted(extracted_cvs):
        if c.value.strip() not in existing_cv_l:
            res.cv_urls.append(c)

    # Name is only provided if caller doesn't already have one; caller decides.
    res.full_name = best_name
    res.crawl_log = combined_log
    return res


def merge_non_overwrite_updates(
    existing_row: Dict[str, object],
    scrape_result: PersonDeepScrapeResult,
    email_field: str = "Public_Email",
    cv_field: str = "CV_URL",
    github_io_field: str = "GitHub_IO_URL",
    provenance_field: str = "Deep_Scrape_Provenance_JSON",
) -> Dict[str, object]:
    """
    Returns a dict of updates to apply to an existing row, without overwriting.
    The caller applies updates to their dataframe/row only where current values are blank.
    """
    updates: Dict[str, object] = {}

    # GitHub_IO_URL (non-overwrite)
    if github_io_field in existing_row:
        cur = (existing_row.get(github_io_field) or "").strip()
        if not cur and scrape_result.discovered_github_io_url:
            updates[github_io_field] = scrape_result.discovered_github_io_url

    # Public_Email (non-overwrite, append-first behavior)
    if email_field in existing_row and scrape_result.emails:
        cur = (existing_row.get(email_field) or "").strip()
        if not cur:
            # Join multiple emails with " | " for readability
            updates[email_field] = " | ".join([e.value for e in scrape_result.emails])

    # CV_URL (non-overwrite)
    if cv_field in existing_row and scrape_result.cv_urls:
        cur = (existing_row.get(cv_field) or "").strip()
        if not cur:
            updates[cv_field] = scrape_result.cv_urls[0].value

    # Provenance JSON (always safe to write if blank)
    if provenance_field in existing_row:
        cur = (existing_row.get(provenance_field) or "").strip()
        if not cur:
            updates[provenance_field] = json.dumps(scrape_result.to_json(), ensure_ascii=False)

    return updates


def stable_person_hash(person_id: str, github_username: Optional[str]) -> str:
    """
    Deterministic hash used for caching keys.
    """
    s = f"{person_id}::{(github_username or '').strip().lower()}"
    return hashlib.sha256(s.encode("utf-8")).hexdigest()[:16]
