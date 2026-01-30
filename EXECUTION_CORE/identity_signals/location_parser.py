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
Location Parser Module
Parses free-text location into City, State, Country components
"""

import re


def enrich_row(row: dict) -> dict:
    """
    Parse location into components
    
    Args:
        row: Input row dictionary
        
    Returns:
        Dict with Location_City, Location_State, Location_Country keys
    """
    location = row.get('Location', '').strip()
    
    if not location:
        return {
            'Location_City': '',
            'Location_State': '',
            'Location_Country': ''
        }
    
    # Pattern: "City, State, Country" or "City, Country"
    pattern = re.compile(r'^\s*(?P<city>[^,]+)\s*(?:,\s*(?P<state>[^,]+)\s*)?(?:,\s*(?P<country>[^,]+)\s*)?$')
    match = pattern.match(location)
    
    if not match:
        # Cannot parse - put in city field
        return {
            'Location_City': location,
            'Location_State': '',
            'Location_Country': ''
        }
    
    return {
        'Location_City': (match.group('city') or '').strip(),
        'Location_State': (match.group('state') or '').strip(),
        'Location_Country': (match.group('country') or '').strip()
    }
