#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI Talent Engine – Research-First Sourcer Automation
Module: Patent Finder
Version: v1.0.0-day2-artifacts
Date: 2025-12-30
Author: Dave Mendoza
© 2025 L. David Mendoza. All Rights Reserved.

Purpose
- Generate public Google Patents search URLs
- No ownership inference
- No claim analysis

Output
- Search URLs only
"""

from __future__ import annotations

import urllib.parse
from typing import Dict


def patent_search_url(name: str) -> Dict:
    encoded = urllib.parse.quote_plus(name)
    return {
        "artifact_type": "patent_search",
        "url": f"https://patents.google.com/?q={encoded}",
        "source": "name_query",
        "confidence": "inferred"
    }
