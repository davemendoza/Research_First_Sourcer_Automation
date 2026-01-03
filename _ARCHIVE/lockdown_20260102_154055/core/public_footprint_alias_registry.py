#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Public Footprint Alias Registry
AI Talent Engine — Canonical Alias Source of Truth

© 2026 L. David Mendoza

Purpose:
- Single authoritative registry for all public footprint surface detection
- Prevent alias drift across enrichers
- Maximize recall without schema pollution
- Enforce meaning-based normalization into canonical People schema fields

MANDATORY:
- All enrichers MUST import this file
- No alias logic is allowed outside this registry
"""

from __future__ import annotations
from typing import Dict

PUBLIC_FOOTPRINT_ALIAS_REGISTRY: Dict[str, Dict[str, object]] = {

    "resume": {
        "aliases": [
            "resume", "résumé",
            "cv", "c.v.", "c v",
            "curriculum vitae", "vitae",
            "academic cv", "research cv",
            "download cv", "view cv",
            "download resume", "view resume",
        ],
        "canonical_fields": ["Resume_URL", "Resume_File_Type", "Resume_Source"],
        "notes": "CV/Curriculum Vitae/Vitae are treated as Resume evidence. No parallel CV column allowed."
    },

    "personal_website": {
        "aliases": [
            "personal website", "personal site",
            "homepage", "home page",
            "about me", "bio",
            "profile", "author page",
            "academic homepage", "faculty page",
            "researcher page", "lab profile",
            "university profile", "google sites", "sites.google.com",
        ],
        "canonical_fields": ["Personal_Website_URL"],
        "notes": "Root hub for an individual (academic homepage included)."
    },

    "portfolio": {
        "aliases": [
            "portfolio", "work portfolio",
            "projects", "project portfolio",
            "selected work", "selected projects",
            "case studies", "work samples",
            "research projects", "academic projects",
            "experiments", "demos", "prototypes",
            "open source work", "code portfolio",
            "hackerrank", "leetcode", "codeforces",
            "stack overflow",
        ],
        "canonical_fields": ["Portfolio_URL"],
        "notes": "Curated body of work (not chronological writing)."
    },

    "blog": {
        "aliases": [
            "blog", "weblog", "posts", "articles",
            "writing", "writings", "essays",
            "thoughts", "notes", "journal",
            "research notes", "technical blog",
            "engineering blog", "lab notes",
            "medium", "substack", "ghost",
            "dev.to", "hashnode", "wordpress",
            "blogger", "jekyll",
        ],
        "canonical_fields": ["Blog_URL", "Blog_Source"],
        "notes": "Chronological writing; not scholarly publication counts."
    },

    "academic_publications": {
        "aliases": [
            "arxiv", "arxiv.org",
            "openalex", "openalex.org",
            "semantic scholar", "semanticscholar.org",
            "google scholar", "scholar.google.com",
            "dblp", "dblp.org",
            "ieee xplore", "ieeexplore.ieee.org",
            "acm digital library", "dl.acm.org",
            "springer", "nature", "sciencedirect",
            "neurips", "icml", "iclr", "cvpr", "eccv", "iccv",
            "openreview", "papers with code",
            "zenodo", "figshare",
            "researchgate", "researchgate.net",
        ],
        "canonical_fields": ["arXiv_URLs", "OpenAlex_Works_URLs", "SemanticScholar_Papers", "GoogleScholar_Profile_URL"],
        "notes": "Scholarly artifacts only. Supports citation math normalization."
    },

    "conference_activity": {
        "aliases": [
            "conference speaker",
            "keynote", "keynote speaker",
            "invited talk", "invited speaker",
            "plenary speaker",
            "panelist", "panel discussion",
            "fireside chat",
            "symposium", "symposium speaker",
            "workshop", "workshop presenter",
            "tutorial", "tutorial presenter",
            "seminar", "colloquium", "lecture",
            "oral presentation", "poster presentation",
            "slides", "slide deck", "presentation",
            "speakerdeck", "slideshare",
            "youtube", "vimeo",
        ],
        "canonical_fields": ["Conference_Talk_URLs", "Conference_Names", "Workshop_Presentations", "Slides_URLs", "Video_Talk_URLs"],
        "notes": "Talks/presentations/slides/recordings. Parsed into evidential columns, not notes-only."
    },

    "academic_identity": {
        "aliases": [
            "orcid", "orcid.org",
            "phd thesis", "doctoral thesis",
            "dissertation",
        ],
        "canonical_fields": ["ORCID_URL"],
        "notes": "Academic identity surfaces. Thesis links route to scholarly/provenance fields when discovered."
    },

    "company_xray": {
        "aliases": [
            "research team", "our team", "team", "people",
            "research", "publications", "authors",
            "blog authors", "author bio", "contributors",
            "labs", "researchers",
        ],
        "canonical_fields": ["Company_XRay_Public_URLs", "Company_XRay_Notes"],
        "notes": "Public-domain company research/team pages used as x-ray roots and provenance sources."
    },
}
