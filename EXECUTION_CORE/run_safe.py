#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
AI Talent Engine | Research-First Sourcer Automation
File: EXECUTION_CORE/run_safe.py

Author: © 2026 L. David Mendoza. All rights reserved.
Version: v2.1.0-run-safe-orchestrator-metrics-aligned
Date: 2026-01-06

LOCKED PURPOSE
This is the ONE thing you run to produce interview-grade, public-domain-only, evidence-backed people CSV outputs:
- DEMO runs (bounded 25 to 50 real people)
- SCENARIO runs (unbounded, all available valid people)
- GPT-SLIM runs (runs DEMO-bounded pipeline, then triggers GPT-Slim runner only if present)

NON-NEGOTIABLES
- No synthetic data. No placeholders. No inferred identity. No fabricated contact info.
- Truthful sparsity: if not found publicly, leave blank.
- Mandatory terminal metrics (accurate counters) for:
  github_ok, github_io, resume_cv_rows, email_rows, phone_rows, domains_crawled, repos_scanned
- Mandatory CSV auto-open on macOS (uses `open`).
- No parallel pipelines introduced. No renames. No new files.

WIRING (BEST PRACTICE)
- run_people_pipeline.py (repo root) is Phase 1 inventory only.
- EXECUTION_CORE/people_source_github.py is Phase 2 enrichment module only.
- This file orchestrates them.

WHAT WAS FIXED IN THIS VERSION
- Metrics key alignment with EXECUTION_CORE/people_source_github.py.
  Prior versions used different keys (github_profiles_ok, github_io_found, resume_or_cv_rows) which caused false terminal output.

VALIDATION
1) python3 -m py_compile EXECUTION_CORE/run_safe.py
2) DEMO:
   python3 EXECUTION_CORE/run_safe.py demo frontier_ai_scientist
3) SCENARIO:
   python3 EXECUTION_CORE/run_safe.py scenario frontier_ai_scientist
4) GPT-SLIM (optional runner only if present):
   python3 EXECUTION_CORE/run_safe.py gpt_slim frontier_ai_scientist

