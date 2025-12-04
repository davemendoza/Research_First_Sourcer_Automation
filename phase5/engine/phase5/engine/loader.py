import os
import pandas as pd
from .enrich import enrich_dataframe

# engine/ -> phase5/ -> project root
ENGINE_DIR = os.path.dirname(os.path.abspath(__file__))
PHASE5_DIR = os.path.dirname(ENGINE_DIR)
PROJECT_ROOT = os.path.dirname(PHASE5_DIR)

PHASE5_ENRICHED = os.path.join(PHASE5_DIR, "phase5_enriched_talent.csv")

PHASE4_CANDIDATES = [
    os.path.join(PHASE5_DIR, "phase4_ranked_signals.csv"),
    os.path.join(PROJECT_ROOT, "phase2_demo", "phase4_ranked_signals.csv"),
]


def load_data() -> pd.DataFrame:
    # If we already have enriched Phase 5 CSV, load it
    if os.path.exists(PHASE5_ENRICHED):
        return pd.read_csv(PHASE5_ENRICHED)

    # Otherwise, find Phase 4 output, enrich it, and save
    for p in PHASE4_CANDIDATES:
        if os.path.exists(p):
            df4 = pd.read_csv(p)
            df5 = enrich_dataframe(df4)
            df5.to_csv(PHASE5_ENRICHED, index=False)
            return df5

    raise FileNotFoundError(
        f"Could not find phase4_ranked_signals.csv in {PHASE4_CANDIDATES}. "
        f"Run phase4_master_engine.py first."
    )
