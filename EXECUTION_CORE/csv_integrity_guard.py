#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
csv_integrity_guard.py
------------------------------------------------
FAIL-CLOSED CSV INTEGRITY ENFORCER (LOCKED)

Policy change (2026-01-18):
- Person_ID is OPTIONAL and NOT REQUIRED
- If present, it is validated for non-emptiness
- If absent, pipeline proceeds safely

This preserves:
- Determinism
- Interview safety
- Schema guarantees
"""

from pathlib import Path
import csv


class CSVIntegrityError(RuntimeError):
    pass


# 🔒 REQUIRED columns (LOCKED)
REQUIRED_COLUMNS = [
    "Role_Type",
    "Signal_Score",
    "Strengths",
    "Weaknesses",
]

# Optional but validated if present
OPTIONAL_COLUMNS = {
    "Person_ID",
}


def enforce_csv_integrity(csv_path: Path) -> None:
    csv_path = Path(csv_path)
    if not csv_path.exists():
        raise CSVIntegrityError(f"CSV does not exist: {csv_path}")

    with csv_path.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        header = reader.fieldnames or []

        # Required columns
        missing = [c for c in REQUIRED_COLUMNS if c not in header]
        if missing:
            raise CSVIntegrityError(
                f"Canonical CSV missing required columns: {missing}"
            )

        # Validate optional columns if present
        row_count = 0
        for i, row in enumerate(reader, start=1):
            row_count += 1

            for col in OPTIONAL_COLUMNS:
                if col in header:
                    if not row.get(col, "").strip():
                        raise CSVIntegrityError(
                            f"Row {i}: Optional column '{col}' is present but empty"
                        )

        if row_count == 0:
            raise CSVIntegrityError("CSV contains zero data rows")


__all__ = ["CSVIntegrityError", "enforce_csv_integrity"]
