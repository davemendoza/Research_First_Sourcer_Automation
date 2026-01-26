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
Contact Scraper Module
Actively scrapes and extracts public contact information
"""

import re
import requests
from typing import Dict, Optional, Tuple
from urllib.parse import urljoin
import time


class ContactScraper:
    """Scrape public contact information from various sources"""
    
    EMAIL_PATTERN = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')
    PHONE_PATTERN = re.compile(r'(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}')
    
    def __init__(self):
        """Initialize scraper with session"""
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'AI-Talent-Engine/1.0 (Research Contact Scraper)'
        })
    
    def scrape(self, record: Dict):
        """
        Scrape contact information and update record in-place
        AGGRESSIVE BUT COMPLIANT - All public sources attempted
        
        Args:
            record: Talent record to enrich with contact info
        """
        # Try all available sources in priority order
        
        # 1. GitHub profile (may already have email from API)
        github_url = record.get('GitHub_Profile_URL', '')
        if github_url:
            self._scrape_github_profile_page(record, github_url)
        
        # 2. Portfolio/Personal website
        portfolio_url = record.get('Portfolio_URL', '')
        if portfolio_url:
            self._scrape_personal_site(record, portfolio_url)
        
        # 3. GitHub.io site (construct from username)
        github_io_url = self._construct_github_io_url(record)
        if github_io_url and not record.get('Primary_Email'):
            self._scrape_personal_site(record, github_io_url)
        
        # 4. Blog URLs
        blog_urls = record.get('Blog_URLs', '') or record.get('Blog_Post_URLs', '')
        if blog_urls and not record.get('Primary_Email'):
            for blog_url in blog_urls.split(','):
                blog_url = blog_url.strip()
                if blog_url:
                    self._scrape_personal_site(record, blog_url)
                    if record.get('Primary_Email'):  # Stop if found
                        break
        
        # 5. CV/Resume URL
        cv_url = record.get('CV_URL', '') or record.get('Resume_URL', '')
        if cv_url:
            self._scrape_cv(record, cv_url)
        
        # 6. Kaggle profile
        kaggle_url = record.get('Kaggle_Profile_URL', '')
        if kaggle_url and not record.get('Primary_Email'):
            self._scrape_kaggle_profile(record, kaggle_url)
        
        # 7. LinkedIn (if present - limited scraping)
        linkedin_url = record.get('LinkedIn_URL', '')
        if linkedin_url and not record.get('Location_City'):
            self._scrape_linkedin_minimal(record, linkedin_url)
        
        # 8. Scholar profile pages
        scholar_url = record.get('Google_Scholar_URL', '') or record.get('Semantic_Scholar_URL', '')
        if scholar_url and not record.get('Primary_Email'):
            self._scrape_scholar_profile(record, scholar_url)
        
        # 9. Parse and normalize location if available
        self._parse_location(record)
        
        # 10. Validate and clean contact data
        self._validate_contact_data(record)
    
    def _scrape_github_profile_page(self, record: Dict, url: str):
        """Scrape GitHub profile page for additional contact info"""
        try:
            response = self._safe_get(url)
            if not response or response.status_code != 200:
                return
            
            content = response.text
            
            # Extract emails from page content
            if not record.get('Primary_Email'):
                emails = self.EMAIL_PATTERN.findall(content)
                valid_emails = [e for e in emails if not self._is_invalid_email(e)]
                if valid_emails:
                    record['Primary_Email'] = valid_emails[0]
            
            # Extract location from profile
            if not record.get('Location_City'):
                # Look for location in profile
                location_match = re.search(r'<span[^>]*itemprop="homeLocation"[^>]*>([^<]+)</span>', content, re.IGNORECASE)
                if location_match:
                    record['Location_City'] = location_match.group(1).strip()
        
        except Exception as e:
            print(f"GitHub profile page scraping failed: {str(e)}")
    
    def _scrape_linkedin_minimal(self, record: Dict, url: str):
        """Minimal LinkedIn scraping (location only, respects ToS)"""
        try:
            # LinkedIn blocks most scrapers, so this is minimal
            # Only attempt if user has a public profile link
            if not url.startswith('http'):
                url = f"https://www.linkedin.com/in/{url}"
            
            response = self._safe_get(url)
            if response and response.status_code == 200:
                content = response.text
                
                # Look for location in meta tags only (public info)
                location_match = re.search(r'<meta[^>]*property="og:locality"[^>]*content="([^"]+)"', content)
                if location_match and not record.get('Location_City'):
                    record['Location_City'] = location_match.group(1).strip()
        
        except Exception as e:
            # LinkedIn blocking is expected - fail silently
            pass
    
    def _scrape_scholar_profile(self, record: Dict, url: str):
        """Scrape Scholar profile for contact info"""
        try:
            response = self._safe_get(url)
            if not response or response.status_code != 200:
                return
            
            content = response.text
            
            # Extract emails (Scholar profiles sometimes show institutional emails)
            if not record.get('Primary_Email'):
                emails = self.EMAIL_PATTERN.findall(content)
                valid_emails = [e for e in emails if not self._is_invalid_email(e)]
                if valid_emails:
                    # Prefer .edu emails
                    edu_emails = [e for e in valid_emails if '.edu' in e.lower()]
                    if edu_emails:
                        record['Primary_Email'] = edu_emails[0]
                    else:
                        record['Primary_Email'] = valid_emails[0]
            
            # Extract affiliation/location
            if 'semanticscholar' in url.lower():
                # Semantic Scholar structure
                affiliation_match = re.search(r'"affiliation":"([^"]+)"', content)
                if affiliation_match and not record.get('Current_Company'):
                    record['Current_Company'] = affiliation_match.group(1)
        
        except Exception as e:
            print(f"Scholar profile scraping failed: {str(e)}")
    
    def _validate_contact_data(self, record: Dict):
        """Validate and clean contact data"""
        # Clean email
        email = record.get('Primary_Email', '').strip()
        if email:
            # Remove any surrounding quotes or brackets
            email = email.strip('"\'<>[]')
            if '@' not in email or '.' not in email:
                record['Primary_Email'] = ''  # Invalid format
            else:
                record['Primary_Email'] = email.lower()
        
        # Clean phone
        phone = record.get('Primary_Phone', '').strip()
        if phone:
            # Basic phone validation
            digits = re.sub(r'\D', '', phone)
            if len(digits) < 10 or len(digits) > 15:
                record['Primary_Phone'] = ''  # Invalid length
        
        # Ensure location fields are clean
        for field in ['Location_City', 'Location_State', 'Location_Country']:
            val = record.get(field, '').strip()
            if val:
                record[field] = val
    
    def _scrape_github_profile(self, record: Dict, url: str):
        """Scrape GitHub profile for contact info"""
        try:
            # GitHub API may have already populated email in evidence enricher
            # Check profile page for additional contact info
            response = self._safe_get(url)
            if response and response.status_code == 200:
                content = response.text
                
                # Extract emails from page
                emails = self.EMAIL_PATTERN.findall(content)
                if emails and not record.get('Primary_Email'):
                    # Filter out common non-personal emails
                    valid_emails = [e for e in emails if not self._is_invalid_email(e)]
                    if valid_emails:
                        record['Primary_Email'] = valid_emails[0]
        
        except Exception as e:
            print(f"GitHub profile scraping failed: {str(e)}")
    
    def _scrape_personal_site(self, record: Dict, url: str):
        """Scrape personal website for contact info"""
        try:
            response = self._safe_get(url)
            if not response or response.status_code != 200:
                return
            
            content = response.text
            
            # Extract email
            if not record.get('Primary_Email'):
                emails = self.EMAIL_PATTERN.findall(content)
                valid_emails = [e for e in emails if not self._is_invalid_email(e)]
                if valid_emails:
                    record['Primary_Email'] = valid_emails[0]
            
            # Extract phone
            if not record.get('Primary_Phone'):
                phones = self.PHONE_PATTERN.findall(content)
                if phones:
                    record['Primary_Phone'] = phones[0]
        
        except Exception as e:
            print(f"Personal site scraping failed for {url}: {str(e)}")
    
    def _scrape_cv(self, record: Dict, url: str):
        """Scrape CV/resume for contact info"""
        try:
            # For PDF CVs, would need PDF parsing library
            # For now, handle HTML CVs
            if url.lower().endswith('.pdf'):
                # Skip PDF parsing for now
                return
            
            response = self._safe_get(url)
            if not response or response.status_code != 200:
                return
            
            content = response.text
            
            # Extract contact info
            if not record.get('Primary_Email'):
                emails = self.EMAIL_PATTERN.findall(content)
                valid_emails = [e for e in emails if not self._is_invalid_email(e)]
                if valid_emails:
                    record['Primary_Email'] = valid_emails[0]
            
            if not record.get('Primary_Phone'):
                phones = self.PHONE_PATTERN.findall(content)
                if phones:
                    record['Primary_Phone'] = phones[0]
        
        except Exception as e:
            print(f"CV scraping failed: {str(e)}")
    
    def _scrape_kaggle_profile(self, record: Dict, url: str):
        """Scrape Kaggle profile for contact info"""
        try:
            response = self._safe_get(url)
            if not response or response.status_code != 200:
                return
            
            content = response.text
            
            # Kaggle may show email on profile page
            if not record.get('Primary_Email'):
                emails = self.EMAIL_PATTERN.findall(content)
                valid_emails = [e for e in emails if not self._is_invalid_email(e)]
                if valid_emails:
                    record['Primary_Email'] = valid_emails[0]
        
        except Exception as e:
            print(f"Kaggle profile scraping failed: {str(e)}")
    
    def _parse_location(self, record: Dict):
        """Parse location from existing location field"""
        location = record.get('Location_City', '').strip()
        if not location:
            return
        
        # Try to split into city, state, country
        parts = [p.strip() for p in location.split(',')]
        
        if len(parts) >= 1:
            record['Location_City'] = parts[0]
        if len(parts) >= 2:
            record['Location_State'] = parts[1]
        if len(parts) >= 3:
            record['Location_Country'] = parts[2]
    
    def _construct_github_io_url(self, record: Dict) -> Optional[str]:
        """Construct potential github.io URL from username"""
        username = record.get('GitHub_Username', '')
        if username:
            return f"https://{username}.github.io"
        return None
    
    def _safe_get(self, url: str) -> Optional[requests.Response]:
        """Make safe HTTP GET request with timeout and error handling"""
        try:
            response = self.session.get(url, timeout=5)
            time.sleep(0.5)  # Rate limiting
            return response
        except Exception as e:
            print(f"Request failed for {url}: {str(e)}")
            return None
    
    @staticmethod
    def _is_invalid_email(email: str) -> bool:
        """Check if email is likely invalid/spam"""
        invalid_domains = [
            'example.com', 'test.com', 'domain.com', 
            'email.com', 'noreply', 'no-reply'
        ]
        email_lower = email.lower()
        return any(domain in email_lower for domain in invalid_domains)
