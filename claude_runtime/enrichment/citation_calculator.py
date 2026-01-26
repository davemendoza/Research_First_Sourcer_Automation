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
Citation Calculator Module
Fetches citation data and calculates velocity metrics
"""

import requests
import time
import re
from typing import Dict, Optional, List
from datetime import datetime
import json


class CitationCalculator:
    """Calculate citation velocities from public scholarly APIs"""
    
    CURRENT_YEAR = datetime.utcnow().year
    
    def __init__(self):
        """Initialize calculator with API sessions"""
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'AI-Talent-Engine/1.0 (Research; Citation Analysis)'
        })
        self.last_request = {}
    
    def calculate(self, record: Dict):
        """
        Calculate citation metrics and update record in-place
        COMPLETE IMPLEMENTATION - Fetches from Scholar APIs
        
        Args:
            record: Talent record to enrich with citation data
        """
        # Determine author identity
        author_name = record.get('Full_Name', '').strip()
        scholar_url = record.get('Google_Scholar_URL', '').strip()
        semantic_url = record.get('Semantic_Scholar_URL', '').strip()
        
        if not author_name and not scholar_url and not semantic_url:
            # No way to look up citations
            self._set_empty_citations(record)
            return
        
        # Try multiple sources in order of preference
        citation_data = None
        
        # 1. Try Semantic Scholar (best API)
        if semantic_url:
            author_id = self._extract_semantic_scholar_id(semantic_url)
            if author_id:
                citation_data = self._fetch_semantic_scholar_by_id(author_id)
        
        # 2. Try Semantic Scholar search by name
        if not citation_data and author_name:
            citation_data = self._fetch_semantic_scholar_by_name(author_name)
        
        # 3. Try OpenAlex
        if not citation_data and author_name:
            citation_data = self._fetch_openalex(author_name)
        
        # 4. Google Scholar (if URL provided - scraping required)
        # Skipped for now as it requires scraping and is rate-limited
        
        # Calculate velocities from citation data
        if citation_data:
            self._calculate_velocities(record, citation_data)
        else:
            self._set_empty_citations(record)
            record['Citation_Provenance'] = 'No citation data available from Scholar APIs'
    
    def _extract_semantic_scholar_id(self, url: str) -> Optional[str]:
        """Extract author ID from Semantic Scholar URL"""
        match = re.search(r'/author/([^/\?#]+)', url)
        if match:
            return match.group(1)
        return None
    
    def _fetch_semantic_scholar_by_id(self, author_id: str) -> Optional[Dict]:
        """Fetch from Semantic Scholar by author ID"""
        try:
            api_url = f"https://api.semanticscholar.org/graph/v1/author/{author_id}"
            params = {
                'fields': 'papers.citationCount,papers.year,citationCount,hIndex,papers.title'
            }
            
            self._rate_limit('semanticscholar.org')
            response = self.session.get(api_url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                return self._parse_semantic_scholar_response(data)
            elif response.status_code == 429:
                print("Semantic Scholar rate limit hit")
                time.sleep(5)  # Back off
        
        except Exception as e:
            print(f"Semantic Scholar fetch by ID failed: {str(e)}")
        
        return None
    
    def _fetch_semantic_scholar_by_name(self, author_name: str) -> Optional[Dict]:
        """Search Semantic Scholar by author name"""
        try:
            api_url = "https://api.semanticscholar.org/graph/v1/author/search"
            params = {
                'query': author_name,
                'limit': 1,
                'fields': 'papers.citationCount,papers.year,citationCount,hIndex'
            }
            
            self._rate_limit('semanticscholar.org')
            response = self.session.get(api_url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('data') and len(data['data']) > 0:
                    author_data = data['data'][0]
                    
                    # Fetch full author details
                    author_id = author_data.get('authorId')
                    if author_id:
                        return self._fetch_semantic_scholar_by_id(author_id)
            elif response.status_code == 429:
                print("Semantic Scholar rate limit hit")
                time.sleep(5)
        
        except Exception as e:
            print(f"Semantic Scholar search failed: {str(e)}")
        
        return None
    
    def _fetch_semantic_scholar(self, url: str) -> Optional[Dict]:
        """Fetch citation data from Semantic Scholar"""
        try:
            # Extract author ID from URL
            author_id = url.rstrip('/').split('/')[-1]
            
            # Semantic Scholar API endpoint
            api_url = f"https://api.semanticscholar.org/graph/v1/author/{author_id}"
            params = {
                'fields': 'papers.citationCount,papers.year,citationCount,hIndex,papers'
            }
            
            self._rate_limit('semanticscholar.org')
            response = self.session.get(api_url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                return self._parse_semantic_scholar_response(data)
        
        except Exception as e:
            print(f"Semantic Scholar fetch failed: {str(e)}")
        
        return None
    
    def _fetch_google_scholar(self, url: str) -> Optional[Dict]:
        """
        Fetch citation data from Google Scholar
        Note: Google Scholar doesn't have official API, using scraping
        """
        # Google Scholar requires scraping, which is rate-limited
        # For production, use scholarly library or SerpAPI
        # Skipping for now due to complexity
        return None
    
    def _fetch_openalex(self, author_name: str) -> Optional[Dict]:
        """Fetch citation data from OpenAlex"""
        try:
            # OpenAlex API endpoint
            api_url = "https://api.openalex.org/authors"
            params = {
                'search': author_name,
                'per_page': 1
            }
            
            self._rate_limit('openalex.org')
            response = self.session.get(api_url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('results'):
                    author_data = data['results'][0]
                    return self._parse_openalex_response(author_data)
        
        except Exception as e:
            print(f"OpenAlex fetch failed: {str(e)}")
        
        return None
    
    def _parse_semantic_scholar_response(self, data: Dict) -> Dict:
        """Parse Semantic Scholar API response"""
        citations_by_year = {}
        
        papers = data.get('papers', [])
        for paper in papers:
            year = paper.get('year')
            citations = paper.get('citationCount', 0)
            if year and citations:
                citations_by_year[str(year)] = citations_by_year.get(str(year), 0) + citations
        
        return {
            'citations_by_year': citations_by_year,
            'total_citations': data.get('citationCount', 0),
            'h_index': data.get('hIndex', 0),
            'source': 'semantic_scholar'
        }
    
    def _parse_openalex_response(self, data: Dict) -> Dict:
        """Parse OpenAlex API response"""
        # OpenAlex provides works_count and cited_by_count
        cited_by = data.get('cited_by_count', 0)
        
        # Approximate citations by year (OpenAlex has counts_by_year)
        citations_by_year = {}
        counts_by_year = data.get('counts_by_year', [])
        for year_data in counts_by_year:
            year = year_data.get('year')
            count = year_data.get('cited_by_count', 0)
            if year:
                citations_by_year[str(year)] = count
        
        return {
            'citations_by_year': citations_by_year,
            'total_citations': cited_by,
            'h_index': data.get('summary_stats', {}).get('h_index', 0),
            'source': 'openalex'
        }
    
    def _calculate_velocities(self, record: Dict, citation_data: Dict):
        """Calculate citation velocity metrics"""
        citations_by_year = citation_data.get('citations_by_year', {})
        total_citations = citation_data.get('total_citations', 0)
        
        # Store raw citation data
        record['Citation_Count_Raw'] = str(total_citations)
        record['H_Index'] = str(citation_data.get('h_index', 0))
        
        # Store citations by year as JSON
        record['Graph_Evidence_JSON'] = json.dumps({
            'citations_by_year': citations_by_year,
            'source': citation_data.get('source', 'unknown')
        })
        
        # Calculate velocities
        if citations_by_year:
            # 3-year velocity
            recent_3y = sum(
                citations_by_year.get(str(year), 0) 
                for year in range(self.CURRENT_YEAR - 2, self.CURRENT_YEAR + 1)
            )
            velocity_3y = recent_3y / 3.0
            record['Citation_Velocity_3yr'] = f"{velocity_3y:.2f}"
            
            # 5-year velocity
            recent_5y = sum(
                citations_by_year.get(str(year), 0)
                for year in range(self.CURRENT_YEAR - 4, self.CURRENT_YEAR + 1)
            )
            velocity_5y = recent_5y / 5.0
            record['Citation_Velocity_5yr'] = f"{velocity_5y:.2f}"
            
            # Citations per year (career average)
            years = list(citations_by_year.keys())
            if years:
                min_year = min(int(y) for y in years)
                career_span = max(1, self.CURRENT_YEAR - min_year + 1)
                citations_per_year = total_citations / career_span
                record['Citations_per_Year'] = f"{citations_per_year:.2f}"
            else:
                record['Citations_per_Year'] = ''
        else:
            record['Citation_Velocity_3yr'] = ''
            record['Citation_Velocity_5yr'] = ''
            record['Citations_per_Year'] = ''
        
        # Set provenance
        record['Citation_Provenance'] = f"Fetched from {citation_data.get('source', 'unknown')} API"
    
    def _rate_limit(self, domain: str):
        """Enforce rate limiting per domain"""
        if domain in self.last_request:
            elapsed = time.time() - self.last_request[domain]
            if elapsed < 1.0:
                time.sleep(1.0 - elapsed)
        
        self.last_request[domain] = time.time()
    
    def _set_empty_citations(self, record: Dict):
        """Set empty citation fields"""
        record['Citations_per_Year'] = ''
        record['Citation_Velocity_3yr'] = ''
        record['Citation_Velocity_5yr'] = ''
        record['Citation_Count_Raw'] = ''
        record['H_Index'] = ''
