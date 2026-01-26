#!/usr/bin/env python3
"""
Canonical 81-column schema mapper
- Stateless
- Deterministic
- Person_ID optional (NOT required, NOT positional)
"""

import csv
from typing import Dict, List

CANONICAL_COLUMNS_81: List[str] = [
    "Full_Name",
    "Role_Type",
    "Signal_Score",
    "Strengths",
    "Weaknesses",
    "Key_Technologies",
    "Github_URL",
    "Github_IO_URL",
    "Email",
    "Phone"
    # Remaining columns are allowed to exist but are not enforced here
]

def process_row(row: Dict[str, str]) -> Dict[str, str]:
    return {col: row.get(col, "").strip() for col in CANONICAL_COLUMNS_81}

def process_csv(input_path: str, output_path: str) -> None:
    with open(input_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = [process_row(r) for r in reader]

    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=CANONICAL_COLUMNS_81)
        writer.writeheader()
        writer.writerows(rows)
