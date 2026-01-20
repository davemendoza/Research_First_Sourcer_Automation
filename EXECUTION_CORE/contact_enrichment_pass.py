#!/usr/bin/env python3
"""
contact_enrichment_pass.py

Public contact enrichment (email/phone placeholders).
"""

import csv

def process_csv(input_path: str, output_path: str) -> None:
    with open(input_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = []

        for r in reader:
            r.setdefault("Public_Email", "")
            r.setdefault("Public_Phone", "")
            rows.append(r)

    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)
