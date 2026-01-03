#!/usr/bin/env python3
"""
AI Talent Engine — Safe Runner (Canonical, Real People, Single Path)
© 2025 L. David Mendoza
Version: v1.1.0-real-people

Pipeline:
- Preflight guard must pass
- Canonical schema (82) must exist
- Resolver pulls real people (GitHub) with GitHub.io emphasis
- Writes:
  - outputs/people/people_master.csv
  - outputs/leads/run_<run_id>/LEADS_MASTER_<scenario>_<run_id>.csv
  - outputs/leads/run_<run_id>/LEADS_SLIM_<scenario>_<run_id>.csv
  - outputs/leads/run_<run_id>/gpt_slim_request.json
  - outputs/leads/run_<run_id>/gpt_slim_result.json
  - outputs/manifests/run_manifest_<scenario>_<run_id>.json
"""

from __future__ import annotations

import argparse
import os
import shutil
import uuid
from datetime import datetime, timezone

from tools.schema_loader import load_schema
from tools.manifest import build_manifest, write_manifest
from tools.gpt_slim_stage import run_gpt_slim
from people_scenario_resolver import run_people
from slim_projector import write_slim

def utc_stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")

def new_run_id() -> str:
    return f"{utc_stamp()}_{uuid.uuid4().hex[:8]}"

def ensure_preflight_ok() -> None:
    if not os.path.exists("./preflight_duplicate_guard.py"):
        raise RuntimeError("Missing preflight guard: preflight_duplicate_guard.py")
    rc = os.system("./preflight_duplicate_guard.py")
    if rc != 0:
        raise RuntimeError("Preflight guard failed. Fix duplicates before running.")

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("scenario")
    ap.add_argument("--mode", choices=["demo", "real"], default="demo")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    ensure_preflight_ok()
    schema = load_schema()

    run_id = new_run_id()
    scenario = args.scenario
    mode = args.mode

    people_dir = os.path.join("outputs", "people")
    leads_dir = os.path.join("outputs", "leads", f"run_{run_id}")
    manifest_path = os.path.join("outputs", "manifests", f"run_manifest_{scenario}_{run_id}.json")

    os.makedirs(people_dir, exist_ok=True)
    os.makedirs(leads_dir, exist_ok=True)

    if args.dry_run:
        print("DRY-RUN OK")
        print("scenario:", scenario)
        print("mode:", mode)
        print("run_id:", run_id)
        print("canonical_schema_count:", schema.get("count"))
        return 0

    people_master = run_people(
        scenario=scenario,
        mode=mode,
        outdir=people_dir,
        min_rows=25,
        max_rows=50 if mode == "demo" else 5000
    )

    leads_master = os.path.join(leads_dir, f"LEADS_MASTER_{scenario}_{run_id}.csv")
    shutil.copyfile(people_master, leads_master)

    leads_slim = os.path.join(leads_dir, f"LEADS_SLIM_{scenario}_{run_id}.csv")
    write_slim(leads_master, leads_slim)

    slim = run_gpt_slim(
        run_dir=leads_dir,
        scenario=scenario,
        leads_csv=leads_master,
        slim_csv=leads_slim,
        schema_json=os.path.join("schemas", "canonical_people_schema_82.json")
    )

    manifest = build_manifest(
        run_id=run_id,
        scenario=scenario,
        mode=mode,
        artifacts={
            "people_master_csv": people_master,
            "leads_master_csv": leads_master,
            "leads_slim_csv": leads_slim,
            "gpt_slim_request_json": slim["request"],
            "gpt_slim_result_json": slim["result"],
            "canonical_schema_json": os.path.join("schemas", "canonical_people_schema_82.json"),
            "scenario_registry_json": "scenario_registry.json"
        }
    )
    write_manifest(manifest_path, manifest)

    print("✅ RUN OK")
    print("people_master:", people_master)
    print("leads_master:", leads_master)
    print("leads_slim:", leads_slim)
    print("manifest:", manifest_path)
    print("gpt_slim_result:", slim["result"])
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
