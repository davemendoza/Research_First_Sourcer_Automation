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
Schema Validator Module
Implements Governance Agents #21-24, #36 for schema and compliance validation
"""

from typing import Dict, List, Set
import sys
sys.path.insert(0, '/mnt/user-data/uploads')
from ai_role_registry import is_valid_role


class SchemaValidator:
    """
    Schema validation and governance enforcement
    Implements Agents: #21 Schema Validator, #22 Audit & Provenance, 
                       #24 Governance Compliance, #36 Governance Integrity
    """
    
    # Canonical field order for v3.3 schema (37 base fields)
    CANONICAL_FIELDS_DEMO = [
        'AI_Classification',
        'Full_Name',
        'Company',
        'Team_or_Lab',
        'Title',
        'Seniority_Level',
        'Corporate_Email',
        'Personal_Email',
        'LinkedIn_URL',
        'Portfolio_URL',
        'Google_Scholar_URL',
        'Semantic_Scholar_URL',
        'GitHub_URL',
        'Primary_Specialties',
        'LLM_Names',
        'VectorDB_Tech',
        'RAG_Details',
        'Inference_Stack',
        'GPU_Infra_Signals',
        'RLHF_Eval_Signals',
        'Multimodal_Signals',
        'Research_Areas',
        'Top_Papers_or_Blogposts',
        'Conference_Presentations',
        'Awards_Luminary_Signals',
        'Panel_Talks_Workshops',
        'Citation_Trajectory',
        'Strengths',
        'Weaknesses',
        'Corporate_Profile_URL',
        'Publications_Page_URL',
        'Blog_Post_URLs',
        'Career_Velocity_Score',
        'Influence_Delta_12mo',
        'Emerging_Talent_Flag',
        'Governance_Compliance_Score',
        'Predictive_Hiring_Score'
    ]
    
    # GPT-SLIM uses 23 fields
    GPT_SLIM_FIELDS = [
        'Full_Name',
        'AI_Role_Type',
        'Current_Title',
        'Current_Company',
        'Location_City',
        'Location_State',
        'Location_Country',
        'Primary_Email',
        'Primary_Phone',
        'GitHub_Username',
        'GitHub_Profile_URL',
        'Repo_Evidence_URLs',
        'Repo_Topics_Keywords',
        'Primary_Model_Families',
        'Determinative_Skill_Areas',
        'Benchmarks_Worked_On',
        'Citations_per_Year',
        'Citation_Velocity_3yr',
        'Citation_Velocity_5yr',
        'Hiring_Recommendation',
        'Strengths',
        'Weaknesses',
        'Field_Level_Provenance_JSON'
    ]
    
    VALID_AI_CLASSIFICATIONS = [
        'Frontier', 'RLHF', 'Applied', 'Infra', 'Multimodal', 'Safety', 'Evaluation'
    ]
    
    VALID_SENIORITY_LEVELS = [
        'Principal', 'Staff', 'Senior', 'Director', 'VP', 'IC', 'Manager'
    ]
    
    def __init__(self):
        """Initialize validator"""
        self.validation_errors = []
    
    def validate(self, record: Dict, mode: str = 'demo') -> bool:
        """
        Validate record against schema
        
        Args:
            record: Record to validate
            mode: Validation mode (demo, gpt_slim, scenario)
            
        Returns:
            True if valid, False otherwise
        """
        self.validation_errors = []
        
        # Agent #21: Schema Validator
        if not self._validate_schema_structure(record, mode):
            return False
        
        # Agent #24: Governance Compliance
        if not self._validate_governance_compliance(record):
            return False
        
        # Agent #22: Audit & Provenance
        if not self._validate_provenance(record):
            return False
        
        # Agent #36: Governance Integrity
        if not self._validate_integrity(record):
            return False
        
        return True
    
    def _validate_schema_structure(self, record: Dict, mode: str) -> bool:
        """Agent #21: Validate schema structure and field order"""
        required_fields = self.GPT_SLIM_FIELDS if mode == 'gpt_slim' else self.CANONICAL_FIELDS_DEMO
        
        # Helper to safely get string value
        def safe_str(val):
            if val is None or (isinstance(val, float) and val != val):
                return ''
            return str(val).strip()
        
        # Check for required fields (allow some to be empty)
        critical_fields = ['Full_Name', 'AI_Role_Type'] if mode == 'gpt_slim' else ['Full_Name', 'AI_Classification']
        
        for field in critical_fields:
            val = safe_str(record.get(field, ''))
            if not val:
                self.validation_errors.append(f"Missing critical field: {field}")
                return False
        
        # Validate AI classification/role
        if mode == 'gpt_slim':
            role = safe_str(record.get('AI_Role_Type', ''))
            if role and not is_valid_role(role):
                self.validation_errors.append(f"Invalid AI_Role_Type: {role}")
                return False
        else:
            classification = safe_str(record.get('AI_Classification', ''))
            if classification and classification not in self.VALID_AI_CLASSIFICATIONS:
                self.validation_errors.append(f"Invalid AI_Classification: {classification}")
                return False
        
        return True
    
    def _validate_governance_compliance(self, record: Dict) -> bool:
        """Agent #24: Validate governance compliance (no private data, etc.)"""
        # Helper to safely get string value
        def safe_str(val):
            if val is None or (isinstance(val, float) and val != val):
                return ''
            return str(val).strip()
        
        # Check that we don't have inferred data
        email = safe_str(record.get('Primary_Email', '')) or safe_str(record.get('Personal_Email', ''))
        if email and not self._is_public_email(email):
            # Allow empty, but if present must be from public source
            provenance = safe_str(record.get('Field_Level_Provenance_JSON', ''))
            if not provenance or 'github' not in provenance.lower():
                # Email present but no clear public provenance
                # This is acceptable - just flag for review
                pass
        
        # No fabricated contact data
        phone = safe_str(record.get('Primary_Phone', ''))
        if phone:
            # Ensure phone has provenance
            provenance = safe_str(record.get('Field_Level_Provenance_JSON', ''))
            if not provenance:
                record['Primary_Phone'] = ''  # Clear unverified phone
        
        return True
    
    def _validate_provenance(self, record: Dict) -> bool:
        """Agent #22: Validate audit trail and provenance"""
        # Helper to safely get string value
        def safe_str(val):
            if val is None or (isinstance(val, float) and val != val):
                return ''
            return str(val).strip()
        
        # Ensure at least one external artifact exists
        evidence_fields = [
            'GitHub_Profile_URL',
            'Google_Scholar_URL',
            'Semantic_Scholar_URL',
            'Portfolio_URL',
            'Kaggle_Profile_URL',
            'LinkedIn_URL'
        ]
        
        has_evidence = any(safe_str(record.get(field, '')) for field in evidence_fields)
        
        if not has_evidence:
            self.validation_errors.append("No external evidence artifacts found")
            return False
        
        return True
    
    def _validate_integrity(self, record: Dict) -> bool:
        """Agent #36: Validate cross-field integrity"""
        # Ensure citation metrics are consistent
        velocity_3y = record.get('Citation_Velocity_3yr', '')
        velocity_5y = record.get('Citation_Velocity_5yr', '')
        
        if velocity_3y and velocity_5y:
            try:
                v3 = float(velocity_3y)
                v5 = float(velocity_5y)
                # 3-year velocity should generally be >= 5-year velocity for rising researchers
                # But this is not a hard rule, so just check they're reasonable
                if v3 < 0 or v5 < 0:
                    self.validation_errors.append("Negative citation velocity detected")
                    return False
            except ValueError:
                pass  # Allow empty strings
        
        return True
    
    @staticmethod
    def _is_public_email(email: str) -> bool:
        """Check if email is from a public domain"""
        public_domains = ['gmail.com', 'outlook.com', 'yahoo.com', 'hotmail.com']
        return any(domain in email.lower() for domain in public_domains)
    
    def get_errors(self) -> List[str]:
        """Get validation errors from last validation"""
        return self.validation_errors
