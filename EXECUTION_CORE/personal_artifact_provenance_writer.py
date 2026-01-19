#!/usr/bin/env python3
"""
personal_artifact_provenance_writer.py

Day-1 Provenance Persistence Module
Author: L. David Mendoza © 2026

Purpose:
- Persist deep personal artifact scrape provenance
- Persist crawl logs for auditability
- One JSON file per person_id
- Deterministic, non-destructive writes

This module performs:
✓ provenance persistence
✓ crawl log persistence
✓ deterministic filenames
✗ no scraping
✗ no enrichment
✗ no overwrites by default
"""

import json
import os
from datetime import datetime

# ------------------------------------------------------------------------------
# CONSTANTS (LOCKED)
# ------------------------------------------------------------------------------

OUTPUT_DIR = "outputs/personal_artifact_provenance"
TIMESTAMP_FMT = "%Y-%m-%dT%H:%M:%SZ"

# ------------------------------------------------------------------------------
# HELPERS
# ------------------------------------------------------------------------------

def ensure_output_dir():
    os.makedirs(OUTPUT_DIR, exist_ok=True)


def build_filename(person_id):
    safe_id = "".join(c for c in str(person_id) if c.isalnum() or c in ("_", "-"))
    return f"{safe_id}.json"


def current_utc_timestamp():
    return datetime.utcnow().strftime(TIMESTAMP_FMT)


# ------------------------------------------------------------------------------
# CORE WRITE LOGIC
# ------------------------------------------------------------------------------

def write_provenance(person_id, scraper_output, allow_overwrite=False):
    """
    Writes provenance JSON for a single person.

    Args:
        person_id (str)
        scraper_output (dict): output from deep_personal_artifact_scrape.run()
        allow_overwrite (bool): default False

    Returns:
        str: path to written file
    """

    ensure_output_dir()
    filename = build_filename(person_id)
    path = os.path.join(OUTPUT_DIR, filename)

    if os.path.exists(path) and not allow_overwrite:
        return path  # non-destructive

    payload = {
        "person_id": person_id,
        "generated_at": current_utc_timestamp(),
        "source": "deep_personal_artifact_scrape_day1",
        "scrape_provenance": scraper_output.get("discovered", {}),
        "crawl_log": scraper_output.get("crawl_log", {}),
    }

    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)

    return path


# ------------------------------------------------------------------------------
# PUBLIC ENTRYPOINT
# ------------------------------------------------------------------------------

def run(person_id, scraper_output):
    """
    Convenience wrapper.
    """
    return write_provenance(person_id, scraper_output)
