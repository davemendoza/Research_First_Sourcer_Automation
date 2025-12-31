"""
Phase G Config — Competitive Movement Escalation

Contract: include best-practice options by default.
- Deterministic, input-driven
- Resume-safe
- Auditable numeric scoring
- No scraping/crawling
"""

from __future__ import annotations
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List

@dataclass(frozen=True)
class PhaseGPaths:
    # Phase E enqueue is our default movement event substrate (conference emergence signals)
    phase_e_enqueue_default: Path = Path("outputs/phase_e/enqueue/conference_enqueue.json")
    # Optional: Phase D escalation flags can be incorporated if present
    phase_d_escalations_default: Path = Path("outputs/phase_d/escalations/people_escalations.json")

    out_dir: Path = Path("outputs/phase_g")
    logs_dir: Path = Path("outputs/phase_g/logs")
    signals_dir: Path = Path("outputs/phase_g/signals")
    clusters_dir: Path = Path("outputs/phase_g/clusters")
    scores_dir: Path = Path("outputs/phase_g/scores")

@dataclass(frozen=True)
class PhaseGThresholds:
    # Cluster detection: how many signals constitute a "cluster"
    min_cluster_size: int = 3

    # Optional time-window clustering (only used if year present)
    cluster_year_window: int = 1

    # Resume safe: do nothing if scores exist and --resume passed
    resume_scores_filename: str = "movement_escalation_scores.json"

@dataclass(frozen=True)
class RoleCriticalityWeights:
    """
    Role criticality weighting.
    These are conservative defaults and can be tailored later via config.
    """
    weights: Dict[str, float] = field(default_factory=lambda: {
        "Frontier": 1.50,
        "Foundational": 1.50,
        "RLHF": 1.40,
        "AI_Infra": 1.35,
        "Performance": 1.35,
        "Applied_ML": 1.20,
        "AI_Engineer": 1.15,
        "Solutions_Architect": 1.05,
        "DevRel": 1.05,
        "General": 1.00,
        "Unknown": 1.00
    })

@dataclass(frozen=True)
class PhaseGConfig:
    paths: PhaseGPaths = PhaseGPaths()
    thresholds: PhaseGThresholds = PhaseGThresholds()
    role_weights: RoleCriticalityWeights = RoleCriticalityWeights()

    output_schema_version: str = "phase_g_v1"
