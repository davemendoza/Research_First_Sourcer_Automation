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
Seed Enumerator Module
Enumerates individuals from seed sources (GitHub repos, conferences, labs, patents)
CRITICAL MISSING LAYER - Converts seed sources to individual talent records
"""

import requests
import time
import re
from typing import List, Dict, Set, Optional
from urllib.parse import urlparse
import json


class SeedEnumerator:
    """
    Enumerate individuals from seed sources
    Deterministic, bounded, no social graph expansion
    """
    
    def __init__(self):
        """Initialize enumerator with rate limiting"""
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'AI-Talent-Engine/1.0 (Seed Enumeration; Research)'
        })
        self.last_request_time = {}
        self.rate_limit_delay = 1.0
        self.enumeration_stats = {}
        self.seen_identities = set()  # Deduplication
    
    def enumerate_from_seed(self, seed_record: Dict) -> List[Dict]:
        """
        Enumerate individuals from a single seed source
        
        Args:
            seed_record: Seed source record from Seed Hub
            
        Returns:
            List of individual talent records
        """
        seed_type = seed_record.get('Seed_Hub_Type', '').lower()
        seed_class = seed_record.get('Seed_Hub_Class', '').lower()
        url = seed_record.get('Seed_Hub_URL', '').strip()
        org = seed_record.get('Organization', '')
        target = seed_record.get('Primary_Enumeration_Target', '').lower()
        
        individuals = []
        
        # Route to appropriate enumeration method
        if 'github' in seed_type or 'github' in seed_class or 'github.com' in url:
            if 'repo' in target or 'contributor' in target:
                individuals = self._enumerate_github_repo_contributors(url, seed_record)
            elif 'org' in target or 'member' in target:
                individuals = self._enumerate_github_org_members(url, seed_record)
            else:
                # Default to contributors for repos
                individuals = self._enumerate_github_repo_contributors(url, seed_record)
        
        elif 'kaggle' in seed_type or 'kaggle.com' in url:
            individuals = self._enumerate_kaggle_competition(url, seed_record)
        
        elif 'conference' in seed_type or 'conference' in seed_class:
            individuals = self._enumerate_conference_speakers(url, seed_record)
        
        elif 'lab' in seed_type or 'research' in seed_type:
            individuals = self._enumerate_lab_members(url, seed_record)
        
        elif 'patent' in seed_type:
            individuals = self._enumerate_patent_inventors(url, seed_record)
        
        else:
            # Generic URL - attempt intelligent parsing
            individuals = self._enumerate_generic_url(url, seed_record)
        
        # Track enumeration stats
        source_key = f"{org}|{url[:50]}"
        self.enumeration_stats[source_key] = len(individuals)
        
        # Deduplicate
        deduplicated = self._deduplicate_individuals(individuals)
        
        return deduplicated
    
    def _enumerate_github_repo_contributors(self, url: str, seed_record: Dict) -> List[Dict]:
        """Enumerate contributors from a GitHub repository"""
        individuals = []
        
        try:
            # Extract owner and repo from URL
            match = re.search(r'github\.com/([^/]+)/([^/\?#]+)', url, re.IGNORECASE)
            if not match:
                return []
            
            owner = match.group(1)
            repo = match.group(2)
            
            # GitHub API endpoint for contributors
            api_url = f"https://api.github.com/repos/{owner}/{repo}/contributors"
            
            # Fetch contributors (paginated)
            page = 1
            max_pages = 5  # Limit to top 500 contributors (100 per page)
            
            while page <= max_pages:
                self._rate_limit('github.com')
                params = {'per_page': 100, 'page': page, 'anon': 'false'}
                response = self.session.get(api_url, params=params, timeout=10)
                
                if response.status_code != 200:
                    break
                
                contributors = response.json()
                if not contributors:
                    break
                
                # Convert each contributor to individual record
                for contributor in contributors:
                    individual = self._create_individual_from_github_user(
                        contributor, seed_record, source_type='github_contributor'
                    )
                    individuals.append(individual)
                
                # Check if there are more pages
                if len(contributors) < 100:
                    break
                
                page += 1
        
        except Exception as e:
            print(f"GitHub contributor enumeration failed for {url}: {str(e)}")
        
        return individuals
    
    def _enumerate_github_org_members(self, url: str, seed_record: Dict) -> List[Dict]:
        """Enumerate members from a GitHub organization"""
        individuals = []
        
        try:
            # Extract org from URL
            match = re.search(r'github\.com/([^/\?#]+)', url, re.IGNORECASE)
            if not match:
                return []
            
            org = match.group(1)
            
            # GitHub API endpoint for org members
            api_url = f"https://api.github.com/orgs/{org}/members"
            
            # Fetch members (paginated)
            page = 1
            max_pages = 3  # Limit to 300 members
            
            while page <= max_pages:
                self._rate_limit('github.com')
                params = {'per_page': 100, 'page': page}
                response = self.session.get(api_url, params=params, timeout=10)
                
                if response.status_code != 200:
                    break
                
                members = response.json()
                if not members:
                    break
                
                # Convert each member to individual record
                for member in members:
                    individual = self._create_individual_from_github_user(
                        member, seed_record, source_type='github_org_member'
                    )
                    individuals.append(individual)
                
                if len(members) < 100:
                    break
                
                page += 1
        
        except Exception as e:
            print(f"GitHub org enumeration failed for {url}: {str(e)}")
        
        return individuals
    
    def _create_individual_from_github_user(self, user_data: Dict, seed_record: Dict, 
                                           source_type: str) -> Dict:
        """Create individual record from GitHub user data"""
        username = user_data.get('login', '')
        
        individual = {
            'Full_Name': '',  # Will be enriched later
            'GitHub_Username': username,
            'GitHub_Profile_URL': user_data.get('html_url', f"https://github.com/{username}"),
            'Seed_Source_Type': source_type,
            'Seed_Source_URL': seed_record.get('Seed_Hub_URL', ''),
            'Seed_Source_Label': seed_record.get('Organization', ''),
            'Seed_Query_Or_Handle': username,
            '_seed_organization': seed_record.get('Organization', ''),
            '_seed_category': seed_record.get('Category', ''),
            '_seed_tier': seed_record.get('Tier', ''),
        }
        
        return individual
    
    def _enumerate_kaggle_competition(self, url: str, seed_record: Dict) -> List[Dict]:
        """Enumerate participants from Kaggle competition"""
        individuals = []
        
        try:
            # Kaggle API requires authentication - skip for now
            # In production, use Kaggle API with credentials
            # For now, mark as needs enumeration
            pass
        
        except Exception as e:
            print(f"Kaggle enumeration failed for {url}: {str(e)}")
        
        return individuals
    
    def _enumerate_conference_speakers(self, url: str, seed_record: Dict) -> List[Dict]:
        """Enumerate speakers from conference"""
        individuals = []
        
        try:
            # Conference enumeration requires scraping specific conference pages
            # This is highly variable by conference format
            # Skip for now - requires conference-specific parsers
            pass
        
        except Exception as e:
            print(f"Conference enumeration failed for {url}: {str(e)}")
        
        return individuals
    
    def _enumerate_lab_members(self, url: str, seed_record: Dict) -> List[Dict]:
        """Enumerate members from research lab/team page"""
        individuals = []
        
        try:
            # Lab pages are highly variable in structure
            # Requires scraping and parsing HTML
            # Skip for now - needs custom parsers per lab
            pass
        
        except Exception as e:
            print(f"Lab enumeration failed for {url}: {str(e)}")
        
        return individuals
    
    def _enumerate_patent_inventors(self, url: str, seed_record: Dict) -> List[Dict]:
        """Enumerate inventors from patent"""
        individuals = []
        
        try:
            # Patent enumeration requires parsing patent office pages
            # Skip for now - needs patent-specific parsers
            pass
        
        except Exception as e:
            print(f"Patent enumeration failed for {url}: {str(e)}")
        
        return individuals
    
    def _enumerate_generic_url(self, url: str, seed_record: Dict) -> List[Dict]:
        """Attempt intelligent enumeration from generic URL"""
        individuals = []
        
        # Check if URL is actually a GitHub URL that wasn't caught
        if 'github.com' in url.lower():
            return self._enumerate_github_repo_contributors(url, seed_record)
        
        # Otherwise skip
        return individuals
    
    def _deduplicate_individuals(self, individuals: List[Dict]) -> List[Dict]:
        """Deduplicate individuals by identity"""
        deduplicated = []
        
        for individual in individuals:
            # Create identity key
            github_user = individual.get('GitHub_Username', '').lower().strip()
            email = individual.get('Primary_Email', '').lower().strip()
            name = individual.get('Full_Name', '').lower().strip()
            
            # Identity key (prefer GitHub username > email > name)
            if github_user:
                identity_key = f"github:{github_user}"
            elif email:
                identity_key = f"email:{email}"
            elif name:
                identity_key = f"name:{name}"
            else:
                # No clear identity - skip
                continue
            
            # Check if already seen
            if identity_key in self.seen_identities:
                continue
            
            # Mark as seen
            self.seen_identities.add(identity_key)
            deduplicated.append(individual)
        
        return deduplicated
    
    def _rate_limit(self, domain: str):
        """Enforce rate limiting per domain"""
        if domain in self.last_request_time:
            elapsed = time.time() - self.last_request_time[domain]
            if elapsed < self.rate_limit_delay:
                time.sleep(self.rate_limit_delay - elapsed)
        
        self.last_request_time[domain] = time.time()
    
    def get_enumeration_stats(self) -> Dict[str, int]:
        """Get enumeration statistics"""
        return self.enumeration_stats.copy()
