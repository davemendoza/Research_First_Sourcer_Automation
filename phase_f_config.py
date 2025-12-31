"""
Phase F Config (Career Trajectory Modeling)

Contract: include best-practice options by default.
- Deterministic
- Resume-safe
- Auditable outputs
- Input-driven only
"""

from __future__ import annotations
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Dict, Pattern
import re

@dataclass(frozen=True)
class PhaseFPaths:
    phase_e_enqueue_default: Path = Path("outputs/phase_e/enqueue/conference_enqueue.json")
    out_dir: Path = Path("outputs/phase_f")
    logs_dir: Path = Path("outputs/phase_f/logs")
    timelines_dir: Path = Path("outputs/phase_f/timelines")
    velocity_dir: Path = Path("outputs/phase_f/velocity")
    flags_dir: Path = Path("outputs/phase_f/flags")

@dataclass(frozen=True)
class PhaseFThresholds:
    # Velocity: if a person has >= N distinct sources within a rolling window, flag
    min_events_for_velocity_signal: int = 3

    # If year is missing, we avoid timing-based claims
    require_year_for_transition: bool = True

@dataclass(frozen=True)
class PhaseFPatterns:
    # Conservative, configurable patterns. These do NOT claim ground truth.
    # They only generate flags when affiliation text strongly matches.
    academia_regexes: List[Pattern] = field(default_factory=lambda: [
        re.compile(r"\b(university|universität|universidad|college|institute of technology|polytechnic)\b", re.I),
        re.compile(r"\b(csail|mit|stanford|berkeley|cmu|eth zurich|oxford|cambridge)\b", re.I),
        re.compile(r"\b(lab|laboratory|research institute)\b", re.I),
    ])
    industry_regexes: List[Pattern] = field(default_factory=lambda: [
        re.compile(r"\b(inc\.|corp\.|llc|ltd|gmbh|ag)\b", re.I),
        re.compile(r"\b(openai|anthropic|deepmind|google|meta|microsoft|nvidia|apple)\b", re.I),
        re.compile(r"\b(startup|company)\b", re.I),
    ])

@dataclass(frozen=True)
class PhaseFConfig:
    paths: PhaseFPaths = PhaseFPaths()
    thresholds: PhaseFThresholds = PhaseFThresholds()
    patterns: PhaseFPatterns = PhaseFPatterns()

    # Schema stability: output keys are locked
    output_schema_version: str = "phase_f_v1"
