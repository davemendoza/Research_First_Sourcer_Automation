# © 2025 Dave Mendoza, DBA AI Craft, Inc. All rights reserved. Strictly proprietary; no copying, derivative works, reverse engineering, redistribution, or commercial/personal use permitted without written authorization. Governed by Colorado, USA law.
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

Proprietary Rights Notice
------------------------
All code, scripts, GitHub repositories, documentation, data, and GPT-integrated components of the AI Talent Engine – Signal Intelligence and Research_First_Sourcer_Automation Python Automation Sourcing Framework are strictly proprietary. All intellectual property rights, copyrights, trademarks, and related rights are exclusively owned by Dave Mendoza, DBA AI Craft, Inc.
No individual or entity may copy, reproduce, distribute, modify, create derivative works, reverse engineer, decompile, or otherwise use any part of this system, software, or associated materials for personal or commercial purposes without explicit written authorization from Dave Mendoza.
All rights reserved. Unauthorized use may result in legal action.
This statement is governed by the laws of the State of Colorado, USA.
