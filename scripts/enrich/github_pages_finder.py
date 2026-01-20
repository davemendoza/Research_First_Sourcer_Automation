#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI Talent Engine – Research-First Sourcer Automation
Module: GitHub Pages & Personal Site Finder
Version: v1.0.0-day2-artifacts
Date: 2025-12-30
Author: Dave Mendoza
© 2025 L. David Mendoza. All Rights Reserved.

Purpose
- Discover GitHub Pages (github.io) and personal tech sites
- Use only public GitHub profile + repo metadata
- Record provenance and confidence (direct vs inferred)

Out of Scope
- No scraping behind auth
- No guessing domains
- No enrichment scoring

Output Schema (per artifact)
- artifact_type
- url
- source
- confidence
"""

from __future__ import annotations

from typing import Dict, List


def find_github_pages(profile: Dict, repos: List[Dict]) -> List[Dict]:
    artifacts = []

    username = profile.get("login")
    blog = profile.get("blog", "").strip()

    if username:
        gh_pages_url = f"https://{username}.github.io"
        artifacts.append({
            "artifact_type": "github_pages",
            "url": gh_pages_url,
            "source": "github_profile_username",
            "confidence": "direct"
        })

    if blog.startswith("http"):
        artifacts.append({
            "artifact_type": "personal_site",
            "url": blog,
            "source": "github_profile_blog",
            "confidence": "direct"
        })

    for repo in repos:
        homepage = repo.get("homepage", "")
        if homepage and homepage.startswith("http"):
            artifacts.append({
                "artifact_type": "project_homepage",
                "url": homepage,
                "source": "github_repo_homepage",
                "confidence": "direct"
            })

    # de-duplicate by URL
    seen = set()
    unique = []
    for a in artifacts:
        if a["url"] not in seen:
            unique.append(a)
            seen.add(a["url"])

    return unique
