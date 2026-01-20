"""
Phase H Config — Daily-Use Hardening & Closure

Goals:
- One-command execution: C → D → E → F → G → B → A
- CLI flags, resume-safe runs, logging, rate limiting controls
- Deterministic, audit-ready manifests
- No scraping/crawling added by Phase H
"""

from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path

@dataclass(frozen=True)
class PhaseHPaths:
    repo_root: Path = Path(".")
    logs_dir: Path = Path("logs")
    phase_h_logs_dir: Path = Path("outputs/phase_h/logs")
    manifests_dir: Path = Path("outputs/phase_h/manifests")

    # Default runner entrypoints
    run_d: Path = Path("run_phase_d.py")
    run_e: Path = Path("run_phase_e.py")
    run_f: Path = Path("run_phase_f.py")
    run_g: Path = Path("run_phase_g.py")

    # Track B/A (expected to exist already in your repo; adjust paths if your filenames differ)
    run_b: Path = Path("run_track_b.py")
    run_a: Path = Path("run_track_a.py")

@dataclass(frozen=True)
class PhaseHDefaults:
    verbose: bool = False
    resume: bool = True
    dry_run: bool = False

    # Rate limiting is enforced in Track C; Phase H only passes through flags if present.
    rate_limit_rps: float = 1.0
    max_retries: int = 3

@dataclass(frozen=True)
class PhaseHConfig:
    paths: PhaseHPaths = PhaseHPaths()
    defaults: PhaseHDefaults = PhaseHDefaults()
    schema_version: str = "phase_h_v1"
