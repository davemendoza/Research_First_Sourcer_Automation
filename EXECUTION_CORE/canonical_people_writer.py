#!/usr/bin/env python3
"""
Canonical People CSV Writer (LOCKED)

This module is responsible for writing the final canonical people CSV.
It MUST execute exactly once per pipeline run.

If called multiple times, it will silently no-op after the first write.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Iterable, Dict, Any

import pandas as pd

# ---------------------------------------------------------------------
# GLOBAL SINGLE-RUN GUARD
# ---------------------------------------------------------------------
_HAS_WRITTEN = False


def write_canonical_people_csv(
    rows: Iterable[Dict[str, Any]],
    output_path: Path,
) -> Path:
    """
    Write canonical people CSV exactly once.

    If invoked more than once in the same process, it will return
    the existing path without rewriting or printing spam.
    """

    global _HAS_WRITTEN

    if _HAS_WRITTEN:
        # Absolute silence on repeat calls — this kills the loop spam
        return output_path

    _HAS_WRITTEN = True

    output_path = output_path.resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Convert rows to DataFrame
    df = pd.DataFrame(list(rows))

    if df.empty:
        raise RuntimeError("Canonical people writer received zero rows")

    # Write once
    df.to_csv(output_path, index=False)

    print(f"✓ Wrote canonical CSV: {output_path}")
    print(f"Rows: {len(df)}, Columns: {len(df.columns)}")

    return output_path


# ---------------------------------------------------------------------
# BACKWARD-COMPATIBILITY ENTRY (if called as script)
# ---------------------------------------------------------------------
if __name__ == "__main__":
    print("❌ canonical_people_writer.py is not executable directly", file=sys.stderr)
    sys.exit(1)
