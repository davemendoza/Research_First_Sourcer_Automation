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
Talent Intelligence Preview Module
Generates HTML preview of talent pipeline results
"""

from typing import List, Dict
from datetime import datetime


class TalentPreview:
    """Generate HTML preview of talent intelligence results"""
    
    def __init__(self):
        """Initialize preview generator"""
        pass
    
    def generate(self, data: List[Dict], mode: str, enumeration_failed: bool = False) -> str:
        """
        Generate HTML preview from real run data
        
        Args:
            data: Processed talent records
            mode: Execution mode
            
        Returns:
            HTML string
        """
        timestamp = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')
        
        html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI Talent Engine - Intelligence Preview</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 40px 20px;
            color: #333;
        }}
        
        .container {{
            max-width: 1400px;
            margin: 0 auto;
        }}
        
        .header {{
            background: white;
            padding: 30px;
            border-radius: 12px;
            box-shadow: 0 10px 40px rgba(0, 0, 0, 0.1);
            margin-bottom: 30px;
        }}
        
        .header h1 {{
            color: #667eea;
            font-size: 32px;
            margin-bottom: 10px;
        }}
        
        .header .meta {{
            color: #666;
            font-size: 14px;
        }}
        
        .stats {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        
        .stat-card {{
            background: white;
            padding: 25px;
            border-radius: 12px;
            box-shadow: 0 5px 20px rgba(0, 0, 0, 0.1);
        }}
        
        .stat-card .label {{
            color: #666;
            font-size: 14px;
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-bottom: 10px;
        }}
        
        .stat-card .value {{
            color: #667eea;
            font-size: 36px;
            font-weight: bold;
        }}
        
        .talent-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(400px, 1fr));
            gap: 25px;
        }}
        
        .talent-card {{
            background: white;
            border-radius: 12px;
            overflow: hidden;
            box-shadow: 0 5px 20px rgba(0, 0, 0, 0.1);
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }}
        
        .talent-card:hover {{
            transform: translateY(-5px);
            box-shadow: 0 10px 40px rgba(0, 0, 0, 0.15);
        }}
        
        .card-header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
        }}
        
        .card-header h3 {{
            font-size: 20px;
            margin-bottom: 5px;
        }}
        
        .card-header .role {{
            font-size: 14px;
            opacity: 0.9;
        }}
        
        .card-body {{
            padding: 20px;
        }}
        
        .field {{
            margin-bottom: 15px;
        }}
        
        .field-label {{
            color: #666;
            font-size: 12px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-bottom: 5px;
        }}
        
        .field-value {{
            color: #333;
            font-size: 14px;
        }}
        
        .field-value a {{
            color: #667eea;
            text-decoration: none;
        }}
        
        .field-value a:hover {{
            text-decoration: underline;
        }}
        
        .tags {{
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
            margin-top: 15px;
        }}
        
        .tag {{
            background: #f0f0f0;
            color: #666;
            padding: 5px 12px;
            border-radius: 20px;
            font-size: 12px;
        }}
        
        .tag.highlight {{
            background: #667eea;
            color: white;
        }}
        
        .footer {{
            text-align: center;
            color: white;
            margin-top: 40px;
            padding: 20px;
            font-size: 14px;
        }}
        
        .failure-banner {{
            background: #dc3545;
            color: white;
            padding: 30px;
            border-radius: 12px;
            margin-bottom: 30px;
            box-shadow: 0 10px 40px rgba(220, 53, 69, 0.3);
            border: 3px solid #c82333;
            text-align: center;
        }}
        
        .failure-banner h2 {{
            font-size: 24px;
            margin-bottom: 15px;
        }}
    </style>
</head>
<body>
    <div class="container">
"""
        
        # Add failure banner if enumeration failed
        if enumeration_failed:
            html += """
        <div class="failure-banner">
            <h2>❌ ENUMERATION BLOCKED — NO INDIVIDUALS GENERATED</h2>
            <p><strong>Run Status: FAILED</strong></p>
            <p>Network blocking prevented enumeration. Deploy in environment with API access.</p>
        </div>
"""
        
        html += f"""
        <div class="header">
            <h1>🧠 AI Talent Engine — Intelligence Preview</h1>
            <p class="meta">
                <strong>Mode:</strong> {mode.upper()} | 
                <strong>Generated:</strong> {timestamp} | 
                <strong>Schema:</strong> v3.3 Extended | 
                <strong>Records:</strong> {len(data)}
            </p>
        </div>
        
        <div class="stats">
            <div class="stat-card">
                <div class="label">Total Candidates</div>
                <div class="value">{len(data)}</div>
            </div>
            <div class="stat-card">
                <div class="label">With Contact Info</div>
                <div class="value">{self._count_with_contact(data)}</div>
            </div>
            <div class="stat-card">
                <div class="label">GitHub Profiles</div>
                <div class="value">{self._count_github_profiles(data)}</div>
            </div>
            <div class="stat-card">
                <div class="label">Scholar Profiles</div>
                <div class="value">{self._count_scholar_profiles(data)}</div>
            </div>
        </div>
        
        <div class="talent-grid">
"""
        
        # Add talent cards
        for record in data[:50]:  # Limit to 50 for preview
            html += self._generate_card(record)
        
        html += """
        </div>
        
        <div class="footer">
            <p>© 2025-2026 L. David Mendoza. All Rights Reserved.</p>
            <p>AI Talent Engine — Signal Intelligence | Proprietary and Confidential</p>
        </div>
    </div>
</body>
</html>
"""
        
        return html
    
    def _generate_card(self, record: Dict) -> str:
        """Generate HTML card for single talent record"""
        # Helper to safely get string value
        def safe_str(val):
            if val is None or (isinstance(val, float) and val != val):
                return ''
            return str(val)
        
        name = safe_str(record.get('Full_Name', 'Unknown'))
        role = safe_str(record.get('AI_Role_Type', record.get('AI_Classification', 'Not Classified')))
        company = safe_str(record.get('Current_Company', record.get('Company', '')))
        email = safe_str(record.get('Primary_Email', record.get('Personal_Email', '')))
        github = safe_str(record.get('GitHub_Profile_URL', record.get('GitHub_URL', '')))
        scholar = safe_str(record.get('Google_Scholar_URL', ''))
        location = self._format_location(record)
        
        # Extract skills
        skills = safe_str(record.get('Primary_Specialties', record.get('Determinative_Skill_Areas', '')))
        skill_list = [s.strip() for s in skills.split(',')[:5]] if skills else []
        
        card = f"""
            <div class="talent-card">
                <div class="card-header">
                    <h3>{name}</h3>
                    <p class="role">{role}</p>
                </div>
                <div class="card-body">
"""
        
        if company:
            card += f"""
                    <div class="field">
                        <div class="field-label">Company</div>
                        <div class="field-value">{company}</div>
                    </div>
"""
        
        if location:
            card += f"""
                    <div class="field">
                        <div class="field-label">Location</div>
                        <div class="field-value">{location}</div>
                    </div>
"""
        
        if email:
            card += f"""
                    <div class="field">
                        <div class="field-label">Email</div>
                        <div class="field-value"><a href="mailto:{email}">{email}</a></div>
                    </div>
"""
        
        if github:
            card += f"""
                    <div class="field">
                        <div class="field-label">GitHub</div>
                        <div class="field-value"><a href="{github}" target="_blank">{github}</a></div>
                    </div>
"""
        
        if scholar:
            card += f"""
                    <div class="field">
                        <div class="field-label">Google Scholar</div>
                        <div class="field-value"><a href="{scholar}" target="_blank">View Profile</a></div>
                    </div>
"""
        
        if skill_list:
            card += """
                    <div class="tags">
"""
            for skill in skill_list:
                card += f'<span class="tag">{skill}</span>\n'
            
            card += """
                    </div>
"""
        
        card += """
                </div>
            </div>
"""
        
        return card
    
    def _count_with_contact(self, data: List[Dict]) -> int:
        """Count records with contact information"""
        count = 0
        for record in data:
            if record.get('Primary_Email') or record.get('Personal_Email') or record.get('Primary_Phone'):
                count += 1
        return count
    
    def _count_github_profiles(self, data: List[Dict]) -> int:
        """Count records with GitHub profiles"""
        count = 0
        for record in data:
            if record.get('GitHub_Profile_URL') or record.get('GitHub_URL'):
                count += 1
        return count
    
    def _count_scholar_profiles(self, data: List[Dict]) -> int:
        """Count records with Scholar profiles"""
        count = 0
        for record in data:
            if record.get('Google_Scholar_URL') or record.get('Semantic_Scholar_URL'):
                count += 1
        return count
    
    def _format_location(self, record: Dict) -> str:
        """Format location from record fields"""
        # Helper to safely get string value
        def safe_str(val):
            if val is None or (isinstance(val, float) and val != val):
                return ''
            return str(val).strip()
        
        parts = []
        
        city = safe_str(record.get('Location_City', ''))
        state = safe_str(record.get('Location_State', ''))
        country = safe_str(record.get('Location_Country', ''))
        
        if city:
            parts.append(city)
        if state:
            parts.append(state)
        if country:
            parts.append(country)
        
        return ', '.join(parts) if parts else ''
