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
Name Splitter Module
Splits Full_Name into First_Name and Last_Name using whitespace rules only
"""


def enrich_row(row: dict) -> dict:
    """
    Split Full_Name into First_Name and Last_Name
    
    Args:
        row: Input row dictionary
        
    Returns:
        Dict with First_Name and Last_Name keys
    """
    full_name = row.get('Full_Name', '').strip()
    
    if not full_name:
        return {'First_Name': '', 'Last_Name': ''}
    
    parts = [p.strip() for p in full_name.split() if p.strip()]
    
    if len(parts) == 0:
        return {'First_Name': '', 'Last_Name': ''}
    elif len(parts) == 1:
        return {'First_Name': parts[0], 'Last_Name': ''}
    else:
        return {'First_Name': parts[0], 'Last_Name': parts[-1]}
