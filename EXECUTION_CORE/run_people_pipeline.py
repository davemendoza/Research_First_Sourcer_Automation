# ============================================================
#  Research_First_Sourcer_Automation
#  File: EXECUTION_CORE/run_people_pipeline.py
#
#  Purpose:
#    Deterministic people CSV pipeline orchestrator (gold standard mode).
#    Runs staged transforms:
#      1) people_source_github
#      2) canonical_schema_mapper (Sample81)
#      3) long_running_enrichment_pass
#      4) citation_velocity_calculator
#      5) deep_inference_graph_pass
#    Emits full output + GPT-Slim + preview.
#
#  Contract:
#    main callable: run_pipeline(input_csv: str, output_dir: str, run_tag: str) -> Dict[str, str]
#
#  Version: v4.2.0-gold-orchestrator
#  Author: Dave Mendoza
# ============================================================

from __future__ import annotations

import csv
import os
import time
from typing import Dict, List

from EXECUTION_CORE.people_source_github import run as stage_people_source
from EXECUTION_CORE.canonical_schema_mapper import run as stage_canonical_mapper
from EXECUTION_CORE.long_running_enrichment_pass import run as stage_long_enrich
from EXECUTION_CORE.citation_velocity_calculator import run as stage_citation_velocity
from EXECUTION_CORE.deep_inference_graph_pass import run as stage_graph

PIPELINE_VERSION = "v4.2.0-gold-orchestrator"

GPT_SLIM_COLUMNS = [
    "Full_Name",
    "AI_Role_Type",
    "Current_Title",
    "Current_Company",
    "Location_City",
    "Location_State",
    "Location_Country",
    "Primary_Email",
    "Primary_Phone",
    "GitHub_Username",
    "GitHub_Profile_URL",
    "Repo_Evidence_URLs",
    "Repo_Topics_Keywords",
    "Primary_Model_Families",
    "Determinative_Skill_Areas",
    "Benchmarks_Worked_On",
    "Citations_per_Year",
    "Citation_Velocity_3yr",
    "Citation_Velocity_5yr",
    "Hiring_Recommendation",
    "Strengths",
    "Weaknesses",
    "Field_Level_Provenance_JSON",
]

def run_pipeline(input_csv: str, output_dir: str, run_tag: str) -> Dict[str, str]:
    os.makedirs(output_dir, exist_ok=True)

    # Deterministic file names
    stage1 = os.path.join(output_dir, f"{run_tag}.01_people_source.csv")
    stage2 = os.path.join(output_dir, f"{run_tag}.02_canonical_sample81.csv")
    stage3 = os.path.join(output_dir, f"{run_tag}.03_long_enriched.csv")
    stage4 = os.path.join(output_dir, f"{run_tag}.04_citation_velocity.csv")
    stage5 = os.path.join(output_dir, f"{run_tag}.05_graph_enriched.csv")

    full_out = os.path.join(output_dir, f"{run_tag}.FULL.csv")
    slim_out = os.path.join(output_dir, f"{run_tag}.GPT_SLIM.csv")
    preview_out = os.path.join(output_dir, f"{run_tag}.PREVIEW.csv")

    t0 = time.time()

    stage_people_source(input_csv, stage1)
    stage_canonical_mapper(stage1, stage2)
    stage_long_enrich(stage2, stage3)
    stage_citation_velocity(stage3, stage4)
    stage_graph(stage4, stage5)

    # Finalize FULL = stage5 (also stamp Output_File_Path inside mapper already)
    _copy_csv(stage5, full_out)

    # Emit GPT-Slim and preview
    _write_slim(full_out, slim_out, GPT_SLIM_COLUMNS)
    _write_preview(full_out, preview_out, 25)

    minutes = (time.time() - t0) / 60.0
    return {
        "pipeline_version": PIPELINE_VERSION,
        "full_csv": os.path.abspath(full_out),
        "gpt_slim_csv": os.path.abspath(slim_out),
        "preview_csv": os.path.abspath(preview_out),
        "runtime_minutes": f"{minutes:.2f}",
    }

def _copy_csv(src: str, dst: str) -> None:
    # Pure CSV copy, deterministic
    with open(src, "r", encoding="utf-8-sig", newline="") as f_in:
        content = f_in.read()
    with open(dst, "w", encoding="utf-8", newline="") as f_out:
        f_out.write(content)

def _write_slim(full_csv: str, out_csv: str, cols: List[str]) -> None:
    rows = _read_rows(full_csv)
    os.makedirs(os.path.dirname(out_csv) or ".", exist_ok=True)
    with open(out_csv, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols, extrasaction="ignore")
        w.writeheader()
        for r in rows:
            w.writerow({c: ("" if r.get(c) is None else str(r.get(c, ""))) for c in cols})

def _write_preview(full_csv: str, out_csv: str, n: int) -> None:
    rows, cols = _read_rows_with_cols(full_csv)
    os.makedirs(os.path.dirname(out_csv) or ".", exist_ok=True)
    with open(out_csv, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols, extrasaction="ignore")
        w.writeheader()
        for r in rows[:n]:
            w.writerow({c: ("" if r.get(c) is None else str(r.get(c, ""))) for c in cols})

def _read_rows(path: str) -> List[Dict[str, str]]:
    rows, _ = _read_rows_with_cols(path)
    return rows

def _read_rows_with_cols(path: str):
    with open(path, "r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        cols = list(reader.fieldnames or [])
        rows: List[Dict[str, str]] = []
        for row in reader:
            if row and any((v or "").strip() for v in row.values()):
                rows.append({k: (v if v is not None else "") for k, v in row.items()})
        return rows, cols
