#!/usr/bin/env python3
"""
personal_artifact_terminal_preview.py

Day-3 Terminal Preview Renderer
Author: L. David Mendoza © 2026

Purpose:
- Render a clean terminal preview of personal artifact intelligence
- Used during demo and debug runs

No scraping, no mutation.
"""

def render(person_id, evidence_summary, provenance_path):
    print("\n" + "=" * 72)
    print(f"PERSON ID: {person_id}")
    print("-" * 72)
    print(evidence_summary)
    if provenance_path:
        print(f"\nProvenance JSON: {provenance_path}")
    print("=" * 72 + "\n")


def run(person_id, evidence_summary, provenance_path):
    render(person_id, evidence_summary, provenance_path)
