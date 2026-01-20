#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI Talent Engine – Research-First Sourcer Automation
Entrypoint: Artifact Discovery Orchestrator
Version: v1.0.0-day2-artifacts
Date: 2025-12-30
Author: Dave Mendoza
© 2025 L. David Mendoza. All Rights Reserved.

Purpose
- Discover public technical artifacts per person
- Resume-safe
- No scoring, no inference beyond URLs

Inputs
- people_master.csv
- repo_inventory.csv

Outputs
- artifacts.json
- artifacts.csv
"""

from __future__ import annotations

import csv
import os
from typing import Dict, List

from scripts.enrich.github_pages_finder import find_github_pages
from scripts.enrich.scholar_finder import scholar_search_urls
from scripts.enrich.patent_finder import patent_search_url
from scripts.enrich.artifact_writer import write_artifacts


def load_people(path: str) -> List[Dict]:
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def run(run_dir: str, people_csv: str, repos: Dict[str, List[Dict]]) -> None:
    people = load_people(people_csv)
    artifacts: List[Dict] = []

    for p in people:
        person_id = p.get("person_id") or p.get("id") or p.get("login") or p.get("name")
        name = p.get("name") or p.get("login", "")

        profile = p
        person_repos = repos.get(person_id, [])

        for a in find_github_pages(profile, person_repos):
            a["person_id"] = person_id
            artifacts.append(a)

        for a in scholar_search_urls(name):
            a["person_id"] = person_id
            artifacts.append(a)

        patent = patent_search_url(name)
        patent["person_id"] = person_id
        artifacts.append(patent)

    write_artifacts(run_dir, artifacts)
