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
Metadata Stamper Module
Populates mechanical metadata fields
"""

import os


PIPELINE_VERSION = "v1.0.0-phase2"


def enrich_row(row: dict, output_path: str = '') -> dict:
    """
    Stamp metadata fields
    
    Args:
        row: Input row dictionary
        output_path: Optional output file path
        
    Returns:
        Dict with metadata fields
    """
    result = {}
    
    # Pipeline version
    result['Pipeline_Version'] = PIPELINE_VERSION
    
    # Output file path
    if output_path:
        result['Output_File_Path'] = os.path.abspath(output_path)
    else:
        result['Output_File_Path'] = ''
    
    # Row validity status
    has_name = bool(row.get('Full_Name', '').strip())
    has_github = bool(row.get('GitHub_Profile_URL', '').strip())
    
    if has_name and has_github:
        result['Row_Validity_Status'] = 'OK'
    elif has_name:
        result['Row_Validity_Status'] = 'PARTIAL'
    else:
        result['Row_Validity_Status'] = 'INVALID'
    
    # GPT Slim eligibility
    has_skills = bool(row.get('Determinative_Skill_Areas', '').strip())
    has_role = bool(row.get('Role_Type', '').strip())
    
    if has_github and has_role and has_skills:
        result['GPT_Slim_Input_Eligible'] = 'TRUE'
        result['GPT_Slim_Rationale'] = 'Has GitHub identity, role, and skill signals'
    elif has_github:
        result['GPT_Slim_Input_Eligible'] = 'PARTIAL'
        result['GPT_Slim_Rationale'] = 'Has GitHub identity but missing role or skills'
    else:
        result['GPT_Slim_Input_Eligible'] = 'FALSE'
        result['GPT_Slim_Rationale'] = 'Missing GitHub identity'
    
    return result
