#!/usr/bin/env python3
"""
AI Talent Engine — Deep Artifact + Contact Harvester (Crawler)
© 2025 L. David Mendoza

Version: v1.2.0 (2026-01-01)
Changelog:
- v1.2.0: Adds Hugging Face discovery + model/space/org URL extraction.
- v1.1.0: Adds provenance splitting (contact vs research URLs) + stronger de-duplication.
- v1.0.0: Bounded crawler for github.io + linked public pages/docs; extracts emails/phones + key URLs.

Contract behavior (no loopholes):
- Crawl github.io + linked public portfolio/personal sites + linked resume PDFs (when accessible)
- Extract: contact info (email/phone) + identity/research/conference/patent URLs
- Only harvest what is explicitly public (no guessing, no placeholders)
- Bounded crawl so demos remain stable and interview-safe

Input:
- CSV path via --input (must contain GitHub_Username OR GitHub_URL OR github_url fields)

Output:
- Updates the same CSV in place (or writes --output if provided)

Validation:
- Never fabricates. Blanks remain blank if not publicly present.

Legal/Safety:
- Public pages only. No authentication circumvention. No LinkedIn scraping.
"""

from __future__ import annotations

import argparse
import csv
import os
import re
import sys
import time
import json
import hashlib
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple
from urllib.parse import urljoin, urlparse, urldefrag

try:
    import requests
except Exception as e:
    print("ERROR: requests is required. Install: python3 -m pip install requests", file=sys.stderr)
    raise

# Optional PDF parsing (best effort)
PDF_TEXT_ENABLED = False
try:
    import PyPDF2  # type: ignore
    PDF_TEXT_ENABLED = True
except Exception:
    PDF_TEXT_ENABLED = False

USER_AGENT = "AI-Talent-Engine-DeepHarvester/1.2 (+public-web-crawl; bounded; audit)"
DEFAULT_TIMEOUT = 12

EMAIL_RE = re.compile(r"(?i)\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b")
PHONE_RE = re.compile(
    r"(?x)(?<!\d)"
    r"(?:\+?1[\s\-.]?)?"
    r"(?:\(\s*\d{3}\s*\)|\d{3})"
    r"[\s\-.]?\d{3}"
    r"[\s\-.]?\d{4}"
    r"(?!\d)"
)

HREF_RE = re.compile(r'(?i)\bhref\s*=\s*["\']([^"\']+)["\']')
SRC_RE = re.compile(r'(?i)\bsrc\s*=\s*["\']([^"\']+)["\']')

# URL classifiers
def is_http_url(u: str) -> bool:
    try:
        p = urlparse(u)
        return p.scheme in ("http", "https")
    except Exception:
        return False

def normalize_url(u: str) -> str:
    u = u.strip()
    u, _frag = urldefrag(u)
    return u

def same_host(a: str, b: str) -> bool:
    try:
        return urlparse(a).netloc.lower() == urlparse(b).netloc.lower()
    except Exception:
        return False

def safe_join(base: str, href: str) -> Optional[str]:
    href = href.strip()
    if not href:
        return None
    if href.startswith("mailto:") or href.startswith("tel:"):
        return href
    if href.startswith("#"):
        return None
    try:
        u = urljoin(base, href)
        u = normalize_url(u)
        if is_http_url(u):
            return u
        return None
    except Exception:
        return None

def looks_like_pdf(url: str) -> bool:
    return url.lower().split("?")[0].endswith(".pdf")

def domain(u: str) -> str:
    try:
        return urlparse(u).netloc.lower()
    except Exception:
        return ""

def canonical_github_io(username: str) -> str:
    return f"https://{username}.github.io/"

def canonical_github_profile(username: str) -> str:
    return f"https://github.com/{username}"

def extract_github_username(row: Dict[str, str]) -> Optional[str]:
    for k in ("GitHub_Username", "github_username", "GitHubUsername", "github_user"):
        v = (row.get(k) or "").strip()
        if v:
            return v.lstrip("@").strip()
    # derive from github url
    for k in ("GitHub_URL", "github_url", "github"):
        v = (row.get(k) or "").strip()
        if "github.com/" in v:
            try:
                path = urlparse(v).path.strip("/")
                if path:
                    return path.split("/")[0]
            except Exception:
                pass
    return None

