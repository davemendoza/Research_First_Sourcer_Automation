#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
universal_enrichment_pipeline.py

AI Talent Engine — Universal Lead Enrichment Pipeline (Lead-Grade)
Version: v1.0.0
Author: L. David Mendoza
Date: 2026-01-02
© 2025 L. David Mendoza

Non-negotiable contract:
- GitHub.io is a REQUIRED first-class enrichment surface:
  - Every lead must be probed for https://<username>.github.io/
  - Results must be recorded in canonical columns
  - Pipeline FAILS if probe step cannot run or canonical GitHub.io columns are missing
  - Pipeline does NOT fail if a given user does not have Pages (404 is a valid outcome)

Outputs:
- outputs/leads/run_<run_id>/LEADS_MASTER_<scenario>_<run_id>.csv  (70+ columns)
- outputs/manifests/run_manifest_<scenario>_<run_id>.json

Input:
- A normalized people CSV with Person_ID and Role_Type as first columns.
  Produced by scripts/normalize_people_csv.py

Usage:
  python3 scripts/universal_enrichment_pipeline.py <scenario> <people_csv_normalized> <run_id>

Implementation notes:
- World-class determinism: fixed schema, provenance columns, bounded crawl
- Conservative scraping: only public pages; do not brute-force; rate-limit
"""

from __future__ import annotations

import csv
import json
import re
import sys
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from urllib.parse import urljoin, urlparse
from urllib.request import Request, urlopen


REPO_ROOT = Path(__file__).resolve().parents[1]
OUT_LEADS = REPO_ROOT / "outputs" / "leads"
OUT_MANIFESTS = REPO_ROOT / "outputs" / "manifests"


CANON_PREFIX = ["Person_ID", "Role_Type", "Email", "Phone", "LinkedIn_URL", "GitHub_URL", "GitHub_Username"]

# Lead-grade schema (70+ columns). Keep stable ordering.
LEAD_SCHEMA: List[str] = CANON_PREFIX + [
    # Identity / source passthrough
    "Full_Name",
    "Name_Raw",
    "Company",
    "Location",
    "Bio",
    "Followers",
    "Following",
    "Public_Repos",
    "Created_At",
    "Updated_At",
    "Source_Scenario",
    "Source_Query",
    "Source_Page",
    "Source_Rank",
    "Retrieved_At_UTC",
    "Scenario",
    "Scenario_Score",
    "Scenario_Buckets",
    "Scenario_Keywords",
    "GitHub_Blog_Raw",

    # GitHub.io first-class surface (required)
    "GitHub_IO_URL",
    "GitHub_IO_HTTP_Status",
    "GitHub_IO_Final_URL",
    "GitHub_IO_Checked_UTC",
    "GitHub_IO_Probe_Method",  # HEAD|GET
    "GitHub_IO_Present",       # yes|no
    "GitHub_IO_Error",

    # Enrichment crawl (bounded)
    "Crawl_Root_URL",
    "Crawl_Pages_Fetched",
    "Crawl_Max_Pages",
    "Crawl_Seconds",
    "Crawl_Error",

    # Contact extraction
    "Email_Found",
    "Email_Source",
    "Email_Confidence",         # high|medium|low
    "Email_Evidence_Snippet",
    "Phone_Found",
    "Phone_Source",
    "Phone_Confidence",
    "Phone_Evidence_Snippet",
    "LinkedIn_Found",
    "LinkedIn_Source",
    "LinkedIn_Confidence",
    "LinkedIn_Evidence_URL",

    # Other signals from pages
    "Resume_URL",
    "Resume_Source",
    "CV_URL",
    "Portfolio_URL",
    "Portfolio_Source",
    "Google_Scholar_URL",
    "Semantic_Scholar_URL",
    "OpenAlex_URL",
    "ORCID_URL",
    "Twitter_X_URL",
    "YouTube_URL",
    "Medium_URL",
    "Substack_URL",
    "Blog_URL",
    "Blog_Source",

    # Quality / provenance
    "Enrichment_Attempts",
    "Enrichment_Status",         # ok|partial|fail
    "Escalation_Level",          # 0..3
    "Notes",
    "Provenance_JSON",           # compact json string
]


EMAIL_RE = re.compile(r"(?i)(?<![\w.\-])([a-z0-9._%+\-]+@[a-z0-9.\-]+\.[a-z]{2,})(?![\w.\-])")
# US-ish phone patterns, conservative
PHONE_RE = re.compile(r"(?:(?:\+?1[\s\-\.])?\(?\d{3}\)?[\s\-\.]?\d{3}[\s\-\.]?\d{4})")
LINKEDIN_RE = re.compile(r"https?://(?:www\.)?linkedin\.com/[A-Za-z0-9_\-/%?=.&]+", re.I)

URL_HINTS = {
    "resume": re.compile(r"(?i)\b(resume|résumé|cv)\b"),
    "scholar": re.compile(r"(?i)scholar\.google\.com"),
    "semanticscholar": re.compile(r"(?i)semanticscholar\.org"),
    "openalex": re.compile(r"(?i)openalex\.org"),
    "orcid": re.compile(r"(?i)orcid\.org"),
    "twitter": re.compile(r"(?i)(twitter\.com|x\.com)"),
    "youtube": re.compile(r"(?i)youtube\.com"),
    "medium": re.compile(r"(?i)medium\.com"),
    "substack": re.compile(r"(?i)substack\.com"),
}


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def http_fetch(url: str, timeout: int = 15, method: str = "GET") -> Tuple[int, str, str]:
    """
    Returns: (status_code, final_url, body_text)
    """
    req = Request(url, headers={"User-Agent": "AI-Talent-Engine/1.0"}, method=method)
    with urlopen(req, timeout=timeout) as resp:
        status = getattr(resp, "status", 200)
        final_url = resp.geturl()
        raw = resp.read()
    try:
        text = raw.decode("utf-8", errors="ignore")
    except Exception:
        text = ""
    return int(status), str(final_url), text


def safe_strip(v: object) -> str:
    return "" if v is None else str(v).strip()


def normalize_phone(s: str) -> str:
    s = re.sub(r"[^\d+]", "", s)
    if s.startswith("+1"):
        s = s[2:]
    if len(s) == 10 and s.isdigit():
        return f"({s[0:3]}) {s[3:6]}-{s[6:10]}"
    return ""


@dataclass
class GithubIOProbe:
    url: str
    status: int
    final_url: str
    checked_utc: str
    method: str
    present: str
    error: str


def probe_github_io(username: str) -> GithubIOProbe:
    """
    REQUIRED first-class surface: attempt probe and record result.
    Valid outcomes include 200 (present) and 404 (not present).
    Fail closed only if probe step cannot execute (unexpected exception).
    """
    checked = utc_now()
    base = f"https://{username}.github.io/"
    method = "HEAD"
    try:
        # Try HEAD first (fast), then fallback GET if needed
        try:
            status, final_url, _ = http_fetch(base, timeout=12, method="HEAD")
        except Exception:
            method = "GET"
            status, final_url, _ = http_fetch(base, timeout=12, method="GET")
        present = "yes" if status in (200, 301, 302) else "no"
        return GithubIOProbe(
            url=base,
            status=status,
            final_url=final_url,
            checked_utc=checked,
            method=method,
            present=present,
            error="",
        )
    except Exception as e:
        # This is a hard failure in the GitHub.io contract (probe could not run)
        return GithubIOProbe(
            url=base,
            status=-1,
            final_url="",
            checked_utc=checked,
            method=method,
            present="no",
            error=str(e),
        )


def extract_links(html: str, base_url: str) -> List[str]:
    # naive href extraction, bounded and safe
    links = set()
    for m in re.finditer(r'href\s*=\s*["\']([^"\']+)["\']', html, flags=re.I):
        href = m.group(1).strip()
        if href.startswith("mailto:") or href.startswith("javascript:") or href.startswith("#"):
            continue
        abs_url = urljoin(base_url, href)
        links.add(abs_url)
    return list(links)


def same_domain(a: str, b: str) -> bool:
    try:
        return urlparse(a).netloc.lower() == urlparse(b).netloc.lower()
    except Exception:
        return False


def bounded_crawl(root: str, max_pages: int = 8, delay_s: float = 0.6) -> Tuple[List[Tuple[str, str]], str]:
    """
    Crawl up to max_pages pages on same domain, returning list of (url, html).
    """
    fetched: List[Tuple[str, str]] = []
    seen = set()
    q = [root]

    start = time.time()
    err = ""

    while q and len(fetched) < max_pages:
        u = q.pop(0)
        if u in seen:
            continue
        seen.add(u)

        try:
            status, final_url, html = http_fetch(u, timeout=18, method="GET")
            if status >= 400:
                continue
            fetched.append((final_url, html))
            time.sleep(delay_s)

            # discover more links
            for link in extract_links(html, final_url):
                if len(q) + len(fetched) >= max_pages * 3:
                    break
                if same_domain(root, link):
                    if link not in seen:
                        q.append(link)

        except Exception as e:
            err = str(e)
            break

    _ = time.time() - start
    return fetched, err


def best_email(emails: List[str]) -> Tuple[str, str]:
    if not emails:
        return "", "low"
    # Prefer non-noreply and non-github addresses
    ranked = sorted(set(emails), key=lambda x: (
        "noreply" in x.lower(),
        x.lower().endswith("users.noreply.github.com"),
        x.lower().endswith("@github.com"),
        len(x),
    ))
    chosen = ranked[0]
    conf = "high" if (not chosen.lower().endswith("users.noreply.github.com") and "noreply" not in chosen.lower()) else "medium"
    return chosen, conf


def main() -> None:
    if len(sys.argv) != 4:
        print("USAGE: python3 scripts/universal_enrichment_pipeline.py <scenario> <people_csv_normalized> <run_id>")
        sys.exit(2)

    scenario = sys.argv[1].strip()
    people_csv = Path(sys.argv[2]).expanduser().resolve()
    run_id = sys.argv[3].strip()

    if not people_csv.exists():
        print(f"ERROR: people CSV not found: {people_csv}")
        sys.exit(3)

    out_dir = OUT_LEADS / f"run_{run_id}"
    out_dir.mkdir(parents=True, exist_ok=True)
    OUT_MANIFESTS.mkdir(parents=True, exist_ok=True)

    leads_master = out_dir / f"LEADS_MASTER_{scenario}_{run_id}.csv"
    manifest_path = OUT_MANIFESTS / f"run_manifest_{scenario}_{run_id}.json"

    # Read input
    with people_csv.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        in_cols = reader.fieldnames or []

    # Canonical prefix check (hard)
    if in_cols[:2] != ["Person_ID", "Role_Type"]:
        print("ERROR: people_csv_normalized must start with Person_ID, Role_Type")
        print("Found prefix:", in_cols[:2])
        sys.exit(4)

    # Create output
    start = time.time()
    githubio_checked = 0
    githubio_found = 0

    with leads_master.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=LEAD_SCHEMA)
        w.writeheader()

        for r in rows:
            person_id = safe_strip(r.get("Person_ID"))
            role_type = safe_strip(r.get("Role_Type"))
            gh_user = safe_strip(r.get("GitHub_Username")) or person_id

            gh_url = safe_strip(r.get("GitHub_URL"))
            blog_raw = safe_strip(r.get("Blog"))

            # REQUIRED GitHub.io probe
            probe = probe_github_io(gh_user)
            githubio_checked += 1
            if probe.present == "yes":
                githubio_found += 1

            # Fail-closed if probe couldn't execute
            if probe.status == -1:
                print("ERROR: GitHub.io probe failed to execute. Contract requires probe.")
                print("User:", gh_user)
                print("Error:", probe.error)
                sys.exit(5)

            # Decide crawl root with strict priority: GitHub.io first, then Blog, then GitHub profile
            crawl_root = ""
            if probe.present == "yes":
                crawl_root = probe.final_url or probe.url
            elif "github.io" in blog_raw.lower():
                crawl_root = blog_raw
            elif blog_raw.startswith("http"):
                crawl_root = blog_raw
            elif gh_url.startswith("http"):
                crawl_root = gh_url

            fetched_pages: List[Tuple[str, str]] = []
            crawl_err = ""
            crawl_seconds = 0.0
            max_pages = 8

            enrichment_attempts = []
            emails: List[str] = []
            phones: List[str] = []
            linkedin_urls: List[str] = []
            discovered_links: List[str] = []

            if crawl_root:
                t0 = time.time()
                fetched_pages, crawl_err = bounded_crawl(crawl_root, max_pages=max_pages, delay_s=0.5)
                crawl_seconds = time.time() - t0
                enrichment_attempts.append(f"crawl:{crawl_root}")

                # Extract from pages
                for page_url, html in fetched_pages:
                    discovered_links.append(page_url)
                    emails.extend([m.group(1) for m in EMAIL_RE.finditer(html)])
                    phones.extend([m.group(0) for m in PHONE_RE.finditer(html)])
                    linkedin_urls.extend([m.group(0) for m in LINKEDIN_RE.finditer(html)])

                    # find link candidates inside html
                    for link in extract_links(html, page_url):
                        discovered_links.append(link)

            email_found, email_conf = best_email(emails)
            phone_found = ""
            phone_conf = "low"
            phone_src = ""
            phone_snip = ""
            for p in phones:
                np = normalize_phone(p)
                if np:
                    phone_found = np
                    phone_conf = "medium"
                    phone_src = "crawl"
                    phone_snip = p
                    break

            linkedin_found = ""
            linkedin_conf = "low"
            linkedin_src = ""
            linkedin_ev = ""
            if linkedin_urls:
                linkedin_found = sorted(set(linkedin_urls), key=len)[0]
                linkedin_conf = "high"
                linkedin_src = "crawl"
                linkedin_ev = crawl_root or ""

            # Other link classifications
            resume_url = ""
            cv_url = ""
            portfolio_url = ""
            scholar_url = ""
            semscholar_url = ""
            openalex_url = ""
            orcid_url = ""
            twitter_url = ""
            youtube_url = ""
            medium_url = ""
            substack_url = ""
            blog_url = ""
            blog_source = ""

            uniq_links = sorted(set([u for u in discovered_links if u.startswith("http")]))
            for u in uniq_links:
                if not resume_url and URL_HINTS["resume"].search(u):
                    resume_url = u
                if not cv_url and URL_HINTS["resume"].search(u):
                    cv_url = u
                if not scholar_url and URL_HINTS["scholar"].search(u):
                    scholar_url = u
                if not semscholar_url and URL_HINTS["semanticscholar"].search(u):
                    semscholar_url = u
                if not openalex_url and URL_HINTS["openalex"].search(u):
                    openalex_url = u
                if not orcid_url and URL_HINTS["orcid"].search(u):
                    orcid_url = u
                if not twitter_url and URL_HINTS["twitter"].search(u):
                    twitter_url = u
                if not youtube_url and URL_HINTS["youtube"].search(u):
                    youtube_url = u
                if not medium_url and URL_HINTS["medium"].search(u):
                    medium_url = u
                if not substack_url and URL_HINTS["substack"].search(u):
                    substack_url = u

            # Portfolio/blog heuristics
            if probe.present == "yes":
                portfolio_url = probe.final_url or probe.url
                blog_url = portfolio_url
                blog_source = "github_io"
            elif blog_raw.startswith("http"):
                blog_url = blog_raw
                blog_source = "github_profile_blog"

            # Provenance JSON (compact)
            prov = {
                "github_io": {
                    "url": probe.url,
                    "status": probe.status,
                    "final_url": probe.final_url,
                    "present": probe.present,
                    "checked_utc": probe.checked_utc,
                    "method": probe.method,
                },
                "crawl": {
                    "root": crawl_root,
                    "pages_fetched": len(fetched_pages),
                    "max_pages": max_pages,
                    "seconds": round(crawl_seconds, 3),
                    "error": crawl_err,
                },
                "extract": {
                    "emails_found": len(set(emails)),
                    "phones_found": len(set(phones)),
                    "linkedin_found": len(set(linkedin_urls)),
                },
            }

            # Escalation level: 0 baseline, +1 if github_io present, +1 if crawl succeeded, +1 if email found
            escalation = 0
            if probe.present == "yes":
                escalation += 1
            if len(fetched_pages) > 0:
                escalation += 1
            if email_found:
                escalation += 1

            status = "ok" if (probe.status in (200, 301, 302, 404, 410) and (crawl_err == "")) else "partial"
            if probe.status == -1:
                status = "fail"

            out: Dict[str, str] = {k: "" for k in LEAD_SCHEMA}

            # Canonical prefix (with strict ordering)
            out["Person_ID"] = person_id
            out["Role_Type"] = role_type
            out["Email"] = safe_strip(r.get("Email"))  # preserve if already present
            out["Phone"] = safe_strip(r.get("Phone"))
            out["LinkedIn_URL"] = safe_strip(r.get("LinkedIn_URL"))
            out["GitHub_URL"] = gh_url
            out["GitHub_Username"] = gh_user

            # Identity passthrough
            out["Full_Name"] = safe_strip(r.get("Name"))
            out["Name_Raw"] = safe_strip(r.get("Name"))
            out["Company"] = safe_strip(r.get("Company"))
            out["Location"] = safe_strip(r.get("Location"))
            out["Bio"] = safe_strip(r.get("Bio"))
            out["Followers"] = safe_strip(r.get("Followers"))
            out["Following"] = safe_strip(r.get("Following"))
            out["Public_Repos"] = safe_strip(r.get("Public_Repos"))
            out["Created_At"] = safe_strip(r.get("Created_At"))
            out["Updated_At"] = safe_strip(r.get("Updated_At"))
            out["Source_Scenario"] = safe_strip(r.get("Source_Scenario"))
            out["Source_Query"] = safe_strip(r.get("Source_Query"))
            out["Source_Page"] = safe_strip(r.get("Source_Page"))
            out["Source_Rank"] = safe_strip(r.get("Source_Rank"))
            out["Retrieved_At_UTC"] = safe_strip(r.get("Retrieved_At_UTC"))
            out["Scenario"] = safe_strip(r.get("Scenario"))
            out["Scenario_Score"] = safe_strip(r.get("Scenario_Score"))
            out["Scenario_Buckets"] = safe_strip(r.get("Scenario_Buckets"))
            out["Scenario_Keywords"] = safe_strip(r.get("Scenario_Keywords"))
            out["GitHub_Blog_Raw"] = blog_raw

            # GitHub.io canonical block (required columns)
            out["GitHub_IO_URL"] = probe.url
            out["GitHub_IO_HTTP_Status"] = str(probe.status)
            out["GitHub_IO_Final_URL"] = probe.final_url
            out["GitHub_IO_Checked_UTC"] = probe.checked_utc
            out["GitHub_IO_Probe_Method"] = probe.method
            out["GitHub_IO_Present"] = probe.present
            out["GitHub_IO_Error"] = probe.error

            # Crawl block
            out["Crawl_Root_URL"] = crawl_root
            out["Crawl_Pages_Fetched"] = str(len(fetched_pages))
            out["Crawl_Max_Pages"] = str(max_pages)
            out["Crawl_Seconds"] = f"{crawl_seconds:.3f}"
            out["Crawl_Error"] = crawl_err

            # Contact extraction (do not overwrite existing canonical Email/Phone/LinkedIn_URL unless blank)
            out["Email_Found"] = email_found
            out["Email_Source"] = "crawl" if email_found else ""
            out["Email_Confidence"] = email_conf if email_found else "low"
            out["Email_Evidence_Snippet"] = email_found

            out["Phone_Found"] = phone_found
            out["Phone_Source"] = phone_src
            out["Phone_Confidence"] = phone_conf
            out["Phone_Evidence_Snippet"] = phone_snip

            out["LinkedIn_Found"] = linkedin_found
            out["LinkedIn_Source"] = linkedin_src
            out["LinkedIn_Confidence"] = linkedin_conf
            out["LinkedIn_Evidence_URL"] = linkedin_ev

            if not out["Email"] and email_found:
                out["Email"] = email_found
            if not out["Phone"] and phone_found:
                out["Phone"] = phone_found
            if not out["LinkedIn_URL"] and linkedin_found:
                out["LinkedIn_URL"] = linkedin_found

            # Other signals
            out["Resume_URL"] = resume_url
            out["Resume_Source"] = "crawl" if resume_url else ""
            out["CV_URL"] = cv_url
            out["Portfolio_URL"] = portfolio_url
            out["Portfolio_Source"] = "github_io" if probe.present == "yes" else ("blog" if blog_url else "")
            out["Google_Scholar_URL"] = scholar_url
            out["Semantic_Scholar_URL"] = semscholar_url
            out["OpenAlex_URL"] = openalex_url
            out["ORCID_URL"] = orcid_url
            out["Twitter_X_URL"] = twitter_url
            out["YouTube_URL"] = youtube_url
            out["Medium_URL"] = medium_url
            out["Substack_URL"] = substack_url
            out["Blog_URL"] = blog_url
            out["Blog_Source"] = blog_source

            out["Enrichment_Attempts"] = ";".join(enrichment_attempts)
            out["Enrichment_Status"] = status
            out["Escalation_Level"] = str(escalation)
            out["Notes"] = ""
            out["Provenance_JSON"] = json.dumps(prov, ensure_ascii=False, separators=(",", ":"))

            # Final schema sanity: enforce required GitHub.io columns exist
            required_gio_cols = ["GitHub_IO_URL", "GitHub_IO_HTTP_Status", "GitHub_IO_Checked_UTC", "GitHub_IO_Present"]
            for c in required_gio_cols:
                if c not in out:
                    print(f"ERROR: Missing required GitHub.io column in output: {c}")
                    sys.exit(6)

            w.writerow(out)

    seconds = time.time() - start

    # Manifest
    payload = {
        "scenario": scenario,
        "run_id": run_id,
        "created_utc": utc_now(),
        "repo_root": str(REPO_ROOT),
        "people_csv_normalized": str(people_csv),
        "leads_master_csv": str(leads_master),
        "counts": {
            "people_rows": len(rows),
            "leads_rows": len(rows),
        },
        "github_io": {
            "checked_rows": githubio_checked,
            "found_rows": githubio_found,
            "required_first_class_surface": True,
        },
        "runtime": {
            "seconds": round(seconds, 3),
        },
        "contracts": {
            "canonical_prefix": CANON_PREFIX,
            "github_io_probe_required": True,
            "output_schema_columns": len(LEAD_SCHEMA),
        },
    }
    manifest_path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")

    # Hard fail if leads master missing or schema too small
    if not leads_master.exists():
        print(f"ERROR: LEADS_MASTER not created: {leads_master}")
        sys.exit(7)
    if len(LEAD_SCHEMA) < 70:
        print("ERROR: Schema contract violated: expected 70+ columns")
        print("Columns:", len(LEAD_SCHEMA))
        sys.exit(8)

    print(f"OK: LEADS_MASTER written: {leads_master}")
    print(f"OK: Columns: {len(LEAD_SCHEMA)}")
    print(f"OK: Rows: {len(rows)}")
    print(f"OK: GitHub.io checked: {githubio_checked}, present: {githubio_found}")
    print(f"OK: Manifest written: {manifest_path}")


if __name__ == "__main__":
    main()
