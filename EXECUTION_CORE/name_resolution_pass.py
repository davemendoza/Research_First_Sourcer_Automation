"""
EXECUTION_CORE/name_resolution_pass.py
============================================================
BEST-IN-CLASS NAME + CONTACT PASS

Maintainer: L. David Mendoza © 2026
Version: v2.1.4 (Regression-safe dual interface)

Contract:
- clean_name(str) -> str
- run_name_resolution_pass(rows) -> rows
- process_csv(input_csv, output_csv) -> None
"""
from __future__ import annotations
import csv
import re
from typing import Dict, List
from EXECUTION_CORE.public_identity_contact_pass import enrich_rows_public_identity_contact

def clean_name(s: str) -> str:
    if s is None:
        return ''
    s = str(s).strip()
    if not s:
        return ''
    return _WS_RE.sub(' ', s)

def run_name_resolution_pass(rows: List[Dict[str, str]]) -> List[Dict[str, str]]:
    """
    Regression-safe entrypoint.
    Operates purely in-memory.
    """
    return enrich_rows_public_identity_contact(rows)

def process_csv(input_csv: str, output_csv: str) -> None:
    with open(input_csv, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        fieldnames = list(reader.fieldnames or [])
        rows: List[Dict[str, str]] = list(reader)
    must_cols = ['Full_Name', 'First_Name', 'Last_Name', 'Primary_Email', 'Primary_Phone', 'LinkedIn_Public_URL', 'Seed_Query_Or_Handle', 'Field_Level_Provenance_JSON']
    for c in must_cols:
        if c not in fieldnames:
            fieldnames.append(c)
    rows = run_name_resolution_pass(rows)
    with open(output_csv, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for r in rows:
            writer.writerow({k: r.get(k, '') for k in fieldnames})
__all__ = ['clean_name', 'run_name_resolution_pass', 'process_csv']

def _cli_main():
    _WS_RE = re.compile('\\s+', re.UNICODE)
if __name__ == '__main__':
    _cli_main()
