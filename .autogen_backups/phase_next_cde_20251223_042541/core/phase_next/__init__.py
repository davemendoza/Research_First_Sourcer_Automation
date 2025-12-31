"""
Phase-Next (Continuous Discovery Layer)
READ-ONLY by default.

This package wires new Seed Hub metadata columns as read targets:
- Watchlist_Flag
- Monitoring_Tier
- Domain_Type
- Source_Category
- Language_Code

No writes unless explicitly enabled by flags in phase_next_controller.py.
"""
from .seed_hub_reader import SeedHubRow, load_seed_hubs
from .cadence import CadencePlan, plan_from_tier, compute_domain_profile
from .watchlist_rules import WATCHLIST_RULES_ENABLED, evaluate_watchlist_candidate
from .gpt_writeback import GPT_WRITEBACK_ENABLED, prepare_gpt_writeback_payload
