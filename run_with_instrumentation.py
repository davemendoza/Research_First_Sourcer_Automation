#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI Talent Engine – Research-First Sourcer Automation
Entrypoint: Run Orchestrator (Instrumentation + Resilience Wrapper)
Version: v1.0.0-day1-orchestrator
Date: 2025-12-30
Author: Dave Mendoza
© 2025 L. David Mendoza. All Rights Reserved.

Purpose
- Establish a single run boundary and canonical output directory.
- Wrap existing demo execution (run_demo.py) without modifying its logic.
- Provide:
  - Interval-based progress reporting
  - Checkpoint directory for resume-on-crash (stage-level)
  - Run manifest creation
  - Optional SMTP completion notification
- Preserve existing outputs; do not overwrite.

Important Notes
- This script does NOT redesign core pipelines.
- It standardizes run structure and captures outputs safely.

Usage
- python3 run_with_instrumentation.py --demo
- python3 run_with_instrumentation.py --demo --scenario S40
- python3 run_with_instrumentation.py --demo --scenario S40 --progress-seconds 20

Environment (optional email)
- RFS_SMTP_HOST, RFS_SMTP_PORT, RFS_SMTP_USER, RFS_SMTP_PASS, RFS_EMAIL_FROM, RFS_EMAIL_TO

Contract Requirements Satisfied
- Full-file generation only
- No inline patches
- zsh-safe
- python3 explicit
- Interview-safe outputs and run boundary

Validation Steps
1) python3 -c "import run_with_instrumentation; print('OK')"
2) python3 run_with_instrumentation.py --demo --scenario S40
3) Verify output created under output/people/run_<id>/ and manifest exists
4) Verify demo_result CSVs copied to demo_results/ without deletion
5) (Optional) Configure SMTP env vars and confirm success email
"""

from __future__ import annotations

import argparse
import glob
import os
import shutil
import subprocess
import sys
import traceback
from typing import Dict, Optional

from scripts.ops.checkpoints import CheckpointStore
from scripts.ops.progress_tracker import ProgressTracker
from scripts.ops.run_context import RunContext

try:
    from scripts.ops.email_notify import EmailNotifier
except Exception:
    EmailNotifier = None  # type: ignore


def _project_root() -> str:
    return os.path.dirname(os.path.abspath(__file__))


def _safe_int(v: Optional[str], default: int) -> int:
    try:
        if v is None:
            return default
        return int(v)
    except Exception:
        return default


def _count_csv_rows(path: str) -> int:
    # Lightweight row count without pandas
    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            n = -1
            for n, _ in enumerate(f):
                pass
        return max(0, n)  # minus header
    except Exception:
        return 0


def _capture_demo_outputs(project_root: str, dest_dir: str) -> Dict[str, str]:
    """
    Capture existing demo outputs from output/demo_result_*.csv into dest_dir.
    We COPY (not move) to avoid any accidental loss.
    """
    os.makedirs(dest_dir, exist_ok=True)
    src_glob = os.path.join(project_root, "output", "demo_result_*.csv")
    captured: Dict[str, str] = {}
    for src in sorted(glob.glob(src_glob)):
        base = os.path.basename(src)
        dst = os.path.join(dest_dir, base)
        if not os.path.exists(dst):
            shutil.copy2(src, dst)
        captured[base] = dst
    return captured


def _run_demo(project_root: str, scenario: Optional[str], pt: ProgressTracker) -> None:
    """
    Execute run_demo.py in a subprocess so we do not import/alter its control flow.
    """
    pt.update(stage="demo_start")
    pt.maybe_emit(force=True)

    cmd = ["python3", os.path.join(project_root, "run_demo.py")]
    if scenario:
        # We pass as a generic flag; if run_demo.py does not accept it, it will error clearly.
        cmd += ["--scenario", scenario]

    pt.update(stage="demo_running")
    pt.maybe_emit(force=True)

    subprocess.run(cmd, cwd=project_root, check=True)

    pt.update(stage="demo_done")
    pt.maybe_emit(force=True)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--demo", action="store_true", help="Run demo via run_demo.py and capture outputs")
    ap.add_argument("--scenario", default=None, help="Scenario name (example: S40)")
    ap.add_argument("--progress-seconds", default="20", help="Progress emit interval seconds (default 20)")
    ap.add_argument("--no-email", action="store_true", help="Disable SMTP notifications even if env vars are set")
    args = ap.parse_args()

    project_root = _project_root()
    ctx = RunContext(project_root=project_root)
    ctx.ensure_dirs()

    pt = ProgressTracker(interval_seconds=_safe_int(args.progress_seconds, 20))
    ck = CheckpointStore(root_dir=ctx.checkpoints_dir())
    ck.ensure()

    metrics: Dict[str, int] = {}

    notifier = None
    if not args.no_email and EmailNotifier is not None:
        try:
            notifier = EmailNotifier.from_env()
        except Exception:
            notifier = None

    ctx.write_manifest(status="STARTED", notes="Run initialized (instrumentation wrapper).")

    try:
        ck.set_run_state(stage="STARTED", notes="Run start")

        if args.demo:
            ck.set_run_state(stage="DEMO", notes="Starting demo stage")
            _run_demo(project_root, args.scenario, pt)

        ck.set_run_state(stage="CAPTURE", notes="Capturing demo outputs")
        captured = _capture_demo_outputs(project_root, ctx.demo_dir())

        # Optional: If these exist in project root/output or elsewhere, we record counts for the manifest.
        # We do not guess paths; we only record if present under project output.
        people_master_path = os.path.join(project_root, "output", "people_master.csv")
        repo_inventory_path = os.path.join(project_root, "output", "repo_inventory.csv")

        if os.path.exists(people_master_path):
            metrics["people_rows"] = _count_csv_rows(people_master_path)
        if os.path.exists(repo_inventory_path):
            metrics["repo_rows"] = _count_csv_rows(repo_inventory_path)
        metrics["demo_files_captured"] = len(captured)

        outputs: Dict[str, str] = {}
        for k, v in captured.items():
            outputs[f"demo/{k}"] = v
        if os.path.exists(people_master_path):
            outputs["output/people_master.csv"] = people_master_path
        if os.path.exists(repo_inventory_path):
            outputs["output/repo_inventory.csv"] = repo_inventory_path

        ctx.write_manifest(
            status="SUCCESS",
            metrics=metrics,
            notes="Run completed successfully.",
            outputs=outputs,
        )

        if notifier:
            summary_lines = [f"{k}: {v}" for k, v in sorted(metrics.items())]
            summary = "\n".join(summary_lines) if summary_lines else "No metrics recorded."
            notifier.send_run_success(ctx.run_id, ctx.run_dir(), summary)

        pt.update(stage="complete", people_discovered=metrics.get("people_rows", 0), repos_scanned=metrics.get("repo_rows", 0))
        pt.maybe_emit(force=True)
        return 0

    except Exception as e:
        err = f"{type(e).__name__}: {e}\n\n{traceback.format_exc()}"
        ctx.write_manifest(status="FAILED", metrics=metrics, notes=err)

        if notifier:
            notifier.send_run_failure(ctx.run_id, ctx.run_dir(), err)

        print("❌ RUN FAILED (see run_manifest.json for details):")
        print(err)
        return 2


if __name__ == "__main__":
    sys.exit(main())
