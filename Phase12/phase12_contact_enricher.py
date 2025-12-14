#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
import os
import re
import time
import hashlib
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Set, Tuple

import requests

try:
    from bs4 import BeautifulSoup  # type: ignore
except Exception:
    BeautifulSoup = None

USER_AGENT = "Research_First_Sourcer_Automation/Phase12 (contact enrichment; respectful; no LinkedIn scraping)"

EMAIL_RE = re.compile(r"([a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,})")
MAILTO_RE = re.compile(r"mailto:([^\"'>\s]+)", re.IGNORECASE)

# Conservative phone matcher (US leaning). Best-effort only.
PHONE_RE = re.compile(r"(\+?1[\s\-\.]?)?(\(?\d{3}\)?[\s\-\.]?)\d{3}[\s\-\.]?\d{4}")

GITHUB_PROFILE_RE = re.compile(r"^https?://(www\.)?github\.com/([^/\s]+)/?$", re.IGNORECASE)
GITHUB_REPO_RE = re.compile(r"^https?://(www\.)?github\.com/([^/\s]+)/([^/\s]+)(/.*)?$", re.IGNORECASE)

@dataclass
class FetchResult:
    url: str
    status: int
    text: str

def sha1(s: str) -> str:
    return hashlib.sha1(s.encode("utf-8", errors="ignore")).hexdigest()

def load_json_or_csv(path: Path) -> List[Dict[str, Any]]:
    if path.suffix.lower() == ".json":
        data = json.loads(path.read_text(errors="replace"))
        if isinstance(data, list):
            return data
        if isinstance(data, dict):
            return [data]
        return []
    if path.suffix.lower() == ".csv":
        with path.open(newline="") as f:
            return list(csv.DictReader(f))
    raise ValueError(f"Unsupported input type: {path}")

def write_csv(path: Path, rows: List[Dict[str, Any]]) -> None:
    if not rows:
        # still write headers for predictability
        headers = [
            "Name","Organization","Github","Github.io","Website","Resume Link",
            "Home Email","Work Email","Mobile Phone",
            "Contact_Emails_All","Contact_Phones_All","Contact_Sources"
        ]
        with path.open("w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=headers)
            w.writeheader()
        return

    # stable header order: existing keys first, then new ones
    keys: List[str] = []
    seen: Set[str] = set()
    for r in rows:
        for k in r.keys():
            if k not in seen:
                seen.add(k)
                keys.append(k)
    with path.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=keys)
        w.writeheader()
        for r in rows:
            w.writerow(r)

def norm_url(u: str) -> str:
    u = (u or "").strip()
    if not u:
        return ""
    if u.startswith("http://") or u.startswith("https://"):
        return u
    # allow bare github.com/user
    if u.startswith("github.com/") or u.startswith("www.github.com/"):
        return "https://" + u
    return u

def safe_get(session: requests.Session, url: str, cache_dir: Path, timeout: int, sleep_s: float) -> FetchResult:
    url = norm_url(url)
    if not url:
        return FetchResult(url=url, status=0, text="")

    cache_dir.mkdir(parents=True, exist_ok=True)
    cache_path = cache_dir / f"{sha1(url)}.txt"

    if cache_path.exists():
        return FetchResult(url=url, status=200, text=cache_path.read_text(errors="replace"))

    headers = {"User-Agent": USER_AGENT, "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"}

    # small pacing between requests
    if sleep_s > 0:
        time.sleep(sleep_s)

    try:
        resp = session.get(url, headers=headers, timeout=timeout, allow_redirects=True)
        status = int(resp.status_code)
        text = resp.text or ""
    except Exception:
        return FetchResult(url=url, status=0, text="")

    # cache only successful-ish HTML/text responses
    if status and text:
        cache_path.write_text(text, errors="ignore")

    return FetchResult(url=url, status=status, text=text)

def extract_emails_and_phones(text: str) -> Tuple[Set[str], Set[str]]:
    emails = set(m.group(1).strip() for m in EMAIL_RE.finditer(text or ""))
    # mailto: may contain query params
    for m in MAILTO_RE.finditer(text or ""):
        e = m.group(1).split("?")[0].strip()
        if e:
            emails.add(e)

    phones = set()
    for m in PHONE_RE.finditer(text or ""):
        phones.add(m.group(0).strip())

    # basic cleanup
    emails = set(e.strip(".,;:()[]{}<>\"'").lower() for e in emails if "@" in e and "." in e)
    phones = set(p.strip(".,;:()[]{}<>\"'") for p in phones if len(re.sub(r"\D", "", p)) >= 10)

    return emails, phones

