#!/usr/bin/env python3
"""
people_identity_contact_pass.py

Normalizes identity + contact fields.
"""

import csv

def process_csv(input_path: str, output_path: str) -> None:
    with open(input_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    for r in rows:
        r.setdefault("Full_Name", "")
        r.setdefault("Primary_Contact", r.get("Public_Email", ""))

    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)
