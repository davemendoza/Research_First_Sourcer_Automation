# ===============================================
#  AI TALENT ENGINE — SIGNAL INTELLIGENCE
#
#  Proprietary and Confidential
#
#  © 2025–2026 L. David Mendoza. All Rights Reserved.
#
#  This file is part of the AI Talent Engine — Signal Intelligence system.
#  It contains proprietary methodologies, schemas, scoring logic, and
#  execution workflows developed by L. David Mendoza.
#
#  Unauthorized copying, modification, distribution, disclosure, or use
#  of this file or its contents, in whole or in part, is strictly prohibited
#  without prior written consent from the author.
#
#  This code is intended solely for authorized evaluation, demonstration,
#  and execution under controlled conditions as defined in the
#  Canonical Requirements Manifest and Claude Master Execution Guidebook.
#
#  GOVERNANCE NOTICE:
#  — Public-source data only
#  — No inferred or fabricated data
#  — No private or gated scraping
#  — Deterministic, audit-ready execution required
#
# ===============================================

"""
URL Normalizer Module
Extracts usernames and normalizes profile URLs
"""

import re


def enrich_row(row: dict) -> dict:
    """
    Normalize URLs and extract usernames
    
    Args:
        row: Input row dictionary
        
    Returns:
        Dict with normalized URL fields
    """
    result = {}
    
    github_url = row.get('Github_URL', '').strip()
    github_io = row.get('Github_IO_URL', '').strip()
    
    # Extract GitHub username
    if github_url:
        match = re.search(r'github\.com/([^/\?#]+)', github_url, re.IGNORECASE)
        if match:
            username = match.group(1)
            if username.lower() not in ['orgs', 'organizations', 'repos', 'settings']:
                result['GitHub_Username'] = username
                result['GitHub_Profile_URL'] = f"https://github.com/{username}"
    
    # Normalize GitHub.io URL
    if github_io:
        result['GitHub_IO_URLs'] = github_io
    elif result.get('GitHub_Username'):
        result['GitHub_IO_URLs'] = f"https://{result['GitHub_Username']}.github.io"
    
    # LinkedIn normalization (preserve if exists)
    linkedin = row.get('LinkedIn_URL', '').strip()
    if linkedin:
        result['LinkedIn_Public_URL'] = linkedin
    
    return result
