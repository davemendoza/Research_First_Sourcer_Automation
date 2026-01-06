"""
AI Talent Engine | Research-First Sourcer Automation
EXECUTION_CORE/people_source_github.py

Author: © 2026 L. David Mendoza. All rights reserved.
Version: v1.2.0-people-source-github-universal-multilingual-coupling
Date: 2026-01-06

LOCKED PURPOSE
This module is the canonical GitHub and public-web enrichment source for People Pipeline runs.
It must support BOTH:
1) DEMO runs (bounded 25 to 50 real people)
2) SCENARIO runs (unbounded, all available valid people)

It must enforce:
- No synthetic data. No placeholders. No inferred identity. No fabricated contact info.
- Truthful sparsity: if not found publicly, leave blank.
- Multilingual resume/CV/profile detection across ALL crawled evidence surfaces.
- Coupling logic: resume/CV/profile detection must reliably trigger deeper crawling and always invoke email and phone extraction.
- github.io detection and probing for every GitHub handle.
- Bounded crawling for github.io and personal domains (polite, deterministic).
- Mandatory runtime visibility: metrics counters must be updated consistently (the caller prints them).

IMPORTANT INTERFACE CONTRACT
This file MUST remain importable without side effects.

This module provides a single canonical entry function:

    enrich_person_from_github_and_web(person_row: dict, scenario: str, metrics: dict, config: dict | None = None) -> dict

It is designed to be resilient against caller drift:
- Accepts a dict-like row (Phase 1 inventory output) and returns a dict of field updates.
- Never assumes the presence of any particular schema columns.
- Never writes files directly.
- Never calls GPT.
- Never changes execution order outside its own function body.

ENVIRONMENT
- GITHUB_TOKEN (optional, increases GitHub API rate limits)
- SSL_CERT_FILE (optional; supports certifi path if exported)

CHANGELOG
- v1.2.0
  - Enforced universal multilingual triggers across github.io, personal domains, and any discovered internal pages.
  - Enforced coupling: CV/resume/profile detection always invokes deeper crawl and always invokes email and phone extraction.
  - Hardened github.io probing to HEAD-check and fallback GET-check.
  - Added deterministic bounded crawling (domain pages, link cap, bytes cap, sleep).
  - Normalized obfuscated email forms and captured mailto and tel links.
  - Added stable metrics increments for github_ok, github_io, resume_cv, emails, phones, domains_crawled.

VALIDATION (manual, from repo root)
1) python3 -m py_compile EXECUTION_CORE/people_source_github.py
2) python3 -c "from EXECUTION_CORE.people_source_github import enrich_person_from_github_and_web; print('IMPORT_OK')"
3) Run your canonical entrypoint that calls this module:
   - DEMO
     python3 run_people_pipeline.py --scenario frontier_ai_scientist --mode demo
   - SCENARIO
     python3 run_people_pipeline.py --scenario frontier_ai_scientist --mode scenario

GIT (from repo root)
git add EXECUTION_CORE/people_source_github.py
git commit -m "Harden people_source_github: universal multilingual coupling, bounded crawl, metrics"
git push
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import ssl
import time
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from html.parser import HTMLParser
from typing import Dict, Iterable, List, Optional, Tuple


# ----------------------------
# Constants (locked defaults)
# ----------------------------

GITHUB_API = "https://api.github.com"

DEFAULT_TIMEOUT_SEC = 20
MAX_HTML_BYTES = 2_000_000
CRAWL_SLEEP_SEC = 0.35
MAX_LINKS_PER_PAGE = 250
MAX_PAGES_PER_DOMAIN = 4
MAX_VISIT_QUEUE = 80

MAX_EMAILS = 10
MAX_PHONES = 10
MAX_RESUME_URLS = 10
MAX_PORTFOLIO_URLS = 12
MAX_PERSONAL_URLS = 20
MAX_REPOS_TO_SCAN = 12

USER_AGENT = "AI-Talent-Engine/people-source-github"


# ----------------------------
# Multilingual evidence triggers (locked, conservative)
# ----------------------------

# Resume, CV, vitae, profile equivalents (multilingual)
RESUME_TERMS: List[str] = [
    # English
    "resume", "résumé", "cv", "curriculum vitae", "vita", "vitae", "academic cv", "research cv", "faculty cv",
    "short cv", "full cv", "curriculum", "biography", "bio", "about me",
    # Spanish / Portuguese
    "curriculo", "currículo", "curriculo vitae", "hoja de vida", "vida laboral", "trayectoria",
    "perfil profesional", "biografía", "sobre mí", "sobre mi", "contato", "contáctame", "contacto",
    # French
    "parcours", "parcours professionnel", "parcours académique", "profil", "dossier", "biographie", "à propos",
    # German / Italian / Dutch
    "lebenslauf", "profil", "profilo", "curriculum", "über mich", "contatto", "contatti",
    # Japanese / Chinese / Korean
    "履歴書", "職務経歴書", "简历", "个人简介", "个人简历", "履歴", "経歴",
    "이력서", "경력", "자기소개", "소개",
]

# Contact terms (multilingual)
CONTACT_TERMS: List[str] = [
    # English
    "contact", "email", "e-mail", "reach me", "get in touch", "phone", "tel", "mobile",
    # Spanish / Portuguese
    "contacto", "correo", "correo electrónico", "email", "e-mail", "telefone", "teléfono", "móvil", "celular",
    # French
    "contact", "courriel", "e-mail", "téléphone", "portable",
    # German / Italian
    "kontakt", "e-mail", "telefon", "handy", "contatto", "telefono",
    # Japanese / Chinese / Korean
    "連絡", "メール", "電話", "邮箱", "邮件", "电子邮件", "电话", "联系",
    "연락", "이메일", "전화",
]

# URL path hints for deep-link prioritization
HIGH_VALUE_PATH_HINTS: List[str] = [
    "/cv", "/resume", "/vita", "/about", "/bio", "/contact", "/publications", "/papers", "/research", "/talks", "/slides",
]


# ----------------------------
# Regex: identity anchors + contact extraction
# ----------------------------

GITHUB_PROFILE_RE = re.compile(r"(?i)https?://github\.com/([A-Za-z0-9](?:-?[A-Za-z0-9]){0,38})\b")
PDF_RE = re.compile(r"(?i)\.pdf(\?|#|$)")

EMAIL_RE = re.compile(r"(?i)\b[a-z0-9._%+\-]+@[a-z0-9.\-]+\.[a-z]{2,}\b")
PHONE_RE = re.compile(
    r"(?<!\d)(?:\+?\d{1,3}[\s\-\.]?)?(?:\(\d{2,4}\)|\d{2,4})[\s\-\.]?\d{3,4}[\s\-\.]?\d{4}(?!\d)"
)

# Obfuscations like: name [at] domain [dot] edu
OBFUSCATED_AT = re.compile(r"(?i)\s*(?:\[\s*at\s*\]|\(\s*at\s*\)|\s+at\s+)\s*")
OBFUSCATED_DOT = re.compile(r"(?i)\s*(?:\[\s*dot\s*\]|\(\s*dot\s*\)|\s+dot\s+)\s*")


# ----------------------------
# Data structures
# ----------------------------

@dataclass
class HttpResponse:
    url: str
    status: int
    headers: Dict[str, str]
    body: bytes


class LinkExtractor(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.links: List[str] = []

    def handle_starttag(self, tag: str, attrs: List[Tuple[str, Optional[str]]]) -> None:
        if tag.lower() != "a":
            return
        href: Optional[str] = None
        for k, v in attrs:
            if k.lower() == "href":
                href = v
                break
        if href:
            self.links.append(href)


# ----------------------------
# Helpers
# ----------------------------

def _ssl_context() -> ssl.SSLContext:
    return ssl.create_default_context()

def _sha1(s: str) -> str:
    return hashlib.sha1(s.encode("utf-8", errors="ignore")).hexdigest()

def _norm_url(u: str) -> str:
    u = (u or "").strip()
    if not u:
        return ""
    if u.startswith("http://") or u.startswith("https://"):
        return u
    if u.startswith("www."):
        return "https://" + u
    if re.search(r"\.[a-z]{2,}(/|$)", u, re.I):
        return "https://" + u
    return u

def _same_domain(a: str, b: str) -> bool:
    try:
        pa = urllib.parse.urlparse(a)
        pb = urllib.parse.urlparse(b)
        return bool(pa.netloc) and pa.netloc.lower() == pb.netloc.lower()
    except Exception:
        return False

def _resolve_abs(base: str, href: str) -> str:
    href = (href or "").strip()
    if not href:
        return ""
    if href.startswith("mailto:") or href.startswith("tel:"):
        return href
    return urllib.parse.urljoin(base, href)

def _contains_any(text: str, terms: List[str]) -> bool:
    t = (text or "").lower()
    for term in terms:
        if term.lower() in t:
            return True
    return False

def _normalize_obfuscated_emails(text: str) -> str:
    t = text or ""
    t = OBFUSCATED_AT.sub("@", t)
    t = OBFUSCATED_DOT.sub(".", t)
    return t

def _extract_emails(text: str) -> List[str]:
    t = _normalize_obfuscated_emails(text or "")
    return sorted(set(EMAIL_RE.findall(t)))[:MAX_EMAILS]

def _extract_phones(text: str) -> List[str]:
    return sorted(set(PHONE_RE.findall(text or "")))[:MAX_PHONES]

def _is_probably_resume_url(url: str) -> bool:
    u = (url or "").lower()
    if not u:
        return False
    if any(k in u for k in ["resume", "résumé", "curriculum", "vita", "vitae", "lebenslauf", "hoja", "curriculo", "currículo"]):
        return True
    if PDF_RE.search(u) and any(k in u for k in ["resume", "cv", "vita", "lebenslauf", "curriculo", "currículo", "hoja"]):
        return True
    if "/cv" in u or u.endswith("/cv") or u.endswith("/cv/"):
        return True
    return False

def _join_unique(items: Iterable[str], limit: int) -> str:
    out: List[str] = []
    seen: set = set()
    for it in items:
        it = (it or "").strip()
        if not it or it in seen:
            continue
        seen.add(it)
        out.append(it)
        if len(out) >= limit:
            break
    return " | ".join(out)

def _http_get(url: str, headers: Optional[Dict[str, str]] = None, timeout: int = DEFAULT_TIMEOUT_SEC) -> HttpResponse:
    req = urllib.request.Request(url, method="GET")
    for k, v in (headers or {}).items():
        req.add_header(k, v)
    ctx = _ssl_context()
    try:
        with urllib.request.urlopen(req, timeout=timeout, context=ctx) as resp:
            body = resp.read(MAX_HTML_BYTES + 1)
            if len(body) > MAX_HTML_BYTES:
                body = body[:MAX_HTML_BYTES]
            h = {k.lower(): v for k, v in resp.headers.items()}
            return HttpResponse(url=url, status=int(resp.status), headers=h, body=body)
    except urllib.error.HTTPError as he:
        h = {k.lower(): v for k, v in he.headers.items()} if he.headers else {}
        try:
            body = he.read()
        except Exception:
            body = b""
        return HttpResponse(url=url, status=int(he.code), headers=h, body=body)
    except Exception as ex:
        raise RuntimeError(f"GET failed: {url} :: {ex}") from ex

def _http_head(url: str, headers: Optional[Dict[str, str]] = None, timeout: int = DEFAULT_TIMEOUT_SEC) -> int:
    req = urllib.request.Request(url, method="HEAD")
    for k, v in (headers or {}).items():
        req.add_header(k, v)
    ctx = _ssl_context()
    try:
        with urllib.request.urlopen(req, timeout=timeout, context=ctx) as resp:
            return int(resp.status)
    except urllib.error.HTTPError as he:
        return int(he.code)
    except Exception:
        return 0


# ----------------------------
# GitHub API helpers (public, deterministic)
# ----------------------------

def _github_headers() -> Dict[str, str]:
    h = {
        "Accept": "application/vnd.github+json",
        "User-Agent": USER_AGENT,
    }
    tok = os.environ.get("GITHUB_TOKEN", "").strip()
    if tok:
        h["Authorization"] = f"Bearer {tok}"
    return h

def _github_user(username: str) -> Tuple[bool, Dict]:
    url = f"{GITHUB_API}/users/{urllib.parse.quote(username)}"
    resp = _http_get(url, headers=_github_headers())
    if resp.status != 200:
        return False, {}
    try:
        return True, json.loads(resp.body.decode("utf-8", errors="replace"))
    except Exception:
        return True, {}

def _github_repos(username: str) -> List[Dict]:
    url = f"{GITHUB_API}/users/{urllib.parse.quote(username)}/repos?per_page=100&sort=updated"
    resp = _http_get(url, headers=_github_headers())
    if resp.status != 200:
        return []
    try:
        data = json.loads(resp.body.decode("utf-8", errors="replace"))
        return data if isinstance(data, list) else []
    except Exception:
        return []

def _score_repo(repo: Dict) -> Tuple[int, str]:
    name = (repo.get("name") or "").lower()
    desc = (repo.get("description") or "").lower()
    topics = " ".join(repo.get("topics") or []).lower()
    lang = (repo.get("language") or "").lower()
    stars = int(repo.get("stargazers_count") or 0)
    forks = int(repo.get("forks_count") or 0)

    text = f"{name} {desc} {topics} {lang}"
    signals = 0
    for k in ["llm", "transformer", "rag", "retrieval", "embedding", "vector", "pytorch", "jax", "cuda", "triton", "tensorrt", "vllm", "deepspeed", "fsdp", "moe", "quantization", "lora", "qlora", "peft", "rlhf", "dpo"]:
        if k in text:
            signals += 1

    score = 0
    score += min(stars, 300) // 10
    score += min(forks, 300) // 20
    score += min(signals, 6) * 7
    if repo.get("archived"):
        score = max(0, score - 5)

    why: List[str] = []
    if stars:
        why.append(f"{stars}★")
    if forks:
        why.append(f"{forks} forks")
    if signals:
        why.append(f"signal_hits={signals}")
    return score, "; ".join(why)

def _pick_evidential_repos(repos: List[Dict]) -> Tuple[List[str], List[str]]:
    scored: List[Tuple[int, Dict, str]] = []
    for r in repos or []:
        s, why = _score_repo(r)
        scored.append((s, r, why))
    scored.sort(key=lambda x: x[0], reverse=True)
    picked = scored[:MAX_REPOS_TO_SCAN]

    urls: List[str] = []
    whys: List[str] = []
    for s, r, why in picked:
        u = (r.get("html_url") or "").strip()
        if u:
            urls.append(u)
        n = (r.get("name") or "").strip()
        if n and why:
            whys.append(f"{n}: {why}")

    return urls, whys


# ----------------------------
# github.io probe (must run for every handle)
# ----------------------------

def _probe_github_io(username: str) -> str:
    url = f"https://{username}.github.io/"
    status = _http_head(url, headers={"User-Agent": USER_AGENT})
    if 200 <= status < 400:
        return url
    # Fallback GET once, some sites block HEAD
    try:
        resp = _http_get(url, headers={"User-Agent": USER_AGENT}, timeout=DEFAULT_TIMEOUT_SEC)
        if 200 <= resp.status < 400 and resp.body:
            return url
    except Exception:
        pass
    return ""


# ----------------------------
# Bounded crawl engine (universal multilingual coupling)
# ----------------------------

def _crawl_domain_bounded(start_url: str) -> Dict[str, List[str]]:
    """
    Bounded crawl on the same domain. Polite, deterministic.

    Universal coupling rules:
    - Always extract emails and phones from every fetched page.
    - Always collect resume/CV URLs and treat their presence as a deep-crawl trigger.
    - If multilingual resume/CV/profile terms appear anywhere, prioritize high-value pages.

    Returns dict:
      emails, phones, resume_urls, portfolio_urls, personal_urls, triggers
    """
    start_url = _norm_url(start_url)
    if not start_url:
        return {
            "emails": [],
            "phones": [],
            "resume_urls": [],
            "portfolio_urls": [],
            "personal_urls": [],
            "triggers": [],
        }

    emails: List[str] = []
    phones: List[str] = []
    resume_urls: List[str] = []
    portfolio_urls: List[str] = []
    personal_urls: List[str] = []
    triggers: List[str] = []

    visited: set = set()
    queue: List[str] = [start_url]
    pages = 0

    while queue and pages < MAX_PAGES_PER_DOMAIN:
        url = queue.pop(0)
        if url in visited:
            continue
        visited.add(url)

        try:
            resp = _http_get(url, headers={"User-Agent": USER_AGENT}, timeout=DEFAULT_TIMEOUT_SEC)
        except Exception:
            continue

        pages += 1
        time.sleep(CRAWL_SLEEP_SEC)

        # Decode text (simple, safe)
        try:
            text = resp.body.decode("utf-8", errors="replace")
        except Exception:
            text = resp.body.decode(errors="replace")

        text_lower = (text or "").lower()

        # Universal extraction (always)
        emails.extend(_extract_emails(text))
        phones.extend(_extract_phones(text))

        # Trigger detection (multilingual)
        resume_trigger = _contains_any(text_lower, RESUME_TERMS)
        contact_trigger = _contains_any(text_lower, CONTACT_TERMS)
        if resume_trigger:
            triggers.append("resume_terms_present")
        if contact_trigger:
            triggers.append("contact_terms_present")

        # Extract links
        le = LinkExtractor()
        try:
            le.feed(text)
        except Exception:
            pass

        raw_links = le.links[:MAX_LINKS_PER_PAGE]
        abs_links: List[str] = []
        for href in raw_links:
            a = _resolve_abs(url, href)
            if a:
                abs_links.append(a)

        # Classify and queue
        for a in abs_links:
            al = a.lower()

            # mailto/tel always count
            if al.startswith("mailto:"):
                maybe = a.split(":", 1)[1].strip()
                emails.extend(_extract_emails(maybe))
                continue
            if al.startswith("tel:"):
                maybe = a.split(":", 1)[1].strip()
                phones.extend(_extract_phones(maybe))
                continue

            # resume/cv capture
            if _is_probably_resume_url(a) or any(term in al for term in ["cv", "resume", "vita", "lebenslauf", "curriculo", "currículo", "hoja"]):
                resume_urls.append(a)
                continue

            # portfolio style capture
            if any(k in al for k in ["portfolio", "projects", "publications", "papers", "research", "talks", "slides"]):
                portfolio_urls.append(a)

            # same-domain internal links
            if _same_domain(start_url, a):
                personal_urls.append(a)

        # Deep crawl coupling:
        # If resume terms appear or any resume URL found, prioritize high value pages.
        should_deepen = resume_trigger or bool(resume_urls) or contact_trigger
        if should_deepen:
            for a in personal_urls:
                al = a.lower()
                if any(h in al for h in HIGH_VALUE_PATH_HINTS):
                    if a not in visited and a not in queue:
                        queue.append(a)

        # Otherwise, queue a small number of internal pages
        for a in personal_urls[:40]:
            if a not in visited and a not in queue and _same_domain(start_url, a):
                queue.append(a)

        # Bound queue
        queue = queue[:MAX_VISIT_QUEUE]

    return {
        "emails": sorted(set(emails))[:MAX_EMAILS],
        "phones": sorted(set(phones))[:MAX_PHONES],
        "resume_urls": sorted(set(resume_urls))[:MAX_RESUME_URLS],
        "portfolio_urls": sorted(set(portfolio_urls))[:MAX_PORTFOLIO_URLS],
        "personal_urls": sorted(set(personal_urls))[:MAX_PERSONAL_URLS],
        "triggers": sorted(set(triggers))[:10],
    }


# ----------------------------
# Public API: single entrypoint
# ----------------------------

def enrich_person_from_github_and_web(
    person_row: Dict,
    scenario: str,
    metrics: Dict,
    config: Optional[Dict] = None,
) -> Dict:
    """
    Canonical enrichment entry.

    Inputs:
      person_row: dict-like row from Phase 1 inventory
      scenario: scenario string used for logging context (no heavy logic here)
      metrics: dict of counters, mutated in place. Caller prints.
      config: optional config overrides (bounded crawl remains bounded)

    Returns:
      updates: dict of field updates (strings), plus optional provenance JSON fields if caller supports them.

    Metrics keys this function updates (all optional):
      github_ok, github_io, resume_cv_rows, email_rows, phone_rows, domains_crawled, repos_scanned
    """
    cfg = config or {}
    updates: Dict[str, str] = {}
    provenance: Dict[str, List[str]] = {}

    def bump(key: str, n: int = 1) -> None:
        try:
            metrics[key] = int(metrics.get(key, 0)) + int(n)
        except Exception:
            metrics[key] = metrics.get(key, 0) or 0

    # Resolve GitHub username and URL
    gh_user = (person_row.get("GitHub_Username") or "").strip()
    gh_url = (person_row.get("GitHub_URL") or "").strip()
    seed_handle = (person_row.get("Seed_Query_Or_Handle") or "").strip()

    if not gh_user and gh_url:
        m = GITHUB_PROFILE_RE.search(gh_url)
        if m:
            gh_user = m.group(1)

    if not gh_user and seed_handle and re.fullmatch(r"[A-Za-z0-9](?:-?[A-Za-z0-9]){0,38}", seed_handle):
        gh_user = seed_handle

    if gh_user:
        updates["GitHub_Username"] = gh_user
        if not gh_url:
            gh_url = f"https://github.com/{gh_user}"
            updates["GitHub_URL"] = gh_url

    # No GitHub identity, we cannot do GitHub or github.io enrichment
    if not gh_user:
        # still return safely, no claims, no guessing
        return updates

    # GitHub user profile
    github_ok, gh_profile = _github_user(gh_user)
    if github_ok:
        bump("github_ok", 1)
        provenance.setdefault("GitHub_URL", []).append(gh_url or f"https://github.com/{gh_user}")

    # github.io probe (mandatory per handle)
    ghio = _probe_github_io(gh_user)
    if ghio:
        bump("github_io", 1)
        updates["GitHub_IO_URL"] = ghio
        provenance.setdefault("GitHub_IO_URL", []).append(ghio)

    # Personal site from GitHub blog field (public, explicit)
    personal_site = ""
    if github_ok:
        personal_site = _norm_url(str(gh_profile.get("blog") or "").strip())
        if personal_site:
            provenance.setdefault("Personal_Website_URLs", []).append(gh_url or "")

    # Repo evidence (public metadata only)
    repo_urls: List[str] = []
    repo_whys: List[str] = []
    repos = _github_repos(gh_user)
    if repos:
        repo_urls, repo_whys = _pick_evidential_repos(repos)
        if repo_urls:
            updates["Key_GitHub_AI_Repos"] = _join_unique(repo_urls, limit=12)
            bump("repos_scanned", min(len(repo_urls), MAX_REPOS_TO_SCAN))
            provenance.setdefault("Key_GitHub_AI_Repos", []).append(gh_url or "")

        # Provide a concise "why" if caller supports it
        if repo_whys:
            updates["GitHub_Repo_Evidence_Why"] = _join_unique(repo_whys, limit=12)
            provenance.setdefault("GitHub_Repo_Evidence_Why", []).append(gh_url or "")

    # Crawl targets (bounded, deterministic)
    crawl_targets: List[Tuple[str, str]] = []
    if ghio:
        crawl_targets.append(("github_io", ghio))
    if personal_site:
        crawl_targets.append(("personal_site", personal_site))

    all_emails: List[str] = []
    all_phones: List[str] = []
    all_resume: List[str] = []
    all_portfolio: List[str] = []
    all_personal: List[str] = []
    all_triggers: List[str] = []

    for label, url in crawl_targets:
        bump("domains_crawled", 1)
        result = _crawl_domain_bounded(url)
        all_emails.extend(result.get("emails") or [])
        all_phones.extend(result.get("phones") or [])
        all_resume.extend(result.get("resume_urls") or [])
        all_portfolio.extend(result.get("portfolio_urls") or [])
        all_personal.extend(result.get("personal_urls") or [])
        all_triggers.extend(result.get("triggers") or [])
        if result.get("emails"):
            provenance.setdefault("Primary_Email", []).append(url)
        if result.get("phones"):
            provenance.setdefault("Primary_Phone", []).append(url)
        if result.get("resume_urls"):
            provenance.setdefault("Resume_URL", []).append(url)
            provenance.setdefault("CV_URL", []).append(url)

    all_emails = sorted(set(all_emails))[:MAX_EMAILS]
    all_phones = sorted(set(all_phones))[:MAX_PHONES]
    all_resume = sorted(set(all_resume))[:MAX_RESUME_URLS]
    all_portfolio = sorted(set(all_portfolio))[:MAX_PORTFOLIO_URLS]
    all_personal = sorted(set(all_personal))[:MAX_PERSONAL_URLS]
    all_triggers = sorted(set(all_triggers))[:10]

    # Universal coupling and application:
    # If any resume/cv trigger exists OR any resume URL exists, we must treat emails/phones extraction as mandatory.
    # We already extracted universally. Here we ensure updates are applied consistently and counters are incremented correctly.

    # Apply email
    if all_emails:
        # Only set Primary_Email if empty at caller level. We cannot see caller's final decision, so we supply best candidate.
        updates.setdefault("Primary_Email", all_emails[0])
        bump("email_rows", 1)

    # Apply phone
    if all_phones:
        updates.setdefault("Primary_Phone", all_phones[0])
        bump("phone_rows", 1)

    # Apply resume/cv
    if all_resume or ("resume_terms_present" in all_triggers):
        if all_resume:
            # Prefer a URL that looks most like CV/resume, otherwise shortest.
            ranked = sorted(all_resume, key=lambda u: (0 if _is_probably_resume_url(u) else 1, len(u)))
            updates.setdefault("Resume_URL", ranked[0])
            updates.setdefault("CV_URL", ranked[0])
        bump("resume_cv_rows", 1)

    # Apply personal/portfolio URLs (safe, explicit)
    if personal_site:
        updates.setdefault("Personal_Website_URLs", personal_site)
    if all_portfolio:
        updates.setdefault("Portfolio_URLs", _join_unique(all_portfolio, limit=12))
    if all_personal and not updates.get("Personal_Website_URLs"):
        # As a last resort, store a small set of internal URLs as personal URLs if caller has that column.
        updates.setdefault("Personal_Website_URLs", _join_unique(all_personal, limit=6))

    # Attach provenance if caller supports it
    # 🔒 Schema immutability enforcement:
    # Only attach provenance if the canonical column already exists.
    if provenance and "Field_Level_Provenance_JSON" in person_row:
        prov_json = json.dumps(
            {k: v[:5] for k, v in provenance.items()},
            ensure_ascii=False,
            separators=(",", ":"),
        )
        updates["Field_Level_Provenance_JSON"] = prov_json

    return updates
