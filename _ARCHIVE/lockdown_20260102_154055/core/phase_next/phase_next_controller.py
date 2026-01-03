from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List

from .constants import (
    DEFAULT_SEED_HUB_PATH,
    DEFAULT_READ_ONLY,
    DEFAULT_EXCEL_WRITE_ENABLED,
    DEFAULT_WATCHLIST_RULES_ENABLED,
    DEFAULT_GPT_WRITEBACK_ENABLED,
)
from .seed_hub_reader import load_seed_hubs
from .cadence import plan_from_tier, compute_domain_profile
from .watchlist_rules import WATCHLIST_RULES_ENABLED, evaluate_watchlist_candidate
from .gpt_writeback import GPT_WRITEBACK_ENABLED, prepare_gpt_writeback_payload

@dataclass(frozen=True)
class PhaseNextConfig:
    seed_hub_path: str = DEFAULT_SEED_HUB_PATH
    read_only: bool = DEFAULT_READ_ONLY
    excel_write_enabled: bool = DEFAULT_EXCEL_WRITE_ENABLED
    watchlist_rules_enabled: bool = DEFAULT_WATCHLIST_RULES_ENABLED
    gpt_writeback_enabled: bool = DEFAULT_GPT_WRITEBACK_ENABLED
    max_rows_total: int = 250  # demo-safe cap

def run_phase_next(repo_root: Path, cfg: PhaseNextConfig) -> Dict[str, Any]:
    # Enforce contract safety: read-only means no writes, period.
    if cfg.read_only:
        excel_write = False
        watchlist_enabled = False
        gpt_enabled = False
    else:
        excel_write = cfg.excel_write_enabled
        watchlist_enabled = cfg.watchlist_rules_enabled
        gpt_enabled = cfg.gpt_writeback_enabled

    # Print mode banner
    banner = {
        "read_only": cfg.read_only,
        "excel_write_enabled": excel_write,
        "watchlist_rules_enabled": watchlist_enabled,
        "gpt_writeback_enabled": gpt_enabled,
        "seed_hub_path": cfg.seed_hub_path,
        "max_rows_total": cfg.max_rows_total,
    }

    rows = load_seed_hubs(repo_root=repo_root, seed_hub_path=cfg.seed_hub_path)
    rows = rows[: cfg.max_rows_total]

    samples: List[Dict[str, Any]] = []
    for r in rows[: min(5, len(rows))]:
        meta = r.phase_next_metadata()
        cadence = plan_from_tier(meta.get("Monitoring_Tier"))
        domain_profile = compute_domain_profile(meta.get("Domain_Type", ""), meta.get("Source_Category", ""))

        # Watchlist decision is dormant unless enabled, and even then no Excel writes here.
        watch_decision = evaluate_watchlist_candidate(meta, signals={"provenance_confidence": domain_profile.provenance_confidence})

        # GPT payload prep is dormant unless enabled, and never calls an API here.
        payload = None
        if gpt_enabled:
            payload = prepare_gpt_writeback_payload(r.values, evaluation={"notes": "stub"})

        samples.append({
            "sheet": r.sheet_name,
            "row": r.row_index,
            "metadata": meta,
            "cadence": {
                "tier": cadence.tier,
                "interval_days": cadence.interval.days,
                "sample_cap": cadence.sample_cap,
                "notes": cadence.notes,
            },
            "domain_profile": {
                "semantic_weight": domain_profile.semantic_weight,
                "provenance_confidence": domain_profile.provenance_confidence,
                "notes": domain_profile.notes,
            },
            "watchlist_decision": watch_decision,
            "gpt_payload_prepared": bool(payload),
        })

    return {
        "banner": banner,
        "rows_loaded": len(rows),
        "sample_count": len(samples),
        "samples": samples,
        "writes_performed": False,
        "notes": "Phase-Next executed in read-only mode. No writes performed.",
    }
