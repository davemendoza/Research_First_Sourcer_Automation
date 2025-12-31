"""
Run All — Phase H Orchestrator
One-command execution:
C → D → E → F → G → B → A

Notes:
- Track C runner is expected to exist as your existing discovery entrypoint.
  Provide --run-c path if your repo uses a different name.
- Track B/A runner names are configurable via flags.
- Phase H does not change any scraping logic; it orchestrates existing phases.

Example:
python3 run_all.py --run-c run_track_c.py --run-b run_track_b.py --run-a run_track_a.py --resume --verbose
"""

from __future__ import annotations
import argparse
from datetime import datetime, timezone
from pathlib import Path
import os

from phase_h_config import PhaseHConfig
from phase_h_logging import setup_logger
from phase_h_io import write_manifest
from phase_h_process import run_step

def _py() -> str:
    return os.environ.get("PYTHON", "python3")

def main() -> int:
    cfg = PhaseHConfig()

    ap = argparse.ArgumentParser()
    ap.add_argument("--run-c", type=str, default="run_track_c.py", help="Track C entrypoint (discovery)")
    ap.add_argument("--run-d", type=str, default=str(cfg.paths.run_d))
    ap.add_argument("--run-e", type=str, default=str(cfg.paths.run_e))
    ap.add_argument("--run-f", type=str, default=str(cfg.paths.run_f))
    ap.add_argument("--run-g", type=str, default=str(cfg.paths.run_g))
    ap.add_argument("--run-b", type=str, default=str(cfg.paths.run_b))
    ap.add_argument("--run-a", type=str, default=str(cfg.paths.run_a))

    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--resume", action="store_true")
    ap.add_argument("--verbose", action="store_true")
    ap.add_argument("--continue-on-error", action="store_true")

    # Pass-through knobs for Track C (if supported by your Track C runner)
    ap.add_argument("--rate-limit-rps", type=float, default=cfg.defaults.rate_limit_rps)
    ap.add_argument("--max-retries", type=int, default=cfg.defaults.max_retries)

    args = ap.parse_args()

    repo = cfg.paths.repo_root.resolve()
    cfg.paths.logs_dir.mkdir(parents=True, exist_ok=True)
    cfg.paths.phase_h_logs_dir.mkdir(parents=True, exist_ok=True)
    cfg.paths.manifests_dir.mkdir(parents=True, exist_ok=True)

    log_path = cfg.paths.phase_h_logs_dir / "run_all.log"
    logger = setup_logger(log_path, args.verbose)

    ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    manifest_name = f"run_all_manifest_{ts}.json"

    def step_cmd(script: str, extra: list[str]) -> list[str]:
        cmd = [_py(), script]
        if args.dry_run:
            cmd.append("--dry-run")
        if args.resume:
            cmd.append("--resume")
        if args.verbose:
            cmd.append("--verbose")
        cmd.extend(extra)
        return cmd

    steps = [
        ("Track C", step_cmd(args.run_c, ["--rate-limit-rps", str(args.rate_limit_rps), "--max-retries", str(args.max_retries)])),
        ("Phase D", step_cmd(args.run_d, [])),
        ("Phase E", step_cmd(args.run_e, [])),
        ("Phase F", step_cmd(args.run_f, [])),
        ("Phase G", step_cmd(args.run_g, [])),
        ("Track B", step_cmd(args.run_b, [])),
        ("Track A", step_cmd(args.run_a, [])),
    ]

    results = []
    overall_rc = 0

    logger.info("Run All starting (Phase H).")
    logger.info(f"Repo: {repo}")
    logger.info(f"Dry-run={args.dry_run} Resume={args.resume} Verbose={args.verbose}")

    for name, cmd in steps:
        logger.info(f"==> {name}: {' '.join(cmd)}")
        r = run_step(name=name, cmd=cmd, cwd=repo)

        results.append({
            "name": r.name,
            "cmd": r.cmd,
            "returncode": r.returncode,
            "stdout_tail": r.stdout[-2000:],  # tail only for manifest size safety
            "stderr_tail": r.stderr[-2000:],
        })

        if r.returncode != 0:
            overall_rc = r.returncode
            logger.error(f"{name} failed with rc={r.returncode}")
            if r.stderr:
                logger.error(r.stderr[-2000:])
            if not args.continue_on_error:
                logger.error("Stopping pipeline (use --continue-on-error to override).")
                break
        else:
            logger.info(f"{name} OK")

    manifest = {
        "phase": "H",
        "schema_version": cfg.schema_version,
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "repo_root": str(repo),
        "log_path": str(log_path),
        "args": {
            "dry_run": args.dry_run,
            "resume": args.resume,
            "verbose": args.verbose,
            "continue_on_error": args.continue_on_error,
            "rate_limit_rps": args.rate_limit_rps,
            "max_retries": args.max_retries,
            "entrypoints": {
                "run_c": args.run_c,
                "run_d": args.run_d,
                "run_e": args.run_e,
                "run_f": args.run_f,
                "run_g": args.run_g,
                "run_b": args.run_b,
                "run_a": args.run_a,
            }
        },
        "results": results,
        "governance": {
            "no_new_scraping_added": True,
            "deterministic_orchestration": True,
            "audit_manifest_written": True,
        }
    }

    mp = write_manifest(cfg.paths.manifests_dir, manifest_name, manifest)
    logger.info(f"Wrote manifest: {mp}")

    if overall_rc == 0:
        logger.info("Run All complete: SUCCESS")
    else:
        logger.error(f"Run All complete: FAILURE rc={overall_rc}")

    return overall_rc

if __name__ == "__main__":
    raise SystemExit(main())
