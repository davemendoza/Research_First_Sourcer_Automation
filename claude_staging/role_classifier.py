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
Role Classifier Module
Classifies AI talent into canonical 27-role taxonomy
"""

import sys
import os
from typing import Dict, List, Optional

# Import the canonical role registry
sys.path.insert(0, '/mnt/user-data/uploads')
from ai_role_registry import (
    resolve_role, 
    is_valid_role, 
    CANONICAL_AI_ROLE_TYPES
)


class RoleClassifier:
    """Classify talent records into canonical AI role types"""
    
    # Keywords for role classification
    ROLE_KEYWORDS = {
        "Foundational AI Scientist": [
            "transformer", "architecture", "foundational", "theory", "mathematical",
            "proof", "fundamental", "breakthrough"
        ],
        "Frontier AI Research Scientist": [
            "research", "frontier", "agi", "reasoning", "novel", "cutting-edge"
        ],
        "Applied AI Research Scientist": [
            "applied research", "application", "deployment", "production research"
        ],
        "Machine Learning Research Scientist": [
            "machine learning research", "ml research", "statistical learning"
        ],
        "RLHF Research Scientist": [
            "rlhf", "reinforcement learning", "human feedback", "alignment", 
            "reward model", "ppo", "dpo"
        ],
        "AI Performance Engineer": [
            "performance", "optimization", "inference", "speed", "efficiency"
        ],
        "Model Training Engineer": [
            "training", "pretraining", "fine-tuning", "distributed training"
        ],
        "Inference Optimization Engineer": [
            "inference", "serving", "deployment", "runtime", "tensorrt", "onnx"
        ],
        "LLM Systems Engineer": [
            "llm", "large language model", "gpt", "bert", "transformer systems"
        ],
        "AI Engineer (General)": [
            "ai engineer", "ml engineer", "machine learning engineer"
        ],
        "Applied Machine Learning Engineer": [
            "applied ml", "ml applications", "ml deployment"
        ],
        "Generative AI Engineer": [
            "generative", "diffusion", "gan", "vae", "stable diffusion", "dalle"
        ],
        "LLM Application Engineer": [
            "llm application", "rag", "retrieval augmented", "prompt engineering"
        ],
        "AI Infrastructure Engineer": [
            "ai infrastructure", "ml infrastructure", "ai platform"
        ],
        "ML Infrastructure Engineer": [
            "ml infra", "mlops infrastructure", "training infrastructure"
        ],
        "Distributed Systems Engineer (AI Focus)": [
            "distributed", "parallel", "cluster", "kubernetes", "ray"
        ],
        "Site Reliability Engineer (AI / ML)": [
            "sre", "reliability", "production", "monitoring", "uptime"
        ],
        "Platform Engineer (AI Systems)": [
            "platform", "infrastructure platform", "ml platform"
        ],
        "Machine Learning Engineer (Data-Centric)": [
            "data-centric", "data quality", "data engineering", "etl"
        ],
        "Data Engineer (AI Pipelines)": [
            "data pipeline", "data engineering", "airflow", "spark"
        ],
        "MLOps Engineer": [
            "mlops", "ml operations", "deployment automation", "ci/cd ml"
        ],
        "Forward Deployed Engineer (AI)": [
            "forward deployed", "customer", "field engineer", "solutions"
        ],
        "AI Solutions Architect": [
            "solutions architect", "technical architect", "system design"
        ],
        "Developer Relations Engineer (AI)": [
            "devrel", "developer relations", "developer advocate", "community"
        ],
        "Technical Evangelist (AI / ML)": [
            "evangelist", "advocate", "education", "outreach"
        ],
        "AI Safety Engineer / Researcher": [
            "safety", "alignment", "interpretability", "robustness", "fairness"
        ],
        "AI Evaluation & Benchmarking Specialist": [
            "evaluation", "benchmark", "testing", "validation", "metrics"
        ]
    }
    
    def __init__(self):
        """Initialize classifier"""
        pass
    
    def classify(self, record: Dict) -> str:
        """
        Classify record into canonical AI role type
        
        Args:
            record: Talent record to classify
            
        Returns:
            Canonical role type string
        """
        # Check if role already exists in record
        existing_role = record.get('AI_Role_Type', '')
        if existing_role and str(existing_role).strip() and existing_role != 'nan':
            existing_role_str = str(existing_role).strip()
            if is_valid_role(existing_role_str):
                return existing_role_str
        
        # Try to resolve from title
        title = record.get('Current_Title', '')
        if title and str(title).strip() and str(title) != 'nan':
            resolved = resolve_role(str(title))
            if resolved:
                record['AI_Role_Type'] = resolved
                return resolved
        
        # Classify based on evidence
        role = self._classify_from_evidence(record)
        if role:
            record['AI_Role_Type'] = role
            return role
        
        # Default classification
        default_role = "AI Engineer (General)"
        record['AI_Role_Type'] = default_role
        return default_role
    
    def _classify_from_evidence(self, record: Dict) -> Optional[str]:
        """Classify based on evidence fields"""
        # Gather all text fields for analysis - handle NaN values
        def safe_str(val):
            if val is None or (isinstance(val, float) and val != val):  # NaN check
                return ''
            return str(val)
        
        text_fields = [
            safe_str(record.get('GitHub_Bio', '')),
            safe_str(record.get('Repo_Topics_Keywords', '')),
            safe_str(record.get('Current_Title', '')),
            safe_str(record.get('Primary_Specialties', '')),
            safe_str(record.get('Research_Areas', '')),
            safe_str(record.get('Determinative_Skill_Areas', ''))
        ]
        
        combined_text = ' '.join(text_fields).lower()
        
        # Score each role based on keyword matches
        role_scores = {}
        for role, keywords in self.ROLE_KEYWORDS.items():
            score = sum(1 for keyword in keywords if keyword.lower() in combined_text)
            if score > 0:
                role_scores[role] = score
        
        # Return highest scoring role
        if role_scores:
            best_role = max(role_scores.items(), key=lambda x: x[1])[0]
            return best_role
        
        return None
    
    def get_role_tier(self, role: str) -> str:
        """
        Get tier classification for role
        
        Args:
            role: Canonical role type
            
        Returns:
            Tier string (Research / Engineering / Infrastructure / Applied)
        """
        if "Research Scientist" in role or "Foundational" in role or "Frontier" in role:
            return "Research"
        elif "Infrastructure" in role or "Platform" in role or "MLOps" in role:
            return "Infrastructure"
        elif "Engineer" in role:
            return "Engineering"
        else:
            return "Applied"
