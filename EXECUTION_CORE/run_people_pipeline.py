"""
EXECUTION_CORE/run_people_pipeline.py
Gold pipeline orchestrator that outputs exactly one deliverable artifact to open.

Version: v5.0.0-deliverable-only
Author: Dave Mendoza
Copyright (c) 2025-2026 L. David Mendoza. All rights reserved.

Behavior:
- Runs stage chain
- Writes FULL and internal intermediates
- Writes DELIVERABLE.csv in exact Sample.xlsx schema
- Opens DELIVERABLE.csv only (macOS)

Validation:
- python3 -m py_compile EXECUTION_CORE/run_people_pipeline.py
- python3 -m EXECUTION_CORE.run_people_pipeline "AI infra" --debug

Git:
- git add EXECUTION_CORE/run_people_pipeline.py
- git commit -m "Fix: gold pipeline outputs deliverable-only CSV aligned to Sample.xlsx"
- git push
"""

from __future__ import annotations

import argparse
import os
import re
import sys
import time
import subprocess
from datetime import datetime
from typing import Optional, Dict

from EXECUTION_CORE.ai_role_registry import resolve_role, is_valid_role
from EXECUTION_CORE.phase4_seed_materializer import create_seed
from EXECUTION_CORE.people_source_github import run as stage_people_source
from EXECUTION_CORE.canonical_schema_mapper import run as stage_canonical_mapper
from EXECUTION_CORE.long_running_enrichment_pass import run as stage_long_enrich
from EXECUTION_CORE.citation_velocity_calculator import run as stage_citation_velocity
from EXECUTION_CORE.deep_inference_graph_pass import run as stage_graph
from EXECUTION_CORE.deliverable_writer import write_deliverable

PIPELINE_VERSION = "v5.0.0-deliverable-only"

_WS = re.compile(r"\s+")
_NON_ALNUM = re.compile(r"[^a-z0-9]+")


def _slug(s: str) -> str:
    s = (s or "").strip().lower()
    s = _NON_ALNUM.sub("_", s)
    s = _WS.sub("_", s)
    s = re.sub(r"_+", "_", s).strip("_")
    return s


def _call_stage(fn, src: str, dst: str) -> None:
    try:
        fn(src, dst)
    except TypeError:
        fn({"input_csv": src, "output_csv": dst})


def run_pipeline(role_input: str, debug: bool = False) -> Dict[str, str]:
    canonical = role_input.strip()
    if not is_valid_role(canonical):
        canonical = resolve_role(role_input)
    if not canonical or not is_valid_role(canonical):
        raise ValueError(f"Unknown role: {role_input}")

    role_slug = _slug(canonical)

    # Ensure seed exists for this role
    seed_res = create_seed(canonical, outputs_root="outputs", debug=debug)
    seed_csv = seed_res.seed_path

    outdir = os.path.join("outputs", "people", role_slug)
    os.makedirs(outdir, exist_ok=True)

    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    run_tag = f"{role_slug}.{stamp}"

    stage1 = os.path.join(outdir, f"{run_tag}.01_people_source.csv")
    stage2 = os.path.join(outdir, f"{run_tag}.02_canonical_sample81.csv")
    stage3 = os.path.join(outdir, f"{run_tag}.03_long_enriched.csv")
    stage4 = os.path.join(outdir, f"{run_tag}.04_citation_velocity.csv")
    stage5 = os.path.join(outdir, f"{run_tag}.05_graph_enriched.csv")

    full_out = os.path.join(outdir, f"{run_tag}.FULL.csv")

    deliverables_dir = os.path.join("outputs", "deliverables")
    os.makedirs(deliverables_dir, exist_ok=True)
    deliverable_out = os.path.join(deliverables_dir, f"{run_tag}.DELIVERABLE.csv")

    t0 = time.time()
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] PIPELINE START role={canonical} tag={run_tag} version={PIPELINE_VERSION}")

    _call_stage(stage_people_source, seed_csv, stage1)
    if debug:
        print("[debug] stage1 ok")

    _call_stage(stage_canonical_mapper, stage1, stage2)
    if debug:
        print("[debug] stage2 ok")

    _call_stage(stage_long_enrich, stage2, stage3)
    if debug:
        print("[debug] stage3 ok")

    _call_stage(stage_citation_velocity, stage3, stage4)
    if debug:
        print("[debug] stage4 ok")

    _call_stage(stage_graph, stage4, stage5)
    if debug:
        print("[debug] stage5 ok")

    # FULL is stage5
    with open(stage5, "r", encoding="utf-8-sig") as f_in:
        content = f_in.read()
    with open(full_out, "w", encoding="utf-8", newline="") as f_out:
        f_out.write(content)

    # DELIVERABLE
    write_deliverable(full_out, deliverable_out, pipeline_version=PIPELINE_VERSION)

    minutes = (time.time() - t0) / 60.0
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] COMPLETE runtime_min={minutes:.2f}")
    print(f"DELIVERABLE={os.path.abspath(deliverable_out)}")

    # Open deliverable only
    try:
        subprocess.run(["open", deliverable_out], check=False)
    except Exception:
        pass

    return {"deliverable_csv": os.path.abspath(deliverable_out), "full_csv": os.path.abspath(full_out)}


def _cli_main(argv: Optional[list[str]] = None) -> int:
    ap = argparse.ArgumentParser(description="Run gold pipeline and open deliverable.")
    ap.add_argument("role")
    ap.add_argument("--debug", action="store_true")
    args = ap.parse_args(argv)

    try:
        run_pipeline(args.role, debug=args.debug)
        return 0
    except Exception as e:
        print(f"🚫 Pipeline failed: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(_cli_main())