def soup_links(html: str) -> List[str]:
    if not html or BeautifulSoup is None:
        return []
    try:
        soup = BeautifulSoup(html, "html.parser")
    except Exception:
        return []
    out = []
    for a in soup.find_all("a"):
        href = a.get("href")
        if href and isinstance(href, str):
            out.append(href.strip())
    return out

def github_api_headers() -> Dict[str, str]:
    h = {"User-Agent": USER_AGENT, "Accept": "application/vnd.github+json"}
    tok = os.environ.get("GITHUB_TOKEN", "").strip()
    if tok:
        h["Authorization"] = f"Bearer {tok}"
    return h

def github_user_from_url(url: str) -> Optional[str]:
    m = GITHUB_PROFILE_RE.match(url.strip())
    if not m:
        return None
    return m.group(2)

def github_repo_from_url(url: str) -> Optional[Tuple[str, str]]:
    m = GITHUB_REPO_RE.match(url.strip())
    if not m:
        return None
    owner = m.group(2)
    repo = m.group(3)
    return owner, repo

def fetch_github_profile_api(session: requests.Session, user: str, timeout: int) -> Dict[str, Any]:
    api = f"https://api.github.com/users/{user}"
    try:
        r = session.get(api, headers=github_api_headers(), timeout=timeout)
        if r.status_code != 200:
            return {}
        return r.json()
    except Exception:
        return {}

def fetch_github_repos_api(session: requests.Session, user: str, timeout: int, max_repos: int = 12) -> List[Dict[str, Any]]:
    api = f"https://api.github.com/users/{user}/repos?per_page=100&sort=updated"
    try:
        r = session.get(api, headers=github_api_headers(), timeout=timeout)
        if r.status_code != 200:
            return []
        data = r.json()
        if isinstance(data, list):
            return data[:max_repos]
        return []
    except Exception:
        return []

def candidate_urls(row: Dict[str, Any]) -> Dict[str, str]:
    # Respect your existing schema conventions and likely columns
    github = norm_url(str(row.get("Github") or row.get("GitHub") or row.get("github") or ""))
    ghio = norm_url(str(row.get("Github.io") or row.get("GitHub.io") or row.get("github.io") or ""))
    web = norm_url(str(row.get("Blog/Website") or row.get("Website") or row.get("Personal Website") or ""))
    resume = norm_url(str(row.get("Resume Link") or row.get("Resume") or row.get("CV") or ""))
    linkedin = norm_url(str(row.get("LinkedIn") or row.get("LinkedIn URL") or row.get("LinkedIn Vanity") or ""))

    # We do not scrape LinkedIn. We only pass it through unchanged.
    return {
        "Github": github,
        "Github.io": ghio,
        "Website": web,
        "Resume Link": resume,
        "LinkedIn": linkedin,
    }

