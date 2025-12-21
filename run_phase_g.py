"""
Run Phase G — Competitive Movement Escalation

Consumes:
- Phase E enqueue output (default), input-driven signals
Optionally incorporates:
- Phase D escalation flags (if provided / present)

Outputs:
- movement_signals.json
- clusters.json
- movement_escalation_scores.json
- run_manifest.json

Governance: no scraping, no crawling, no inference beyond input events.
"""

from __future__ import annotations
import argparse
from datetime import datetime, timezone
from pathlib import Path

from phase_g_config import PhaseGConfig
from phase_g_logging import setup_logger
from phase_g_io import read_json, write_run_manifest
from phase_g_normalize import normalize_events
from phase_g_cluster_detector import cluster_by_affiliation, cluster_by_affiliation_year_window
from phase_g_signal_scoring import score_events
from phase_g_watchlists import load_watchlist, filter_scores
from phase_g_outputs import write_signals, write_clusters, write_scores

def main() -> int:
    cfg = PhaseGConfig()

    ap = argparse.ArgumentParser()
    ap.add_argument("--input", type=str, default=str(cfg.paths.phase_e_enqueue_default))
    ap.add_argument("--out", type=str, default=str(cfg.paths.out_dir))
    ap.add_argument("--watchlist", type=str, default="")  # optional watchlist name
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--resume", action="store_true")
    ap.add_argument("--verbose", action="store_true")
    args = ap.parse_args()

    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    log_path = cfg.paths.logs_dir / "phase_g.log"
    logger = setup_logger(log_path, args.verbose)

    input_path = Path(args.input)
    if not input_path.exists():
        raise FileNotFoundError(f"Phase G input missing: {input_path}")

    scores_path = out_dir / "scores" / cfg.thresholds.resume_scores_filename
    if args.resume and scores_path.exists():
        logger.info("Resume enabled and scores already exist; exiting cleanly.")
        return 0

    raw = read_json(input_path)
    events = normalize_events(raw)

    logger.info(f"Loaded {len(events)} movement events from {input_path}")

    # Cluster detection (affiliation-level clusters)
    clusters = cluster_by_affiliation(events, cfg.thresholds.min_cluster_size)

    # Optional year-window clusters (only adds clusters when year present)
    year_window_clusters = cluster_by_affiliation_year_window(
        events,
        cfg.thresholds.min_cluster_size,
        cfg.thresholds.cluster_year_window
    )

    # Merge cluster dicts deterministically
    merged_clusters = {**clusters, **year_window_clusters}

    # Build cluster membership counts per person
    cluster_members = {}
    for _, c in merged_clusters.items():
        for name in c.get("members", []):
            cluster_members[name] = cluster_members.get(name, 0) + 1

    scores = score_events(events, cfg.role_weights.weights, cluster_members)

    if args.watchlist:
        watch = load_watchlist(args.watchlist)
        scores = filter_scores(scores, watch)
        logger.info(f"Watchlist applied: {args.watchlist} | Remaining scored: {len(scores)}")

    if args.dry_run:
        logger.info("Dry-run enabled; no files written.")
        logger.info(f"Clusters: {len(merged_clusters)} | Scores: {len(scores)}")
        return 0

    p1 = write_signals(out_dir, events)
    p2 = write_clusters(out_dir, merged_clusters)
    p3 = write_scores(out_dir, scores, cfg.output_schema_version)

    manifest = {
        "phase": "G",
        "schema_version": cfg.output_schema_version,
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "input_path": str(input_path),
        "output_dir": str(out_dir),
        "counts": {
            "events": len(events),
            "clusters": len(merged_clusters),
            "scored_people": len(scores),
        },
        "artifacts": {
            "movement_signals": str(p1),
            "clusters": str(p2),
            "scores": str(p3),
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

    logger.info("Phase G complete.")
    logger.info(f"Wrote: {p1}")
    logger.info(f"Wrote: {p2}")
    logger.info(f"Wrote: {p3}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