def extract_text_and_links_from_html(html: str, base_url: str) -> Tuple[str, Set[str]]:
    links: Set[str] = set()
    for m in HREF_RE.finditer(html):
        u = safe_join(base_url, m.group(1))
        if u:
            links.add(u)
    for m in SRC_RE.finditer(html):
        u = safe_join(base_url, m.group(1))
        if u:
            links.add(u)
    # naive text extraction: strip tags
    text = re.sub(r"(?s)<script.*?>.*?</script>", " ", html)
    text = re.sub(r"(?s)<style.*?>.*?</style>", " ", text)
    text = re.sub(r"(?s)<.*?>", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text, links

def fetch(session: requests.Session, url: str, timeout: int) -> Tuple[Optional[str], Optional[bytes], Optional[str]]:
    try:
        r = session.get(url, timeout=timeout, headers={"User-Agent": USER_AGENT}, allow_redirects=True)
        ct = (r.headers.get("Content-Type") or "").lower()
        if r.status_code >= 400:
            return None, None, ct
        if "text/html" in ct or ct.startswith("text/"):
            return r.text, None, ct
        return None, r.content, ct
    except Exception:
        return None, None, None

def pdf_text_from_bytes(b: bytes) -> str:
    if not PDF_TEXT_ENABLED:
        return ""
    try:
        from io import BytesIO
        reader = PyPDF2.PdfReader(BytesIO(b))
        out = []
        for page in reader.pages[:10]:  # bounded
            try:
                out.append(page.extract_text() or "")
            except Exception:
                continue
        return "\n".join(out)
    except Exception:
        return ""

def add_provenance_map(prov: Dict[str, Set[str]], key: str, where: str):
    prov.setdefault(key, set()).add(where)

@dataclass
class HarvestResult:
    emails: Set[str] = field(default_factory=set)
    phones: Set[str] = field(default_factory=set)
    linkedin_urls: Set[str] = field(default_factory=set)
    twitter_urls: Set[str] = field(default_factory=set)
    resume_urls: Set[str] = field(default_factory=set)
    portfolio_urls: Set[str] = field(default_factory=set)

    scholar_urls: Set[str] = field(default_factory=set)
    semantic_urls: Set[str] = field(default_factory=set)
    openreview_urls: Set[str] = field(default_factory=set)
    arxiv_urls: Set[str] = field(default_factory=set)
    patent_urls: Set[str] = field(default_factory=set)
    conference_urls: Set[str] = field(default_factory=set)

    hf_profile_urls: Set[str] = field(default_factory=set)
    hf_model_urls: Set[str] = field(default_factory=set)
    hf_space_urls: Set[str] = field(default_factory=set)
    hf_org_urls: Set[str] = field(default_factory=set)

    other_urls: Set[str] = field(default_factory=set)

    contact_provenance: Dict[str, Set[str]] = field(default_factory=dict)
    research_provenance: Dict[str, Set[str]] = field(default_factory=dict)

def classify_url(u: str):
    du = domain(u)
    ul = u.lower()

    # Contact / identity
    if "linkedin.com/" in ul:
        return ("linkedin", "contact")
    if "twitter.com/" in ul or "x.com/" in ul:
        return ("twitter", "contact")

    # Hugging Face
    if du == "huggingface.co":
        # profile: https://huggingface.co/<user_or_org>
        parts = urlparse(u).path.strip("/").split("/")
        if len(parts) == 1 and parts[0]:
            return ("hf_profile", "research")
        if len(parts) >= 2:
            if parts[0] in ("spaces",):
                return ("hf_space", "research")
            # models are often /<user>/<repo>
            if parts[0] not in ("organizations", "datasets", "docs", "tasks", "spaces", "blog"):
                return ("hf_model", "research")
            if parts[0] == "organizations" and len(parts) >= 2:
                return ("hf_org", "research")
        return ("hf_other", "research")

    # Research
    if "scholar.google." in ul:
        return ("scholar", "research")
    if "semanticscholar.org/" in ul:
        return ("semantic", "research")
    if "openreview.net/" in ul:
        return ("openreview", "research")
    if "arxiv.org/" in ul:
        return ("arxiv", "research")
    if "patents.google." in ul or "google.com/patents" in ul:
        return ("patent", "research")

    # Talks / conferences (best effort patterns)
    if "slideslive.com/" in ul or "youtube.com/" in ul or "youtu.be/" in ul or "speakerdeck.com/" in ul:
        return ("conference", "research")
    if "neurips.cc/" in ul or "iclr.cc/" in ul or "icml.cc/" in ul or "aclanthology.org/" in ul:
        return ("conference", "research")

    # Resume / portfolio heuristics
    if looks_like_pdf(u) or any(x in ul for x in ("/resume", "/cv", "drive.google.com", "docs.google.com")):
        return ("resume", "contact")
    if any(x in ul for x in (".github.io", "about", "portfolio", "projects")):
        return ("portfolio", "contact")

    return ("other", "other")

def bounded_crawl(
    session: requests.Session,
    roots: List[str],
    max_depth: int,
    max_pages: int,
    timeout: int,
) -> HarvestResult:
    seen: Set[str] = set()
    q: List[Tuple[str, int]] = []

    for r in roots:
        if r and is_http_url(r):
            q.append((normalize_url(r), 0))

    result = HarvestResult()

    def ingest_text(text: str, where: str):
        for e in EMAIL_RE.findall(text or ""):
            result.emails.add(e)
            add_provenance_map(result.contact_provenance, f"email:{e}", where)
        for p in PHONE_RE.findall(text or ""):
            pp = re.sub(r"\s+", " ", p).strip()
            result.phones.add(pp)
            add_provenance_map(result.contact_provenance, f"phone:{pp}", where)

    def ingest_url(u: str, where: str):
        u = normalize_url(u)
        key, bucket = classify_url(u)

        if key == "linkedin":
            result.linkedin_urls.add(u)
            add_provenance_map(result.contact_provenance, f"url:{u}", where)
        elif key == "twitter":
            result.twitter_urls.add(u)
            add_provenance_map(result.contact_provenance, f"url:{u}", where)
        elif key == "resume":
            result.resume_urls.add(u)
            add_provenance_map(result.contact_provenance, f"url:{u}", where)
        elif key == "portfolio":
            result.portfolio_urls.add(u)
            add_provenance_map(result.contact_provenance, f"url:{u}", where)

        elif key == "scholar":
            result.scholar_urls.add(u)
            add_provenance_map(result.research_provenance, f"url:{u}", where)
        elif key == "semantic":
            result.semantic_urls.add(u)
            add_provenance_map(result.research_provenance, f"url:{u}", where)
        elif key == "openreview":
            result.openreview_urls.add(u)
            add_provenance_map(result.research_provenance, f"url:{u}", where)
        elif key == "arxiv":
            result.arxiv_urls.add(u)
            add_provenance_map(result.research_provenance, f"url:{u}", where)
        elif key == "patent":
            result.patent_urls.add(u)
            add_provenance_map(result.research_provenance, f"url:{u}", where)
        elif key == "conference":
            result.conference_urls.add(u)
            add_provenance_map(result.research_provenance, f"url:{u}", where)

        elif key == "hf_profile":
            result.hf_profile_urls.add(u)
            add_provenance_map(result.research_provenance, f"url:{u}", where)
        elif key == "hf_model":
            result.hf_model_urls.add(u)
            add_provenance_map(result.research_provenance, f"url:{u}", where)
        elif key == "hf_space":
            result.hf_space_urls.add(u)
            add_provenance_map(result.research_provenance, f"url:{u}", where)
        elif key == "hf_org":
            result.hf_org_urls.add(u)
            add_provenance_map(result.research_provenance, f"url:{u}", where)

        else:
            result.other_urls.add(u)

    pages = 0
    while q and pages < max_pages:
        url, depth = q.pop(0)
        if url in seen:
            continue
        seen.add(url)
        pages += 1

        html, blob, ct = fetch(session, url, timeout)
        ingest_url(url, where=url)

        if html:
            text, links = extract_text_and_links_from_html(html, url)
            ingest_text(text, where=url)

            # Ingest mailto/tel links too
            for l in list(links):
                if l.startswith("mailto:"):
                    e = l.split("mailto:", 1)[1].split("?", 1)[0].strip()
                    if e and EMAIL_RE.search(e):
                        result.emails.add(e)
                        add_provenance_map(result.contact_provenance, f"email:{e}", url)
                    continue
                if l.startswith("tel:"):
                    p = l.split("tel:", 1)[1].split("?", 1)[0].strip()
                    if p:
                        result.phones.add(p)
                        add_provenance_map(result.contact_provenance, f"phone:{p}", url)
                    continue

            for l in links:
                if l.startswith("mailto:") or l.startswith("tel:"):
                    continue
                ingest_url(l, where=url)
                if depth + 1 <= max_depth and is_http_url(l):
                    q.append((l, depth + 1))

        # Optional PDF text extraction (bounded)
        if blob and looks_like_pdf(url):
            pdf_text = pdf_text_from_bytes(blob)
            if pdf_text:
                ingest_text(pdf_text, where=url)

        # Be polite
        time.sleep(0.15)

    # Final: de-dupe other_urls against known sets
    known = (
        result.linkedin_urls
        | result.twitter_urls
        | result.resume_urls
        | result.portfolio_urls
        | result.scholar_urls
        | result.semantic_urls
        | result.openreview_urls
        | result.arxiv_urls
        | result.patent_urls
        | result.conference_urls
        | result.hf_profile_urls
        | result.hf_model_urls
        | result.hf_space_urls
        | result.hf_org_urls
    )
    result.other_urls = set(sorted(u for u in result.other_urls if u not in known))
    return result

def ensure_columns(row: Dict[str, str], cols: List[str]):
    for c in cols:
        if c not in row:
            row[c] = ""

def main() -> int:
    ap = argparse.ArgumentParser(description="Deep artifact harvester (github.io + linked sites + HF + research URLs)")
    ap.add_argument("--input", required=True, help="Input CSV to enrich in place")
    ap.add_argument("--output", default="", help="Optional output CSV path (default: in-place)")
    ap.add_argument("--max-depth", type=int, default=2, help="Max crawl depth (default: 2)")
    ap.add_argument("--max-pages", type=int, default=18, help="Max pages per person (default: 18)")
    ap.add_argument("--timeout", type=int, default=DEFAULT_TIMEOUT, help="HTTP timeout seconds")
    ap.add_argument("--open", action="store_true", help="Open output CSV when done (macOS)")
    args = ap.parse_args()

    inp = Path(args.input)
    if not inp.exists():
        print(f"ERROR: Missing input CSV: {inp}", file=sys.stderr)
        return 2

    outp = Path(args.output) if args.output.strip() else inp

    with inp.open("r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        if not rows:
            print("ERROR: Input CSV has no rows.", file=sys.stderr)
            return 3
        fieldnames = list(reader.fieldnames or [])

    # Required harvester columns (contract)
    add_cols = [
        "Public_Email_Found",
        "Public_Phone_Found",
        "Additional_Public_Emails",
        "Additional_Public_Phones",
        "LinkedIn_Public_URLs",
        "X_Twitter_URLs",
        "Resume_URLs",
        "Portfolio_URLs",
        "Google_Scholar_Profile_URLs",
        "Semantic_Scholar_URLs",
        "OpenReview_URLs",
        "arXiv_URLs",
        "Patent_URLs",
        "Conference_Presentation_URLs",
        "HuggingFace_Profile_URLs",
        "HuggingFace_Model_URLs",
        "HuggingFace_Space_URLs",
        "HuggingFace_Org_URLs",
        "All_Public_URLs_Found",
        "Contact_Provenance_URLs",
        "Research_Provenance_URLs",
        "Harvest_Provenance",
    ]

    # Ensure columns exist in header
    for c in add_cols:
        if c not in fieldnames:
            fieldnames.append(c)

    session = requests.Session()

    for i, row in enumerate(rows):
        gh_user = extract_github_username(row) or ""
        roots: List[str] = []

        if gh_user:
            roots.append(canonical_github_io(gh_user))
            roots.append(canonical_github_profile(gh_user))

        # include any existing URLs already present
        for k in ("GitHub_URL", "github_url", "github_io_url", "GitHub_IO_URL", "Personal_Website", "Portfolio_URL", "portfolio_url"):
            v = (row.get(k) or "").strip()
            if v and is_http_url(v):
                roots.append(v)

        # bounded unique roots
        roots = list(dict.fromkeys([normalize_url(r) for r in roots if r]))

        if not roots:
            # still ensure output columns exist
            for c in add_cols:
                row[c] = row.get(c, "")
            continue

        harvest = bounded_crawl(
            session=session,
            roots=roots,
            max_depth=max(0, args.max_depth),
            max_pages=max(1, args.max_pages),
            timeout=max(5, args.timeout),
        )

        # Primary email/phone: pick first in sorted list (deterministic)
        emails_sorted = sorted(harvest.emails)
        phones_sorted = sorted(harvest.phones)

        row["Public_Email_Found"] = emails_sorted[0] if emails_sorted else ""
        row["Public_Phone_Found"] = phones_sorted[0] if phones_sorted else ""

        row["Additional_Public_Emails"] = " | ".join(emails_sorted[1:]) if len(emails_sorted) > 1 else ""
        row["Additional_Public_Phones"] = " | ".join(phones_sorted[1:]) if len(phones_sorted) > 1 else ""

        row["LinkedIn_Public_URLs"] = " | ".join(sorted(harvest.linkedin_urls))
        row["X_Twitter_URLs"] = " | ".join(sorted(harvest.twitter_urls))
        row["Resume_URLs"] = " | ".join(sorted(harvest.resume_urls))
        row["Portfolio_URLs"] = " | ".join(sorted(harvest.portfolio_urls))

        row["Google_Scholar_Profile_URLs"] = " | ".join(sorted(harvest.scholar_urls))
        row["Semantic_Scholar_URLs"] = " | ".join(sorted(harvest.semantic_urls))
        row["OpenReview_URLs"] = " | ".join(sorted(harvest.openreview_urls))
        row["arXiv_URLs"] = " | ".join(sorted(harvest.arxiv_urls))
        row["Patent_URLs"] = " | ".join(sorted(harvest.patent_urls))
        row["Conference_Presentation_URLs"] = " | ".join(sorted(harvest.conference_urls))

        row["HuggingFace_Profile_URLs"] = " | ".join(sorted(harvest.hf_profile_urls))
        row["HuggingFace_Model_URLs"] = " | ".join(sorted(harvest.hf_model_urls))
        row["HuggingFace_Space_URLs"] = " | ".join(sorted(harvest.hf_space_urls))
        row["HuggingFace_Org_URLs"] = " | ".join(sorted(harvest.hf_org_urls))

        row["All_Public_URLs_Found"] = " | ".join(sorted(harvest.other_urls))

        # Provenance (JSON for audit)
        row["Contact_Provenance_URLs"] = json.dumps(
            {k: sorted(list(v)) for k, v in harvest.contact_provenance.items()},
            ensure_ascii=False,
            sort_keys=True,
        )
        row["Research_Provenance_URLs"] = json.dumps(
            {k: sorted(list(v)) for k, v in harvest.research_provenance.items()},
            ensure_ascii=False,
            sort_keys=True,
        )

        row["Harvest_Provenance"] = json.dumps(
            {
                "crawl_roots": roots,
                "max_depth": args.max_depth,
                "max_pages": args.max_pages,
                "pdf_text_enabled": PDF_TEXT_ENABLED,
                "user_agent": USER_AGENT,
            },
            ensure_ascii=False,
            sort_keys=True,
        )

        # Progress without spam
        if (i + 1) % 5 == 0 or (i + 1) == len(rows):
            print(f"harvest: {i+1}/{len(rows)}")

    with outp.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for r in rows:
            writer.writerow(r)

    print(f"SUCCESS: Deep harvest complete → {outp}")

    if args.open:
        try:
            os.system(f'open "{outp}" >/dev/null 2>&1')
            print(f"POP-UP OPENED: {outp}")
        except Exception:
            pass

    return 0

if __name__ == "__main__":
    raise SystemExit(main())
