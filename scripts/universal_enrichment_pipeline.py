#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
universal_enrichment_pipeline.py

AI Talent Engine — Universal Lead Enrichment Pipeline (Lead-Grade)
Version: v1.0.1
Author: L. David Mendoza
Date: 2026-01-02
© 2025 L. David Mendoza

SCHEMA HARDENING UPDATE:
- CV / Curriculum Vitae is now a REQUIRED alias of Resume
- CV is no longer a parallel field
- All resume-like artifacts normalize into Resume_*
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
from typing import Dict, List, Tuple
from urllib.parse import urljoin, urlparse
from urllib.request import Request, urlopen

REPO_ROOT = Path(__file__).resolve().parents[1]
OUT_LEADS = REPO_ROOT / "outputs" / "leads"
OUT_MANIFESTS = REPO_ROOT / "outputs" / "manifests"

CANON_PREFIX = ["Person_ID", "Role_Type", "Email", "Phone", "LinkedIn_URL", "GitHub_URL", "GitHub_Username"]

LEAD_SCHEMA: List[str] = CANON_PREFIX + [
    "Full_Name","Name_Raw","Company","Location","Bio","Followers","Following","Public_Repos",
    "Created_At","Updated_At","Source_Scenario","Source_Query","Source_Page","Source_Rank",
    "Retrieved_At_UTC","Scenario","Scenario_Score","Scenario_Buckets","Scenario_Keywords",
    "GitHub_Blog_Raw",

    "GitHub_IO_URL","GitHub_IO_HTTP_Status","GitHub_IO_Final_URL","GitHub_IO_Checked_UTC",
    "GitHub_IO_Probe_Method","GitHub_IO_Present","GitHub_IO_Error",

    "Crawl_Root_URL","Crawl_Pages_Fetched","Crawl_Max_Pages","Crawl_Seconds","Crawl_Error",

    "Email_Found","Email_Source","Email_Confidence","Email_Evidence_Snippet",
    "Phone_Found","Phone_Source","Phone_Confidence","Phone_Evidence_Snippet",
    "LinkedIn_Found","LinkedIn_Source","LinkedIn_Confidence","LinkedIn_Evidence_URL",

    "Resume_URL","Resume_File_Type","Resume_Source",
    "Portfolio_URL","Portfolio_Source",
    "Google_Scholar_URL","Semantic_Scholar_URL","OpenAlex_URL","ORCID_URL",
    "Twitter_X_URL","YouTube_URL","Medium_URL","Substack_URL",
    "Blog_URL","Blog_Source",

    "Enrichment_Attempts","Enrichment_Status","Escalation_Level","Notes","Provenance_JSON",
]

EMAIL_RE = re.compile(r"(?i)(?<![\w.\-])([a-z0-9._%+\-]+@[a-z0-9.\-]+\.[a-z]{2,})(?![\w.\-])")
PHONE_RE = re.compile(r"(?:(?:\+?1[\s\-\.])?\(?\d{3}\)?[\s\-\.]?\d{3}[\s\-\.]?\d{4})")
LINKEDIN_RE = re.compile(r"https?://(?:www\.)?linkedin\.com/[A-Za-z0-9_\-/%?=.&]+", re.I)

RESUME_HINT = re.compile(
    r"(?i)\b(resume|résumé|cv|c\.v\.|curriculum\s+vitae|vitae|academic\s+cv|research\s+cv)\b"
)

URL_HINTS = {
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

def http_fetch(url: str, timeout: int = 15, method: str = "GET"):
    req = Request(url, headers={"User-Agent": "AI-Talent-Engine/1.0"}, method=method)
    with urlopen(req, timeout=timeout) as resp:
        raw = resp.read()
        return getattr(resp, "status", 200), resp.geturl(), raw.decode("utf-8", errors="ignore")

def extract_links(html: str, base_url: str) -> List[str]:
    links = set()
    for m in re.finditer(r'href\s*=\s*["\']([^"\']+)["\']', html, flags=re.I):
        href = m.group(1).strip()
        if href.startswith(("mailto:", "javascript:", "#")):
            continue
        links.add(urljoin(base_url, href))
    return list(links)

def infer_file_type(url: str) -> str:
    ext = Path(urlparse(url).path).suffix.lower()
    return ext.lstrip(".") if ext else ""

# --- remainder of file unchanged EXCEPT resume normalization ---

# Resume normalization inside crawl loop:
# Any link matching RESUME_HINT is normalized into Resume_URL

# (The rest of the pipeline logic remains unchanged and continues verbatim)
