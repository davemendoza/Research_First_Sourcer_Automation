#!/usr/bin/env python3
"""
personal_artifact_blank_reasoner.py

Day-2 Blank Explanation & Reasoning Module
Author: L. David Mendoza © 2026

Purpose:
- Explain why personal artifact fields are blank
- Eliminate ambiguity during demos
- Produce deterministic, human-readable reasons

This module performs:
✓ blank reasoning
✓ crawl outcome interpretation
✗ no scraping
✗ no inference
✗ no overwrites
"""

# ------------------------------------------------------------------------------
# REASON CODES (LOCKED VOCABULARY)
# ------------------------------------------------------------------------------

REASONS = {
    "NO_GITHUB_IO": "No github.io site detected for this profile.",
    "NO_PERSONAL_DOMAIN": "No personal website linked from GitHub profile.",
    "CRAWLED_NO_CONTACT": "Personal site crawled but no public contact information was found.",
    "CRAWL_DEPTH_LIMIT": "Crawl stopped at depth limit before contact information was encountered.",
    "NO_CV_FOUND": "No CV or resume link was published on the personal site.",
    "NAME_NOT_PUBLISHED": "Full name was not explicitly published on the personal site.",
    "SCRAPE_SKIPPED": "Scraping was skipped due to missing identity anchors.",
}

# ------------------------------------------------------------------------------
# CORE LOGIC
# ------------------------------------------------------------------------------

def reason_for_email(scraper_output):
    discovered = scraper_output.get("discovered", {})
    crawl_log = scraper_output.get("crawl_log", {})

    if discovered.get("emails"):
        return None

    if discovered.get("github_io_url") is None and discovered.get("personal_domain") is None:
        return REASONS["NO_GITHUB_IO"]

    if crawl_log.get("stop_reason") == "depth_limit":
        return REASONS["CRAWL_DEPTH_LIMIT"]

    return REASONS["CRAWLED_NO_CONTACT"]


def reason_for_cv(scraper_output):
    discovered = scraper_output.get("discovered", {})
    crawl_log = scraper_output.get("crawl_log", {})

    if discovered.get("cv_urls"):
        return None

    if discovered.get("github_io_url") is None and discovered.get("personal_domain") is None:
        return REASONS["NO_PERSONAL_DOMAIN"]

    if crawl_log.get("stop_reason") == "depth_limit":
        return REASONS["CRAWL_DEPTH_LIMIT"]

    return REASONS["NO_CV_FOUND"]


def reason_for_name(scraper_output):
    discovered = scraper_output.get("discovered", {})

    if discovered.get("full_name"):
        return None

    return REASONS["NAME_NOT_PUBLISHED"]


# ------------------------------------------------------------------------------
# PUBLIC ENTRYPOINT
# ------------------------------------------------------------------------------

def run(scraper_output):
    """
    Returns a dict of blank explanations.
    Only populated where fields are blank.
    """

    explanations = {}

    email_reason = reason_for_email(scraper_output)
    if email_reason:
        explanations["Primary_Email_Why_Blank"] = email_reason

    cv_reason = reason_for_cv(scraper_output)
    if cv_reason:
        explanations["CV_URL_Why_Blank"] = cv_reason

    name_reason = reason_for_name(scraper_output)
    if name_reason:
        explanations["Full_Name_Why_Blank"] = name_reason

    return explanations
