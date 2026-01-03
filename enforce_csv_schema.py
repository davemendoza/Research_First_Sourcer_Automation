from contracts.canonical_people_schema import enforce_canonical
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations
import pandas as pd
from pathlib import Path

REQUIRED_PREFIX_COLUMNS = [
    "Person_ID",
    "Full_Name",
    "Role_Type",
    "Email",
    "Phone",
    "LinkedIn_URL",
    "GitHub_URL",
    "GitHub_IO_URL",
    "Google_Scholar_URL",
    "Resume_or_CV_URL",
]

def enforce_csv_schema(path: Path) -> None:
    df = pd.read_csv(path)

    missing = [c for c in REQUIRED_PREFIX_COLUMNS if c not in df.columns]
    if missing:
        raise RuntimeError(f"CSV missing required columns: {missing}")

    remaining = [c for c in df.columns if c not in REQUIRED_PREFIX_COLUMNS]
    df = df[REQUIRED_PREFIX_COLUMNS + remaining]

df = enforce_canonical(df)
    df.to_csv(path, index=False)
