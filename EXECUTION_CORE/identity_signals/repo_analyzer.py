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
Repository Analyzer Module
Extracts repository evidence and technical signals from existing data
"""


def enrich_row(row: dict) -> dict:
    """
    Extract repository evidence from existing data
    
    Args:
        row: Input row dictionary
        
    Returns:
        Dict with repository evidence fields
    """
    result = {}
    
    github_url = row.get('Github_URL', '').strip()
    key_tech = row.get('Key_Technologies', '').strip()
    
    # Repo evidence URLs
    if github_url:
        result['Repo_Evidence_URLs'] = github_url
        result['Repo_Evidence_Count'] = '1'
        result['GitHub_Repo_Evidence_Why'] = 'Primary GitHub profile URL'
    else:
        result['Repo_Evidence_URLs'] = ''
        result['Repo_Evidence_Count'] = '0'
        result['GitHub_Repo_Evidence_Why'] = ''
    
    # Determinative skill areas from Key_Technologies
    result['Determinative_Skill_Areas'] = key_tech
    
    # Extract benchmarks worked on
    result['Benchmarks_Worked_On'] = _extract_benchmarks(key_tech)
    
    # Extract model families
    result['Primary_Model_Families'] = _extract_model_families(key_tech)
    
    # Repo topics/keywords (would come from API)
    result['Repo_Topics_Keywords'] = ''
    
    # Production vs Research indicator
    result['Production_vs_Research_Indicator'] = _classify_prod_vs_research(row)
    
    return result


def _extract_benchmarks(tech: str) -> str:
    """Extract benchmark names from technology keywords"""
    if not tech:
        return ''
    
    tech_lower = tech.lower()
    benchmarks = []
    
    # Common ML benchmarks
    benchmark_keywords = [
        'glue', 'superglue', 'squad', 'mmlu', 'hellaswag', 'truthfulqa',
        'humaneval', 'mbpp', 'gsm8k', 'math', 'arc', 'winogrande',
        'boolq', 'piqa', 'siqa', 'copa', 'drop', 'race'
    ]
    
    for keyword in benchmark_keywords:
        if keyword in tech_lower:
            benchmarks.append(keyword.upper())
    
    return ', '.join(benchmarks)


def _extract_model_families(tech: str) -> str:
    """Extract model family names from technology keywords"""
    if not tech:
        return ''
    
    tech_lower = tech.lower()
    models = []
    
    # Common model families
    model_keywords = [
        'gpt', 'bert', 'llama', 'claude', 'palm', 'gemini', 't5',
        'bart', 'roberta', 'xlnet', 'electra', 'albert', 'distilbert',
        'falcon', 'mistral', 'mixtral', 'phi', 'qwen'
    ]
    
    for keyword in model_keywords:
        if keyword in tech_lower:
            models.append(keyword.upper())
    
    return ', '.join(models)


def _classify_prod_vs_research(row: dict) -> str:
    """Classify as production-oriented or research-oriented"""
    role = row.get('Role_Type', '').lower()
    
    if 'research' in role or 'scientist' in role:
        return 'Research-oriented'
    elif 'engineer' in role or 'infrastructure' in role:
        return 'Production-oriented'
    else:
        return 'Balanced'
