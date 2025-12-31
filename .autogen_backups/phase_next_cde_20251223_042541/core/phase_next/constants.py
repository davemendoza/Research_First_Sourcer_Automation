from __future__ import annotations

from dataclasses import dataclass

DEFAULT_SEED_HUB_PATH = "data/AI_Talent_Landscape_Seed_Hubs.xlsx"

# Column names as they exist in the Excel workbook (targets only, not populated here)
COL_WATCHLIST_FLAG = "Watchlist_Flag"
COL_MONITORING_TIER = "Monitoring_Tier"
COL_DOMAIN_TYPE = "Domain_Type"
COL_SOURCE_CATEGORY = "Source_Category"
COL_LANGUAGE_CODE = "Language_Code"

# Safety defaults (enforced by controller)
DEFAULT_READ_ONLY = True
DEFAULT_EXCEL_WRITE_ENABLED = False
DEFAULT_WATCHLIST_RULES_ENABLED = False
DEFAULT_GPT_WRITEBACK_ENABLED = False

# Reasonable normalizations for tiers and language
ALLOWED_TIERS = {"T0", "T1", "T2", "T3", "T4"}
DEFAULT_TIER = "T3"  # middle-of-the-road cadence by default (read-only)
DEFAULT_LANGUAGE_CODE = "en"

@dataclass(frozen=True)
class DomainProfile:
    domain_type: str
    source_category: str
    semantic_weight: float
    provenance_confidence: float
    notes: str
