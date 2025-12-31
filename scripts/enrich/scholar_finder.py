#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI Talent Engine – Research-First Sourcer Automation
Module: Scholar Finder (Google / Semantic Scholar)
Version: v1.0.0-day2-artifacts
Date: 2025-12-30
Author: Dave Mendoza
© 2025 L. David Mendoza. All Rights Reserved.

Purpose
- Discover public research author profiles
- No citation math yet
- No ranking or frontier logic

Input
- person name
- known affiliations (optional)

Output
- author profile URLs only
"""

from __future__ import annotations

import urllib.parse
from typing import Dict, List


def scholar_search_urls(name: str) -> List[Dict]:
    encoded = urllib.parse.quote_plus(name)

    return [
        {
            "artifact_type": "google_scholar_profile",
            "url": f"https://scholar.google.com/scholar?q={encoded}",
            "source": "name_query",
            "confidence": "inferred"
        },
        {
            "artifact_type": "semantic_scholar_search",
            "url": f"https://www.semanticscholar.org/search?q={encoded}",
            "source": "name_query",
            "confidence": "inferred"
        }
    ]
