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
Seed Hub Parser Module
Parses the AI Talent Engine Seed Hub Excel workbook
COMPLETE IMPLEMENTATION - All worksheets supported
"""

import pandas as pd
from typing import List, Dict, Set, Optional
from pathlib import Path
import re


class SeedHubParser:
    """Parse Seed Hub Excel workbook and extract evidence records"""
    
    # All worksheets that contain seed sources (exclude metadata sheets)
    METADATA_SHEETS = ['MASTER_SEED_HUBS', 'EXECUTION_GATE', 'ReadMe', 'Normalized_List', 'ATTACHMENT_MIRROR', 'ALIASES_ARCHIVE']
    
    # Primary worksheets with most direct talent signals
    PRIMARY_WORKSHEETS = ['OSS_PROJECTS', 'FRONTIER_LABS_ORGS', 'RESEARCH_TEAM_DIRECTORIES']
    
    # Secondary worksheets with additional signals
    SECONDARY_WORKSHEETS = ['PATENTS', 'CONFERENCES_2025_2026', 'RESEARCH_PUBLICATION_SOURCES', 
                           'LLM_FOUNDATION_MODELS', 'KAGGLE_COMPETITIONS']
    
    def __init__(self, seed_hub_path: str):
        """
        Initialize parser
        
        Args:
            seed_hub_path: Path to Seed Hub Excel file
        """
        self.seed_hub_path = Path(seed_hub_path)
        if not self.seed_hub_path.exists():
            raise FileNotFoundError(f"Seed Hub not found: {seed_hub_path}")
        
        self.seen_urls = set()
        self.seen_github_users = set()
        self.seen_org_targets = set()
    
    def parse(self) -> List[Dict]:
        """
        Parse all worksheets and return unified record list
        
        Returns:
            List of seed records with evidence metadata
        """
        records = []
        
        # Load Excel file
        xl_file = pd.ExcelFile(self.seed_hub_path)
        
        # Parse primary worksheets first
        for sheet_name in self.PRIMARY_WORKSHEETS:
            if sheet_name in xl_file.sheet_names:
                sheet_records = self._parse_worksheet(xl_file, sheet_name, is_primary=True)
                records.extend(sheet_records)
        
        # Parse secondary worksheets
        for sheet_name in self.SECONDARY_WORKSHEETS:
            if sheet_name in xl_file.sheet_names:
                sheet_records = self._parse_worksheet(xl_file, sheet_name, is_primary=False)
                records.extend(sheet_records)
        
        # Also parse any other domain sheets not explicitly listed
        for sheet_name in xl_file.sheet_names:
            # Skip metadata and already-parsed sheets
            if sheet_name in self.METADATA_SHEETS:
                continue
            if sheet_name in self.PRIMARY_WORKSHEETS or sheet_name in self.SECONDARY_WORKSHEETS:
                continue
            
            # Parse as secondary worksheet
            sheet_records = self._parse_worksheet(xl_file, sheet_name, is_primary=False)
            records.extend(sheet_records)
        
        return records
    
    def _parse_worksheet(self, xl_file: pd.ExcelFile, sheet_name: str, is_primary: bool) -> List[Dict]:
        """
        Parse a single worksheet with type-specific logic
        
        Args:
            xl_file: Loaded Excel file
            sheet_name: Name of worksheet to parse
            is_primary: Whether this is a primary worksheet
            
        Returns:
            List of records from this worksheet
        """
        try:
            df = xl_file.parse(sheet_name)
        except Exception as e:
            print(f"Warning: Could not parse worksheet '{sheet_name}': {e}")
            return []
        
        if df.empty:
            return []
        
        records = []
        
        # Determine worksheet type and apply specific parsing
        sheet_type = self._get_sheet_type(sheet_name)
        
        for idx, row in df.iterrows():
            # Convert row to dict and clean NaN values
            record = self._clean_record(row.to_dict())
            
            # Add metadata
            record['_source_worksheet'] = sheet_name
            record['_sheet_type'] = sheet_type
            record['_is_primary_source'] = is_primary
            record['_row_index'] = idx
            
            # Check for duplicates
            if self._is_duplicate(record):
                continue
            
            # Apply type-specific enrichment
            if sheet_type == 'kaggle':
                self._enrich_kaggle_record(record)
            elif sheet_type == 'oss':
                self._enrich_oss_record(record)
            elif sheet_type == 'publications':
                self._enrich_publication_record(record)
            elif sheet_type == 'patents':
                self._enrich_patent_record(record)
            elif sheet_type == 'urls':
                self._enrich_url_record(record)
            
            # Track this record
            self._track_record(record)
            
            records.append(record)
        
        return records
    
    def _get_sheet_type(self, sheet_name: str) -> str:
        """Determine worksheet type from name"""
        sheet_lower = sheet_name.lower()
        if 'kaggle' in sheet_lower:
            return 'kaggle'
        elif 'oss' in sheet_lower or 'code' in sheet_lower:
            return 'oss'
        elif 'publication' in sheet_lower:
            return 'publications'
        elif 'patent' in sheet_lower:
            return 'patents'
        elif 'url' in sheet_lower:
            return 'urls'
        return 'generic'
    
    def _clean_record(self, record: Dict) -> Dict:
        """Clean NaN values and normalize strings"""
        cleaned = {}
        for key, val in record.items():
            # Handle NaN
            if pd.isna(val):
                cleaned[key] = ''
            elif isinstance(val, str):
                cleaned[key] = val.strip()
            else:
                cleaned[key] = str(val).strip()
        return cleaned
    
    def _enrich_kaggle_record(self, record: Dict):
        """Add Kaggle-specific metadata"""
        url = record.get('Seed_Hub_URL', '')
        if 'kaggle.com' in url.lower():
            # Extract username from Kaggle URL
            match = re.search(r'kaggle\.com/([^/]+)', url, re.IGNORECASE)
            if match:
                record['Kaggle_Username'] = match.group(1)
                record['Evidence_Type'] = 'Kaggle Profile'
    
    def _enrich_oss_record(self, record: Dict):
        """Add OSS/GitHub-specific metadata"""
        url = record.get('Seed_Hub_URL', '')
        if 'github.com' in url.lower():
            # Extract org and repo from GitHub URL
            match = re.search(r'github\.com/([^/]+)(?:/([^/]+))?', url, re.IGNORECASE)
            if match:
                record['GitHub_Org'] = match.group(1)
                if match.group(2):
                    record['GitHub_Repo'] = match.group(2)
                record['Evidence_Type'] = 'GitHub Repository'
    
    def _enrich_publication_record(self, record: Dict):
        """Add publication-specific metadata"""
        record['Evidence_Type'] = 'Publication'
        # Mark for Scholar API lookup
        record['_needs_scholar_lookup'] = True
    
    def _enrich_patent_record(self, record: Dict):
        """Add patent-specific metadata"""
        record['Evidence_Type'] = 'Patent'
        # Extract patent number if present in URL
        url = record.get('Seed_Hub_URL', '')
        patent_match = re.search(r'(?:patent|US)[\s/]?(\d{7,})', url, re.IGNORECASE)
        if patent_match:
            record['Patent_Number'] = patent_match.group(1)
    
    def _enrich_url_record(self, record: Dict):
        """Add generic URL metadata"""
        record['Evidence_Type'] = 'URL'
        # Try to determine URL type
        url = record.get('Seed_Hub_URL', '').lower()
        if '.edu' in url:
            record['URL_Category'] = 'Academic'
        elif 'linkedin.com' in url:
            record['URL_Category'] = 'LinkedIn'
        elif 'scholar.google' in url:
            record['URL_Category'] = 'Scholar'
        elif 'semanticscholar' in url:
            record['URL_Category'] = 'Semantic Scholar'
    
    def _is_duplicate(self, record: Dict) -> bool:
        """
        Check if record is duplicate using multiple criteria
        
        Args:
            record: Record to check
            
        Returns:
            True if duplicate, False otherwise
        """
        # Check URL (exact and normalized)
        url = record.get('Seed_Hub_URL', '').strip()
        if url:
            if url in self.seen_urls:
                return True
            
            # Normalized URL check (remove trailing slashes, www, etc)
            normalized_url = self._normalize_url(url)
            if normalized_url in self.seen_urls:
                return True
        
        # Check GitHub username
        github_user = self._extract_github_username(url)
        if github_user and github_user in self.seen_github_users:
            return True
        
        # Check organization + target combination
        org = record.get('Primary_Enumeration_Target', '').strip()
        target = record.get('Seed_Hub_Type', '').strip()
        org_target = f"{org}|{target}"
        if org_target and org_target != '|' and org_target in self.seen_org_targets:
            return True
        
        return False
    
    def _track_record(self, record: Dict):
        """Track record to prevent future duplicates"""
        url = record.get('Seed_Hub_URL', '').strip()
        if url:
            self.seen_urls.add(url)
            self.seen_urls.add(self._normalize_url(url))
        
        github_user = self._extract_github_username(url)
        if github_user:
            self.seen_github_users.add(github_user)
        
        org = record.get('Primary_Enumeration_Target', '').strip()
        target = record.get('Seed_Hub_Type', '').strip()
        if org and target:
            self.seen_org_targets.add(f"{org}|{target}")
    
    @staticmethod
    def _normalize_url(url: str) -> str:
        """Normalize URL for comparison"""
        url = url.lower().strip()
        url = url.rstrip('/')
        url = url.replace('www.', '')
        url = url.replace('http://', '').replace('https://', '')
        return url
    
    @staticmethod
    def _extract_github_username(url: str) -> str:
        """Extract GitHub username from URL"""
        if 'github.com' not in url.lower():
            return ''
        
        parts = url.rstrip('/').split('/')
        if len(parts) >= 4 and 'github.com' in parts[-2].lower():
            return parts[-1]
        elif len(parts) >= 3:
            return parts[-1]
        
        return ''
