import pandas as pd
from pathlib import Path

def load_scenarios(xlsx_path: str):
    df = pd.read_excel(xlsx_path)
    required = {"scenario", "seed_type", "seed_value", "tier", "category"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"Scenario matrix missing columns: {missing}")
    return df
