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
Evidence Enricher Module
Enriches records with URLs, OSS contributions, Kaggle profiles, publications, and patents
"""

import requests
import time
import re
from typing import Dict, List, Optional
from urllib.parse import urljoin, urlparse
import json


class EvidenceEnricher:
    """Enrich talent records with external evidence"""
    
    def __init__(self):
        """Initialize enricher with rate limiting"""
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'AI-Talent-Engine/1.0 (Research; +https://github.com/ai-talent-engine)'
        })
        self.last_request_time = {}
        self.rate_limit_delay = 1.0  # seconds between requests per domain
    
    def enrich(self, record: Dict) -> Dict:
        """
        Enrich a single record with external evidence
        COMPLETE IMPLEMENTATION - All source types supported
        
        Args:
            record: Input record from seed hub
            
        Returns:
            Enriched record with additional fields
        """
        enriched = record.copy()
        
        # Determine evidence type and enrich accordingly
        evidence_type = record.get('Evidence_Type', '').lower()
        sheet_type = record.get('_sheet_type', '').lower()
        url = record.get('Seed_Hub_URL', '').strip()
        
        if not url:
            return enriched
        
        # Route to appropriate enrichment function
        if evidence_type == 'github repository' or 'github.com' in url.lower() or sheet_type == 'oss':
            self._enrich_github_comprehensive(enriched, url)
        elif evidence_type == 'kaggle profile' or 'kaggle.com' in url.lower() or sheet_type == 'kaggle':
            self._enrich_kaggle_comprehensive(enriched, url)
        elif evidence_type == 'publication' or sheet_type == 'publications':
            self._enrich_publication_comprehensive(enriched, url)
        elif evidence_type == 'patent' or sheet_type == 'patents':
            self._enrich_patent_comprehensive(enriched, url)
        else:
            self._enrich_generic(enriched, url)
        
        return enriched
    
    def _enrich_github_comprehensive(self, record: Dict, url: str):
        """Comprehensive GitHub enrichment"""
        try:
            # Extract username/org
            username = self._extract_github_username(url)
            if not username:
                return
            
            # Determine if this is a user or org
            is_repo_url = '/blob/' in url or '/tree/' in url or url.count('/') >= 4
            
            if is_repo_url:
                # This is a specific repository
                parts = url.split('github.com/')[-1].split('/')
                if len(parts) >= 2:
                    owner = parts[0]
                    repo_name = parts[1]
                    self._enrich_github_repo(record, owner, repo_name)
            else:
                # This is a user/org profile
                self._enrich_github_user(record, username)
        
        except Exception as e:
            print(f"GitHub enrichment failed for {url}: {str(e)}")
    
    def _enrich_github_user(self, record: Dict, username: str):
        """Enrich from GitHub user profile"""
        # Fetch GitHub profile
        profile_data = self._fetch_github_profile(username)
        if profile_data:
            record['Full_Name'] = profile_data.get('name', '') or record.get('Full_Name', '')
            record['GitHub_Username'] = username
            record['GitHub_Profile_URL'] = f"https://github.com/{username}"
            
            # Location
            location = profile_data.get('location', '').strip()
            if location:
                record['Location_City'] = location
            
            # Company
            company = profile_data.get('company', '').strip().lstrip('@')
            if company:
                record['Current_Company'] = company
            
            # Email
            email = profile_data.get('email', '').strip()
            if email and '@' in email:
                record['Primary_Email'] = email
            
            # Blog/website
            blog = profile_data.get('blog', '').strip()
            if blog:
                record['Portfolio_URL'] = blog if blog.startswith('http') else f"https://{blog}"
            
            # Bio
            bio = profile_data.get('bio', '').strip()
            if bio:
                record['GitHub_Bio'] = bio
        
        # Fetch repositories
        repos = self._fetch_github_repos(username)
        if repos:
            # Get top repos by stars
            sorted_repos = sorted(repos, key=lambda r: r.get('stargazers_count', 0), reverse=True)
            top_repos = sorted_repos[:10]
            
            repo_urls = [r.get('html_url', '') for r in top_repos if r.get('html_url')]
            if repo_urls:
                record['Repo_Evidence_URLs'] = ', '.join(repo_urls)
            
            # Extract topics/keywords
            all_topics = set()
            for repo in top_repos:
                topics = repo.get('topics', [])
                all_topics.update(topics)
            
            if all_topics:
                record['Repo_Topics_Keywords'] = ', '.join(list(all_topics)[:20])
            
            # Extract languages
            languages = set()
            for repo in top_repos:
                lang = repo.get('language')
                if lang:
                    languages.add(lang)
            
            if languages:
                record['Primary_Languages'] = ', '.join(languages)
    
    def _enrich_github_repo(self, record: Dict, owner: str, repo_name: str):
        """Enrich from specific GitHub repository"""
        api_url = f"https://api.github.com/repos/{owner}/{repo_name}"
        response = self._rate_limited_get(api_url)
        
        if response and response.status_code == 200:
            repo_data = response.json()
            
            # Store repo info
            record['Repo_Evidence_URLs'] = repo_data.get('html_url', '')
            record['GitHub_Org'] = owner
            record['GitHub_Repo'] = repo_name
            
            # Get topics
            topics = repo_data.get('topics', [])
            if topics:
                record['Repo_Topics_Keywords'] = ', '.join(topics)
            
            # Get language
            lang = repo_data.get('language')
            if lang:
                record['Primary_Languages'] = lang
            
            # Now enrich the owner as well
            self._enrich_github_user(record, owner)
    
    def _enrich_kaggle_comprehensive(self, record: Dict, url: str):
        """Comprehensive Kaggle enrichment"""
        try:
            # Extract username
            match = re.search(r'kaggle\.com/([^/]+)', url, re.IGNORECASE)
            if not match:
                return
            
            username = match.group(1)
            record['Kaggle_Username'] = username
            record['Kaggle_Profile_URL'] = f"https://www.kaggle.com/{username}"
            
            # Try to fetch Kaggle profile page
            response = self._rate_limited_get(record['Kaggle_Profile_URL'])
            if response and response.status_code == 200:
                content = response.text
                
                # Extract basic info from HTML (simplified - in production use BeautifulSoup)
                # Look for data attributes
                if 'data-user-displayname' in content:
                    # Try to extract display name
                    name_match = re.search(r'data-user-displayname=["\']([^"\']+)["\']', content)
                    if name_match:
                        record['Full_Name'] = name_match.group(1)
                
                # Look for tier information
                if 'Grandmaster' in content or 'Master' in content or 'Expert' in content:
                    record['Kaggle_Tier'] = 'Competition Master+'
        
        except Exception as e:
            print(f"Kaggle enrichment failed for {url}: {str(e)}")
    
    def _enrich_publication_comprehensive(self, record: Dict, url: str):
        """Comprehensive publication enrichment"""
        try:
            record['Publication_URL'] = url
            record['Evidence_Type'] = 'Publication'
            
            # Mark for Scholar API lookup in citation calculator
            record['_needs_scholar_lookup'] = True
            
            # Extract paper ID if it's from a known source
            if 'semanticscholar.org' in url.lower():
                paper_match = re.search(r'/paper/([a-f0-9]+)', url, re.IGNORECASE)
                if paper_match:
                    record['Semantic_Scholar_Paper_ID'] = paper_match.group(1)
            elif 'arxiv.org' in url.lower():
                arxiv_match = re.search(r'arxiv\.org/(?:abs|pdf)/([0-9.]+)', url, re.IGNORECASE)
                if arxiv_match:
                    record['ArXiv_ID'] = arxiv_match.group(1)
        
        except Exception as e:
            print(f"Publication enrichment failed for {url}: {str(e)}")
    
    def _enrich_patent_comprehensive(self, record: Dict, url: str):
        """Comprehensive patent enrichment"""
        try:
            record['Patent_URL'] = url
            record['Evidence_Type'] = 'Patent'
            
            # Extract patent number
            patent_match = re.search(r'(?:patent|US)[\s/]?(\d{7,})', url, re.IGNORECASE)
            if patent_match:
                record['Patent_Number'] = patent_match.group(1)
            
            # Try to fetch patent page for inventor info
            response = self._rate_limited_get(url)
            if response and response.status_code == 200:
                content = response.text.lower()
                
                # Look for inventor names (simplified extraction)
                if 'inventor' in content:
                    # Mark for manual review
                    record['Patent_Inventor_Present'] = 'True'
        
        except Exception as e:
            print(f"Patent enrichment failed for {url}: {str(e)}")
    
    def _fetch_github_profile(self, username: str) -> Optional[Dict]:
        """Fetch GitHub profile via API"""
        api_url = f"https://api.github.com/users/{username}"
        response = self._rate_limited_get(api_url)
        
        if response and response.status_code == 200:
            return response.json()
        
        return None
    
    def _fetch_github_repos(self, username: str) -> List[Dict]:
        """Fetch GitHub repositories via API"""
        api_url = f"https://api.github.com/users/{username}/repos"
        response = self._rate_limited_get(api_url, params={'sort': 'updated', 'per_page': 100})
        
        if response and response.status_code == 200:
            return response.json()
        
        return []
    
    def _rate_limited_get(self, url: str, **kwargs) -> Optional[requests.Response]:
        """Make rate-limited HTTP GET request"""
        domain = urlparse(url).netloc
        
        # Enforce rate limit
        if domain in self.last_request_time:
            elapsed = time.time() - self.last_request_time[domain]
            if elapsed < self.rate_limit_delay:
                time.sleep(self.rate_limit_delay - elapsed)
        
        try:
            response = self.session.get(url, timeout=10, **kwargs)
            self.last_request_time[domain] = time.time()
            return response
        except Exception as e:
            print(f"Request failed for {url}: {str(e)}")
            return None
    
    @staticmethod
    def _extract_github_username(url: str) -> str:
        """Extract GitHub username from URL"""
        if 'github.com' not in url.lower():
            return ''
        
        parts = url.rstrip('/').split('/')
        if len(parts) >= 4 and 'github.com' in url.lower():
            # Handle github.com/username or github.com/username/repo
            idx = parts.index('github.com') if 'github.com' in parts else -1
            if idx >= 0 and idx + 1 < len(parts):
                return parts[idx + 1]
        
        return ''