GIT (SSH)
git status
git add EXECUTION_CORE/run_safe.py
git commit -m "Fix run_safe: align metrics keys with people_source_github [v2.1.0]"
git push
"""

from __future__ import annotations

import argparse
import csv
import os
import platform
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Tuple

import pandas as pd

# Phase 2 enrichment module (locked path)
from people_source_github import enrich_person_from_github_and_web


REPO_ROOT_PHASE1_RUNNER = "run_people_pipeline.py"
DEFAULT_OUT_BASE = Path("outputs") / "people"

PIPELINE_VERSION = "v2.1.0-run-safe-orchestrator-metrics-aligned"


def _utc_stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")


def _info(msg: str) -> None:
    print(msg, flush=True)


def _warn(msg: str) -> None:
    print(f"WARNING: {msg}", file=sys.stderr, flush=True)


def _die(msg: str, code: int = 2) -> None:
    print(f"ERROR: {msg}", file=sys.stderr, flush=True)
    raise SystemExit(code)


def _ensure_file(path: Path, label: str) -> None:
    if not path.is_file():
        _die(f"Missing required file: {label}: {path}")


def _mac_open(path: Path) -> None:
    if platform.system().lower() != "darwin":
        return
    try:
        subprocess.run(["open", str(path)], check=False)
    except Exception as ex:
        _warn(f"Auto-open failed (non-fatal): {ex}")


def _run_phase1(mode: str, scenario: str, out_dir: Path, detail_lookups: int) -> Path:
    """
    Phase 1 inventory runner is repo-root run_people_pipeline.py.
    Produces: <out_dir>/people_master.csv
    """
    _ensure_file(Path(REPO_ROOT_PHASE1_RUNNER), "Phase 1 runner run_people_pipeline.py (repo root)")

    cmd: List[str] = [
        sys.executable,
        REPO_ROOT_PHASE1_RUNNER,
        "--scenario",
        scenario,
        "--detail-lookups",
        str(int(detail_lookups)),
        "--out-dir",
        str(out_dir),
    ]

    if mode == "demo":
        # Demo is explicitly bounded.
        cmd.extend(["--min-people", "25", "--hard-cap-total", "50"])
    elif mode in ("scenario", "gpt_slim"):
        # Scenario and gpt_slim are unbounded at Phase 1 by default.
        # gpt_slim uses demo-bounded Phase 2, not Phase 1 caps.
        pass
    else:
        _die(f"Invalid mode: {mode}. Allowed: demo, scenario, gpt_slim")

    _info("\n=== PHASE 1: INVENTORY (DISCOVERY) ===")
    _info("Command: " + " ".join(cmd))
    rc = subprocess.call(cmd)
    if rc != 0:
        _die(f"Phase 1 inventory runner failed with exit code: {rc}")

    master_csv = out_dir / "people_master.csv"
    _ensure_file(master_csv, "Phase 1 output people_master.csv")

    # Sanity: non-empty
    try:
        with master_csv.open("r", encoding="utf-8", errors="replace") as f:
            lines = f.readlines()
        if len(lines) <= 1:
            _die("people_master.csv is empty (header only). Upstream seed insufficiency or Phase 1 defect.")
    except Exception as ex:
        _die(f"Failed to read people_master.csv: {ex}")

    return master_csv


def _read_csv_rows(path: Path) -> Tuple[List[str], List[Dict[str, str]]]:
    with path.open("r", encoding="utf-8", errors="replace", newline="") as f:
        reader = csv.DictReader(f)
        fields = reader.fieldnames or []
        rows = [dict(r) for r in reader]
    return fields, rows


def _phase2_enrich(master_csv: Path, scenario: str, out_dir: Path, mode: str) -> Path:
    """
    Phase 2 enrichment using EXECUTION_CORE/people_source_github.py module.
    Writes: <out_dir>/people_enriched.csv
    """
    out_dir.mkdir(parents=True, exist_ok=True)
    enriched_csv = out_dir / "people_enriched.csv"

    in_fields, rows = _read_csv_rows(master_csv)

    # Phase 2 will only add or fill explicitly discovered evidence.
    df_in = pd.DataFrame(rows)

    # Ensure a minimal spine exists. We do not delete columns, and we do not invent new schema here.
    # We allow Phase 2 module to populate known fields if present.
    for c in ["GitHub_Username", "GitHub_URL", "GitHub_IO_URL", "Primary_Email", "Primary_Phone", "Resume_URL", "CV_URL"]:
        if c not in df_in.columns:
            df_in[c] = ""

    # Metrics keys MUST match people_source_github.py bump() calls.
    metrics: Dict[str, int] = {
        "rows_processed": 0,
        "github_ok": 0,
        "github_io": 0,
        "resume_cv_rows": 0,
        "email_rows": 0,
        "phone_rows": 0,
        "domains_crawled": 0,
        "repos_scanned": 0,
    }

    _info("\n=== PHASE 2: ENRICHMENT (GITHUB + github.io + PERSONAL DOMAINS + CONTACT + CV) ===")
    _info(f"Input:  {master_csv}")
    _info(f"Output: {enriched_csv}")

    enriched_rows: List[Dict[str, str]] = []
    total = len(df_in)

    # GPT-Slim mode: we keep Phase 2 demo-bounded to reduce evaluation volume.
    # This does not fabricate anything, it only limits how many rows we enrich.
    hard_cap_phase2 = 0
    if mode == "gpt_slim":
        hard_cap_phase2 = 50

    for idx, row in enumerate(df_in.to_dict(orient="records"), start=1):
        if hard_cap_phase2 and idx > hard_cap_phase2:
            break

        metrics["rows_processed"] += 1

        # module returns only updates; we merge
        updates = enrich_person_from_github_and_web(
            person_row=row,
            scenario=scenario,
            metrics=metrics,
            config=None,
        )

        merged = dict(row)
        merged.update({k: v for k, v in (updates or {}).items() if v is not None})

        enriched_rows.append(merged)

        if idx % 25 == 0 or idx == total or (hard_cap_phase2 and idx == hard_cap_phase2):
            _info(
                f"[Phase2] processed={metrics['rows_processed']} "
                f"github_ok={metrics['github_ok']} github_io={metrics['github_io']} "
                f"resume_cv_rows={metrics['resume_cv_rows']} email_rows={metrics['email_rows']} phone_rows={metrics['phone_rows']} "
                f"domains_crawled={metrics['domains_crawled']} repos_scanned={metrics['repos_scanned']}"
            )

    df_out = pd.DataFrame(enriched_rows)

    # Write CSV
    df_out.to_csv(enriched_csv, index=False)

    # Mandatory summary (accurate counters)
    _info("\n================ RUN_SAFE SUMMARY ================")
    _info(f"Pipeline version:        {PIPELINE_VERSION}")
    _info(f"Scenario:                {scenario}")
    _info(f"Mode:                    {mode}")
    _info(f"Output directory:        {out_dir}")
    _info(f"Master CSV:              {master_csv}")
    _info(f"Enriched CSV:            {enriched_csv}")
    _info(f"Rows processed (Phase2): {metrics['rows_processed']}")
    _info(f"github_ok:               {metrics['github_ok']}")
    _info(f"github_io:               {metrics['github_io']}")
    _info(f"resume_cv_rows:          {metrics['resume_cv_rows']}")
    _info(f"email_rows:              {metrics['email_rows']}")
    _info(f"phone_rows:              {metrics['phone_rows']}")
    _info(f"domains_crawled:         {metrics['domains_crawled']}")
    _info(f"repos_scanned:           {metrics['repos_scanned']}")
    _info("Truthful sparsity enforced: missing evidence remains blank.")
    _info("==================================================\n")

    return enriched_csv


def _run_gpt_slim_if_present(enriched_csv: Path, out_dir: Path) -> None:
    """
    Does not invent a GPT-Slim runner. Executes only if a known runner exists.
    """
    candidates = [
        Path("run_gpt_slim.py"),
        Path("gpt_slim_runner.py"),
        Path("EXECUTION_CORE") / "run_gpt_slim.py",
        Path("EXECUTION_CORE") / "gpt_slim_runner.py",
    ]
    runner = next((p for p in candidates if p.is_file()), None)
    if not runner:
        _warn("GPT-Slim runner not found (expected run_gpt_slim.py or gpt_slim_runner.py). Skipping GPT-Slim.")
        return

    out_path = out_dir / "gpt_slim_output.json"
    cmd = [sys.executable, str(runner), "--in", str(enriched_csv), "--out", str(out_path)]
    _info("\n=== GPT-SLIM RUN (OPTIONAL) ===")
    _info("Command: " + " ".join(cmd))
    rc = subprocess.call(cmd)
    if rc != 0:
        _die(f"GPT-Slim runner failed with exit code: {rc}")
    _info(f"GPT-Slim output: {out_path}")


def _build_arg_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="run_safe.py",
        description="Universal safe runner: Phase 1 inventory (repo root) + Phase 2 enrichment (EXECUTION_CORE), metrics, auto-open.",
    )
    p.add_argument("mode", choices=["demo", "scenario", "gpt_slim"], help="Run mode")
    p.add_argument("scenario", help="Scenario name, ex: frontier_ai_scientist")
    p.add_argument("--out-dir", default="", help="Output directory. If omitted, uses outputs/people/<scenario>_<MODE>_<UTCSTAMP>")
    p.add_argument("--detail-lookups", type=int, default=1, help="Pass-through to Phase 1 runner; 0 disables, 1 enables.")
    p.add_argument("--no-auto-open", action="store_true", help="Disable auto-opening the enriched CSV (macOS only).")
    return p


def main() -> None:
    args = _build_arg_parser().parse_args()

    mode = args.mode.strip().lower()
    scenario = args.scenario.strip()
    detail_lookups = int(args.detail_lookups)
    auto_open = not bool(args.no_auto_open)

    if not scenario:
        _die("Scenario cannot be empty.")

    out_dir = args.out_dir.strip()
    if out_dir:
        out_dir_path = Path(out_dir)
    else:
        out_dir_path = DEFAULT_OUT_BASE / f"{scenario}_{mode.upper()}_{_utc_stamp()}"

    out_dir_path.mkdir(parents=True, exist_ok=True)

    _info("\n=========================================================")
    _info("AI Talent Engine - RUN_SAFE (Canonical Orchestrator)")
    _info(f"Pipeline version: {PIPELINE_VERSION}")
    _info(f"Scenario:         {scenario}")
    _info(f"Mode:             {mode}")
    _info(f"Output dir:       {out_dir_path}")
    _info("=========================================================")

    # Phase 1
    master_csv = _run_phase1(mode=mode, scenario=scenario, out_dir=out_dir_path, detail_lookups=detail_lookups)

    # Phase 2
    enriched_csv = _phase2_enrich(master_csv=master_csv, scenario=scenario, out_dir=out_dir_path, mode=mode)

    # Auto-open enriched CSV (mandatory on macOS unless disabled)
    if auto_open:
        _mac_open(enriched_csv)

    # GPT-Slim optional run
    if mode == "gpt_slim":
        _run_gpt_slim_if_present(enriched_csv=enriched_csv, out_dir=out_dir_path)

    _info("DONE: Enriched CSV produced with accurate metrics and auto-open behavior.")


if __name__ == "__main__":
    main()
