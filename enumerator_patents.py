#!/usr/bin/env python3
"""
AI Talent Engine – Patents Enumerator (Enrichment)
Version: v1.0.0-ultra
Date: 2025-12-30
© 2025 L. David Mendoza. All Rights Reserved.

NOTE
This enumerator is included for completeness and enrichment.
It is NOT relied upon for primary volume due to throttling risk.

It supports extracting inventors from explicit patents.google.com/patent/... pages.
"""

from __future__ import annotations

import time
import random
import requests
from bs4 import BeautifulSoup
from typing import List, Optional

UA = "AI-Talent-Engine/PatentsEnumerator (polite)"

def _sleep():
    time.sleep(random.uniform(1.0, 2.2))

def _get(url: str, timeout: int = 30, retries: int = 5) -> Optional[str]:
    headers = {"User-Agent": UA}
    backoff = 1.0
    for i in range(retries):
        try:
            r = requests.get(url, headers=headers, timeout=timeout)
            if r.status_code == 200 and r.text:
                txt = r.text.lower()
                if "unusual traffic" in txt or "/sorry/" in txt:
                    time.sleep(backoff * (i + 2))
                    backoff *= 1.7
                    continue
                return r.text
            if r.status_code in (429, 503):
                time.sleep(backoff * (i + 2))
                backoff *= 1.7
                continue
        except Exception:
            time.sleep(backoff * (i + 2))
            backoff *= 1.7
    return None

def extract_inventors(patent_url: str) -> List[dict]:
    html = _get(patent_url)
    _sleep()
    if not html:
        return []

    soup = BeautifulSoup(html, "html.parser")
    inv = []
    for tag in soup.select("dd[itemprop='inventor'] span[itemprop='name']"):
        name = tag.get_text(strip=True)
        if name:
            inv.append(name)

    out = []
    for n in list(dict.fromkeys(inv))[:50]:
        out.append({
            "source_systems": ["Patents"],
            "openalex_author_id": "",
            "github_login": "",
            "full_name": n,
            "primary_affiliation": "",
            "role_hint": "Inventor",
            "evidence_urls": [patent_url],
            "raw_signals": {"topics": ["patent_inventor"]},
        })
    return out
