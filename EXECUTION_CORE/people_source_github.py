#!/usr/bin/env python3
"""
people_source_github.py

Deterministic GitHub signal enrichment.
No network calls. Safe baseline.
"""

import csv

def process_csv(input_path: str, output_path: str) -> None:
    with open(input_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = []

        for r in reader:
            r.setdefault("Github_URL", "")
            r.setdefault("Github_IO_URL", "")
            r.setdefault("OSS_Activity", "")
            rows.append(r)

    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)