def enrich_row(
    session: requests.Session,
    row: Dict[str, Any],
    cache_dir: Path,
    timeout: int,
    sleep_s: float,
    max_link_hops: int,
    max_repo_scan: int
) -> Dict[str, Any]:

    urls = candidate_urls(row)

    # Never overwrite existing contact fields if present
    existing_emails = set()
    for k in ["Home Email", "Work Email"]:
        v = str(row.get(k) or "").strip()
        if v and "@" in v:
            existing_emails.add(v.lower())

    existing_phone = str(row.get("Mobile Phone") or "").strip()

    found_emails: Set[str] = set(existing_emails)
    found_phones: Set[str] = set([existing_phone]) if existing_phone else set()
    sources: List[str] = []

    def scan_url(label: str, url: str) -> None:
        nonlocal found_emails, found_phones, sources
        if not url:
            return
        # LinkedIn explicitly excluded
        if "linkedin.com" in url.lower():
            return
        fr = safe_get(session, url, cache_dir, timeout=timeout, sleep_s=sleep_s)
        if fr.status == 0 or not fr.text:
            return
        e, p = extract_emails_and_phones(fr.text)
        if e or p:
            sources.append(f"{label}:{url}")
            found_emails |= e
            found_phones |= p

        # Follow a small number of hops to obvious contact pages
        if max_link_hops <= 0:
            return
        links = soup_links(fr.text)
        interesting = []
        for href in links:
            href_l = href.lower()
            if href_l.startswith("mailto:"):
                continue
            if "contact" in href_l or "about" in href_l or "cv" in href_l or "resume" in href_l:
                # normalize relative paths
                if href_l.startswith("http://") or href_l.startswith("https://"):
                    interesting.append(href)
                elif href.startswith("/"):
                    # build from origin
                    try:
                        origin = url.split("/", 3)[:3]
                        interesting.append("/".join(origin) + href)
                    except Exception:
                        pass
        for hop_url in interesting[:max_link_hops]:
            fr2 = safe_get(session, hop_url, cache_dir, timeout=timeout, sleep_s=sleep_s)
            if fr2.status == 0 or not fr2.text:
                continue
            e2, p2 = extract_emails_and_phones(fr2.text)
            if e2 or p2:
                sources.append(f"hop:{hop_url}")
                found_emails |= e2
                found_phones |= p2

    # Scan primary URLs
    scan_url("github", urls["Github"])
    scan_url("githubio", urls["Github.io"])
    scan_url("website", urls["Website"])
    scan_url("resume", urls["Resume Link"])

    # GitHub API enrichment (best practice). Pull email and blog if present.
    gh_user = github_user_from_url(urls["Github"]) if urls["Github"] else None
    if gh_user:
        prof = fetch_github_profile_api(session, gh_user, timeout=timeout)
        api_email = (prof.get("email") or "").strip()
        api_blog = (prof.get("blog") or "").strip()
        if api_email and "@" in api_email:
            found_emails.add(api_email.lower())
            sources.append(f"github_api_email:{gh_user}")
        if api_blog:
            scan_url("github_api_blog", api_blog)

        # Scan a few repos for obvious contact signals in README or docs pages
        repos = fetch_github_repos_api(session, gh_user, timeout=timeout, max_repos=max_repo_scan)
        for repo in repos:
            html_url = (repo.get("html_url") or "").strip()
            if html_url:
                scan_url("repo", html_url)

    # Final assignment. Do not overwrite existing fields unless blank.
    emails_sorted = sorted(found_emails)
    phones_sorted = sorted(found_phones)

    row["Contact_Emails_All"] = "; ".join(emails_sorted)
    row["Contact_Phones_All"] = "; ".join(phones_sorted)
    row["Contact_Sources"] = " | ".join(sources[:50])  # prevent massive cells

    # Fill only blank canonical fields
    if not str(row.get("Home Email") or "").strip() and emails_sorted:
        row["Home Email"] = emails_sorted[0]
    if not str(row.get("Work Email") or "").strip() and len(emails_sorted) >= 2:
        row["Work Email"] = emails_sorted[1]
    if not str(row.get("Mobile Phone") or "").strip() and phones_sorted:
        row["Mobile Phone"] = phones_sorted[0]

    # Preserve LinkedIn fields untouched
    if "LinkedIn" in row and urls["LinkedIn"]:
        row["LinkedIn"] = urls["LinkedIn"]

    # Preserve url fields if present
    for k in ["Github", "Github.io", "Website", "Resume Link"]:
        if urls.get(k) and not str(row.get(k) or "").strip():
            row[k] = urls[k]

    return row

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--in", dest="inp", required=True, help="Input JSON or CSV of candidates")
    ap.add_argument("--out", dest="out", required=True, help="Output CSV path")
    ap.add_argument("--cache", default="./cache/http", help="Cache folder")
    ap.add_argument("--timeout", type=int, default=20)
    ap.add_argument("--sleep", type=float, default=0.25, help="Seconds between requests")
    ap.add_argument("--max-link-hops", type=int, default=2, help="Follow up to N contact/about links per page")
    ap.add_argument("--max-repo-scan", type=int, default=6, help="Scan up to N recent repos per GitHub user")
    args = ap.parse_args()

    inp = Path(args.inp)
    out = Path(args.out)
    cache_dir = Path(args.cache)

    if not inp.exists():
        raise SystemExit(f"Input not found: {inp}")

    rows = load_json_or_csv(inp)

    session = requests.Session()

    enriched = []
    for i, r in enumerate(rows, 1):
        enriched.append(
            enrich_row(
                session=session,
                row=dict(r),
                cache_dir=cache_dir,
                timeout=args.timeout,
                sleep_s=args.sleep,
                max_link_hops=args.max_link_hops,
                max_repo_scan=args.max_repo_scan
            )
        )
        if i % 25 == 0:
            print(f"[progress] {i}/{len(rows)}")

    out.parent.mkdir(parents=True, exist_ok=True)
    write_csv(out, enriched)
    print(f"[ok] wrote {out} rows={len(enriched)}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
