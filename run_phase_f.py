"""
Run Phase F — Career Trajectory Modeling

Consumes input-driven metadata (default: Phase E enqueue output).
Outputs:
- timelines.json
- velocity.json
- career_flags.json
- run_manifest.json

No scraping. No crawling. Deterministic.
"""

from __future__ import annotations
import argparse
from datetime import datetime, timezone
from pathlib import Path

from phase_f_config import PhaseFConfig
from phase_f_logging import setup_logger
from phase_f_io import read_json, write_run_manifest
from phase_f_normalize import normalize_records
from phase_f_timeline_builder import build_timelines
from phase_f_transition_detector import detect_transitions
from phase_f_velocity_analyzer import analyze_velocity
from phase_f_outputs import write_timelines, write_velocity, write_flags

def main() -> int:
    cfg = PhaseFConfig()

    ap = argparse.ArgumentParser()
    ap.add_argument("--input", type=str, default=str(cfg.paths.phase_e_enqueue_default))
    ap.add_argument("--out", type=str, default=str(cfg.paths.out_dir))
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--resume", action="store_true")
    ap.add_argument("--verbose", action="store_true")
    args = ap.parse_args()

    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    log_path = cfg.paths.logs_dir / "phase_f.log"
    logger = setup_logger(log_path, args.verbose)

    input_path = Path(args.input)
    if not input_path.exists():
        raise FileNotFoundError(f"Phase F input missing: {input_path}")

    # Resume-safe: if outputs exist and --resume set, do nothing
    flags_path = out_dir / "flags" / "career_flags.json"
    if args.resume and flags_path.exists():
        logger.info("Resume enabled and outputs already exist; exiting cleanly.")
        return 0

    raw = read_json(input_path)
    records = normalize_records(raw if isinstance(raw, list) else [])

    logger.info(f"Loaded {len(records)} normalized records from {input_path}")

    timelines = build_timelines(records)

    transitions = detect_transitions(
        timelines=timelines,
        academia_regexes=cfg.patterns.academia_regexes,
        industry_regexes=cfg.patterns.industry_regexes,
        require_year=cfg.thresholds.require_year_for_transition,
    )

    velocity = analyze_velocity(
        timelines=timelines,
        min_events=cfg.thresholds.min_events_for_velocity_signal,
    )

    if args.dry_run:
        logger.info("Dry-run enabled; no files written.")
        logger.info(f"Timelines: {len(timelines)} | Transitions: {len(transitions)} | Velocity: {len(velocity)}")
        return 0

    p1 = write_timelines(out_dir, timelines)
    p2 = write_velocity(out_dir, velocity)
    p3 = write_flags(out_dir, transitions, velocity, cfg.output_schema_version)

    manifest = {
        "phase": "F",
        "schema_version": cfg.output_schema_version,
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "input_path": str(input_path),
        "output_dir": str(out_dir),
        "counts": {
            "records": len(records),
            "timelines": len(timelines),
            "transitions": len(transitions),
            "velocity": len(velocity),
        },
        "artifacts": {
            "timelines": str(p1),
            "velocity": str(p2),
            "flags": str(p3),
            "log": str(log_path),
        },
        "governance": {
            "no_scraping": True,
            "no_crawling": True,
            "deterministic": True,
            "input_driven_only": True,
        }
    }
    write_run_manifest(out_dir, manifest)

    logger.info("Phase F complete.")
    logger.info(f"Wrote: {p1}")
    logger.info(f"Wrote: {p2}")
    logger.info(f"Wrote: {p3}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
