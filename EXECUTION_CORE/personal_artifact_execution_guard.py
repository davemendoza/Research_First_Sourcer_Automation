#!/usr/bin/env python3
"""
personal_artifact_execution_guard.py

Execution Guard & Budget Enforcer
Author: L. David Mendoza © 2026

Purpose:
- Enforce crawl budgets
- Enforce domain limits
- Make scraping defensible in demos and audits

No scraping. No mutation.
"""

MAX_TOTAL_PAGES = 20
MAX_DOMAINS = 1


def validate_scrape(scraper_output):
    crawl_log = scraper_output.get("crawl_log", {}) or {}
    pages = crawl_log.get("pages_visited", []) or []

    if len(pages) > MAX_TOTAL_PAGES:
        return False, "Exceeded maximum crawl page budget."

    domains = set()
    for url in pages:
        try:
            domains.add(url.split("/")[2])
        except Exception:
            continue

    if len(domains) > MAX_DOMAINS:
        return False, "Exceeded maximum domain crawl limit."

    return True, None
