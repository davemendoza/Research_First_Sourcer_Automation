#!/usr/bin/env python3
"""
citation_intelligence_api.py

Phase 2 – Citation Intelligence (API-Only, Deterministic)

Purpose:
--------
Provide safe, auditable citation intelligence for researchers using
official public APIs only (no scraping, no bots, no inference).

Primary source:
- Semantic Scholar API (public, unauthenticated usage)

Secondary fallback:
- OpenAlex API (no API key required)

Design Principles:
------------------
- Zero HTML scraping
- Zero headless browsers
- Zero guessing or inference
- Defensive JSON handling
- Deterministic outputs
- Explicit recording of missing data

This module is intentionally conservative and interview-safe.

Author:
-------
Dave Mendoza
© 2025 L. David Mendoza. All rights reserved.
"""

import os
import time
import requests
from typing import Optional, Dict, Any

# -------------------------
# Configuration
# -------------------------

SEMANTIC_SCHOLAR_AUTHOR_SEARCH = "https://api.semanticscholar.org/graph/v1/author/search"
OPENALEX_AUTHOR_SEARCH = "https://api.openalex.org/authors"

DEFAULT_TIMEOUT = 10  # seconds
REQUEST_SLEEP = 0.5  # gentle pacing, not rate-limit gaming

USER_AGENT = "AI-Talent-Engine-Citation-Intelligence/1.0"


# -------------------------
# Defensive JSON Helper
# -------------------------

def safe_json(response: requests.Response) -> Optional[Dict[str, Any]]:
    """
    Safely parse JSON from an HTTP response.

    Guards against:
    - Non-200 responses
    - Empty bodies
    - HTML or edge-case payloads
    - Partial or malformed JSON

    Returns:
        dict if valid JSON, otherwise None
    """
    if response is None:
        return None

    if response.status_code != 200:
        return None

    if not response.text:
        return None

    text = response.text.strip()
    if not text.startswith("{"):
        return None

    try:
        return response.json()
    except ValueError:
        return None


# -------------------------
# Semantic Scholar
# -------------------------

def query_semantic_scholar(full_name: str) -> Optional[Dict[str, Any]]:
    """
    Query Semantic Scholar for author-level citation data.

    Returns a normalized dict if found, otherwise None.
    """
    headers = {
        "User-Agent": USER_AGENT
        # Intentionally no API key required for Phase 2
    }

    params = {
        "query": full_name,
        "limit": 1,
        "fields": "name,hIndex,citationCount,paperCount"
    }

    try:
        response = requests.get(
            SEMANTIC_SCHOLAR_AUTHOR_SEARCH,
            headers=headers,
            params=params,
            timeout=DEFAULT_TIMEOUT
        )
    except requests.RequestException:
        return None

    data = safe_json(response)
    if not data:
        return None

    authors = data.get("data", [])
    if not authors:
        return None

    author = authors[0]

    return {
        "source": "Semantic Scholar",
        "total_citations": author.get("citationCount"),
        "h_index": author.get("hIndex"),
        "works_count": author.get("paperCount"),
        "provenance": "Semantic Scholar Author Search API"
    }


# -------------------------
# OpenAlex
# -------------------------

def query_openalex(full_name: str) -> Optional[Dict[str, Any]]:
    """
    Query OpenAlex for author-level citation data.

    Returns a normalized dict if found, otherwise None.
    """
    headers = {
        "User-Agent": USER_AGENT
    }

    params = {
        "search": full_name,
        "per-page": 1
    }

    try:
        response = requests.get(
            OPENALEX_AUTHOR_SEARCH,
            headers=headers,
            params=params,
            timeout=DEFAULT_TIMEOUT
        )
    except requests.RequestException:
        return None

    data = safe_json(response)
    if not data:
        return None

    results = data.get("results", [])
    if not results:
        return None

    author = results[0]

    citation_stats = author.get("cited_by_count")

    return {
        "source": "OpenAlex",
        "total_citations": citation_stats,
        "h_index": None,  # OpenAlex does not expose h-index directly
        "works_count": author.get("works_count"),
        "provenance": "OpenAlex Authors API"
    }


# -------------------------
# Public API
# -------------------------

def get_citation_profile(
    full_name: str,
    prefer_semantic_scholar: bool = True
) -> Dict[str, Any]:
    """
    Public interface for citation intelligence.

    Strategy:
    ---------
    - Try Semantic Scholar first (if preferred)
    - Fall back to OpenAlex
    - Never merge, infer, or guess
    - Always return a deterministic structure

    Returns:
        dict with citation fields populated or explicitly None
    """
    result = None

    if prefer_semantic_scholar:
        result = query_semantic_scholar(full_name)
        time.sleep(REQUEST_SLEEP)

    if not result:
        result = query_openalex(full_name)
        time.sleep(REQUEST_SLEEP)

    if result:
        return result

    # Explicit, defensible fallback
    return {
        "source": "Not Publicly Available",
        "total_citations": None,
        "h_index": None,
        "works_count": None,
        "provenance": None
    }


# -------------------------
# CLI Smoke Test (Optional)
# -------------------------

if __name__ == "__main__":
    name = "Geoffrey Hinton"
    profile = get_citation_profile(name)
    print(f"Citation profile for {name}:")
    for k, v in profile.items():
        print(f"  {k}: {v}")
