#!/usr/bin/env python3
"""
personal_artifact_enrichment_adapter.py

Adapter layer between run_safe.py and deep_personal_artifact_scrape.py

Contract:
- Import-only
- No filesystem writes
- No sys.path mutation
- Non-overwrite safe
- Deterministic
"""

from typing import Dict, Any

# IMPORTANT:
# deep_personal_artifact_scrape exports ONLY:
#   deep_scrape_person(person_record)
# There is NO `run()` or `scrape()` function.

from deep_personal_artifact_scrape import deep_scrape_person


def run(existing_row: Dict[str, Any], person_record: Dict[str, Any]) -> Dict[str, Any]:
    """
    Adapter wrapper required by run_safe.py

    Args:
        existing_row: canonical people row (dict)
        person_record: identity seed (person_id, github, urls, etc.)

    Returns:
        dict with:
            row_updates
            blank_explanations
            provenance_path
            evidence_summary
    """

    result = deep_scrape_person(person_record)

    if not isinstance(result, dict):
        raise ValueError("deep_scrape_person() must return a dict")

    return {
        "row_updates": result.get("row_updates", {}),
        "blank_explanations": result.get("blank_explanations", {}),
        "provenance_path": result.get("provenance_path"),
        "evidence_summary": result.get("evidence_summary"),
    }
