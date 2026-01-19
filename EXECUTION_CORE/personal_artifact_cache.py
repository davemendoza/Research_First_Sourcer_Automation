#!/usr/bin/env python3
"""
personal_artifact_cache.py

Day-2 Deterministic Cache for Personal Artifact Scraping
Author: L. David Mendoza © 2026

Purpose:
- Cache scraper output per person
- Deterministic replay for demos
- Prevent re-scraping same person repeatedly
- Safe fallback if network unavailable

No scraping, no mutation.
"""

import json
import os
import hashlib

CACHE_DIR = "outputs/personal_artifact_cache"


def ensure_cache_dir():
    os.makedirs(CACHE_DIR, exist_ok=True)


def cache_key(person_record):
    raw = (
        str(person_record.get("person_id", "")) + "|" +
        str(person_record.get("github_username", "")) + "|" +
        str(person_record.get("github_url", ""))
    )
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]


def cache_path(key):
    return os.path.join(CACHE_DIR, f"{key}.json")


def load_from_cache(person_record):
    ensure_cache_dir()
    key = cache_key(person_record)
    path = cache_path(key)
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return None


def write_to_cache(person_record, scraper_output):
    ensure_cache_dir()
    key = cache_key(person_record)
    path = cache_path(key)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(scraper_output, f, indent=2, ensure_ascii=False)
    return path
