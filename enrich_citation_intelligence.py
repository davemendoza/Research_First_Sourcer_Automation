#!/usr/bin/env python3
"""
enrich_citation_intelligence.py

Phase 2 – CSV Runner for Citation Intelligence

Purpose:
--------
Read a CSV file, enrich rows with citation intelligence using
citation_intelligence_api.get_citation_profile(), and write results
to a new CSV with deterministic, audit-safe behavior.

Design Principles:
------------------
- No scraping
- No inference
- No silent overwrites
- Deterministic outputs
- Explicit provenance
- Interview-safe scope

Author:
-------
Dave Mendoza
© 2025 L. David Mendoza. All rights reserved.
"""

import csv
import argparse
import os
from typing import Dict, Any

from citation_intelligence_api import get_citation_profile


# -------------------------
# Configuration Defaults
# -------------------------

DEFAULT_NAME_COLUMN = "Full Name"

CITATION_COLUMNS = [
    "Citation_Source",
    "Total_Citations",
    "H_Index",
    "Works_Count",
    "Citation_Provenance"
]

OPTIONAL_YEARLY_COLUMN = "OpenAlex_Citations_By_Year"


# -------------------------
# Helpers
# -------------------------

def is_empty(value: Any) -> bool:
    return value is None or str(value).strip() == ""


def enrich_row(
    row: Dict[str, Any],
    name_column: str,
    include_yearly_counts: bool
) -> Dict[str, Any]:
    """
    Enrich a single CSV row with citation data.
    Existing non-empty values are preserved.
    """
    name = row.get(name_column)

    if is_empty(name):
        return row

    profile = get_citation_profile(name)

    # Core fields (never overwrite non-empty)
    mapping = {
        "Citation_Source": profile.get("source"),
        "Total_Citations": profile.get("total_citations"),
        "H_Index": profile.get("h_index"),
        "Works_Count": profile.get("works_count"),
        "Citation_Provenance": profile.get("provenance")
    }

    for col, value in mapping.items():
        if col not in row or is_empty(row[col]):
            row[col] = value

    # Optional OpenAlex yearly counts (stringified JSON-like dict)
    if include_yearly_counts:
        yearly = profile.get("yearly_citation_counts")
        if yearly and (OPTIONAL_YEARLY_COLUMN not in row or is_empty(row.get(OPTIONAL_YEARLY_COLUMN))):
            row[OPTIONAL_YEARLY_COLUMN] = str(yearly)

    return row


# -------------------------
# Main Runner
# -------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Phase 2 CSV runner for citation intelligence enrichment"
    )

    parser.add_argument(
        "--input",
        required=True,
        help="Path to input CSV file"
    )

    parser.add_argument(
        "--output",
        required=True,
        help="Path to output CSV file"
    )

    parser.add_argument(
        "--name-column",
        default=DEFAULT_NAME_COLUMN,
        help=f"Column containing full name (default: '{DEFAULT_NAME_COLUMN}')"
    )

    parser.add_argument(
        "--include-yearly-counts",
        action="store_true",
        help="Optionally include OpenAlex yearly citation counts (Phase 3-ready)"
    )

    args = parser.parse_args()

    if not os.path.exists(args.input):
        raise FileNotFoundError(f"Input CSV not found: {args.input}")

    with open(args.input, newline="", encoding="utf-8") as infile:
        reader = csv.DictReader(infile)
        fieldnames = list(reader.fieldnames) if reader.fieldnames else []

        # Ensure citation columns exist
        for col in CITATION_COLUMNS:
            if col not in fieldnames:
                fieldnames.append(col)

        if args.include_yearly_counts and OPTIONAL_YEARLY_COLUMN not in fieldnames:
            fieldnames.append(OPTIONAL_YEARLY_COLUMN)

        rows = []
        for row in reader:
            enriched = enrich_row(
                row=row,
                name_column=args.name_column,
                include_yearly_counts=args.include_yearly_counts
            )
            rows.append(enriched)

    with open(args.output, "w", newline="", encoding="utf-8") as outfile:
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"Enrichment complete. Output written to: {args.output}")


# -------------------------
# Entry Point
# -------------------------

if __name__ == "__main__":
    main()
