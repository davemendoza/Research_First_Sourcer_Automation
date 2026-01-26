#!/usr/bin/env python3
# ============================================================
#  Research_First_Sourcer_Automation
#  File: EXECUTION_CORE/run_safe.py
#
#  Purpose:
#    Single authoritative execution surface for Gold people runs.
#    Guarantees:
#      - SEED exists (auto-create if missing, NO Person_ID)
#      - Runs pipeline stages in order
#      - Live progress preview: rows + contact/url counts + ETA
#      - Writes FULL / GPT_SLIM / PREVIEW
#      - Opens output folder and PREVIEW CSV (macOS) so files "pop out"
#      - Optional completion email when SMTP env vars are configured
#
#  Command (authoritative):
#    python3 -m EXECUTION_CORE.run_safe <ROLE> [--debug] [--no-open]
#
#  Version: v1.0.0-run-safe-spine
#  Author: Dave Mendoza
#  Copyright (c) 2025-2026 L. David Mendoza. All rights reserved.
#
#  Changelog:
#    v1.0.0 - Permanent run spine. No silent exits. No ad hoc pandas.
#
#  Validation:
#    python3 -m py_compile EXECUTION_CORE/run_safe.py
#    python3 -m EXECUTION_CORE.run_safe Frontier_AI_Scientist --debug
#
#  Git:
#    git add EXECUTION_CORE/run_safe.py
#    git commit -m "Run: add permanent run_safe spine (seed + pipeline + progress + outputs)"
#    git push
# ============================================================

from __future__ import annotations

import argparse
import csv
import os
import sys
import time
import subprocess
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

from EXECUTION_CORE.phase4_seed_materializer import create_seed_from_demo
from EXECUTION_CORE.people_source_github import run as stage_people_source
from EXECUTION_CORE.canonical_schema_mapper import run as stage_canonical_mapper
from EXECUTION_CORE.long_running_enrichment_pass import run as stage_long_enrich
from EXECUTION_CORE.citation_velocity_calculator import run as stage_citation_velocity
from EXECUTION_CORE.deep_inference_graph_pass import run as stage_graph


PIPELINE_VERSION = "v1.0.0-run-safe-spine"

# Live preview counters
EMAIL_KEYS = ("Email", "Primary_Email", "Work_Email", "Home_Email")
PHONE_KEYS = ("Phone", "Primary_Phone", "Mobile_Phone")
GITHUB_KEYS = ("Github_URL", "GitHub_Profile_URL", "GitHub_URL", "GitHub")
GITHUB_IO_KEYS = ("Github_IO_URL", "GitHub_IO_URL", "GithubIO_URL", "GitHubIO_URL")
CV_KEYS = ("Resume_Link", "CV_Link", "Resume_URL", "CV_URL", "Resume", "CV")

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


def _now() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def _read_rows_with_cols(path: str) -> Tuple[List[Dict[str, str]], List[str]]:
    with open(path, "r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        cols = list(reader.fieldnames or [])
        rows: List[Dict[str, str]] = []
        for row in reader:
            if row and any((v or "").strip() for v in row.values()):
                rows.append({k: (v if v is not None else "") for k, v in row.items()})
        return rows, cols


def _count_nonempty(rows: List[Dict[str, str]], keys: Tuple[str, ...]) -> int:
    n = 0
    for r in rows:
        for k in keys:
            v = (r.get(k) or "").strip()
            if v:
                n += 1
                break
    return n


def _preview_counts(csv_path: str) -> Dict[str, int]:
    if not os.path.exists(csv_path):
        return {"rows": 0, "emails": 0, "phones": 0, "github": 0, "github_io": 0, "cvs": 0}
    rows, _ = _read_rows_with_cols(csv_path)
    return {
        "rows": len(rows),
        "emails": _count_nonempty(rows, EMAIL_KEYS),
        "phones": _count_nonempty(rows, PHONE_KEYS),
        "github": _count_nonempty(rows, GITHUB_KEYS),
        "github_io": _count_nonempty(rows, GITHUB_IO_KEYS),
        "cvs": _count_nonempty(rows, CV_KEYS),
    }


def _fmt(sec: float) -> str:
    sec = max(0.0, sec)
    m = int(sec // 60)
    s = int(sec % 60)
    return f"{m:02d}:{s:02d}"


def _log_stage(stage_name: str, csv_path: str, t0: float, stage_idx: int, stage_total: int) -> None:
    counts = _preview_counts(csv_path)
    elapsed = time.time() - t0
    avg_stage = elapsed / max(1, stage_idx)
    remaining = max(0, stage_total - stage_idx)
    eta = avg_stage * remaining
    print(
        f"[{_now()}] ✅ stage={stage_name} "
        f"people={counts['rows']} emails={counts['emails']} phones={counts['phones']} "
        f"github={counts['github']} github_io={counts['github_io']} cvs={counts['cvs']} "
        f"elapsed={_fmt(elapsed)} eta={_fmt(eta)}"
    )


def _call_stage(stage_fn, input_csv: str, output_csv: str) -> None:
    """
    Supports both stage signatures:
      - stage(input_csv, output_csv)
      - stage(context_dict)
    """
    try:
        stage_fn(input_csv, output_csv)
        return
    except TypeError:
        pass

    ctx: Dict[str, Any] = {"input_csv": input_csv, "output_csv": output_csv}
    stage_fn(ctx)


def _copy_csv(src: str, dst: str) -> None:
    with open(src, "r", encoding="utf-8-sig", newline="") as f_in:
        content = f_in.read()
    os.makedirs(os.path.dirname(dst) or ".", exist_ok=True)
    with open(dst, "w", encoding="utf-8", newline="") as f_out:
        f_out.write(content)


def _write_slim(full_csv: str, out_csv: str, cols: List[str]) -> None:
    rows, _ = _read_rows_with_cols(full_csv)
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


def _require_people(full_csv: str) -> None:
    rows, _ = _read_rows_with_cols(full_csv)
    if len(rows) <= 0:
        raise RuntimeError("🚫 INVALID RUN: FULL CSV contains 0 people rows. Aborting as non-negotiable.")


def _send_completion_email(subject: str, body: str) -> None:
    """
    Sends email only if env vars are present:
      SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASS, NOTIFY_EMAIL_TO
    """
    host = os.getenv("SMTP_HOST", "").strip()
    port = int(os.getenv("SMTP_PORT", "587").strip() or "587")
    user = os.getenv("SMTP_USER", "").strip()
    pw = os.getenv("SMTP_PASS", "").strip()
    to_addr = os.getenv("NOTIFY_EMAIL_TO", "").strip()
    from_addr = os.getenv("NOTIFY_EMAIL_FROM", user).strip() or user

    if not (host and user and pw and to_addr and from_addr):
        return

    import smtplib
    from email.message import EmailMessage

    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = from_addr
    msg["To"] = to_addr
    msg.set_content(body)

    with smtplib.SMTP(host, port, timeout=30) as s:
        s.starttls()
        s.login(user, pw)
        s.send_message(msg)


def _open_artifacts(output_dir: str, preview_csv: str, no_open: bool) -> None:
    if no_open:
        return
    # macOS Finder open
    try:
        subprocess.run(["open", output_dir], check=False)
        if os.path.exists(preview_csv):
            subprocess.run(["open", preview_csv], check=False)
    except Exception:
        # never fail the run due to Finder
        pass


def _seed_path_for_role(role: str) -> str:
    return os.path.join("outputs", "seed", f"{role}.seed.csv")


def _ensure_seed(role: str, debug: bool) -> str:
    seed = _seed_path_for_role(role)
    if os.path.exists(seed):
        if debug:
            print(f"[{_now()}] [seed] exists: {seed}")
        return seed

    # Auto-create seed from demo people source
    res = create_seed_from_demo(role, outputs_root="outputs", debug=debug)
    if res.rows_written <= 0:
        raise RuntimeError(f"🚫 SEED CREATED BUT EMPTY: {res.seed_path}")
    return res.seed_path


def run_gold(role: str, debug: bool = False, no_open: bool = False) -> Dict[str, str]:
    role = role.strip()
    if not role:
        raise ValueError("role is required")

    seed_csv = _ensure_seed(role, debug=debug)

    # Output layout: outputs/people/<ROLE>/
    output_dir = os.path.join("outputs", "people", role)
    os.makedirs(output_dir, exist_ok=True)

    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    run_tag = f"demo_{role}.{stamp}"

    # Stage file names (deterministic per run_tag)
    stage1 = os.path.join(output_dir, f"{run_tag}.01_people_source.csv")
    stage2 = os.path.join(output_dir, f"{run_tag}.02_canonical_sample81.csv")
    stage3 = os.path.join(output_dir, f"{run_tag}.03_long_enriched.csv")
    stage4 = os.path.join(output_dir, f"{run_tag}.04_citation_velocity.csv")
    stage5 = os.path.join(output_dir, f"{run_tag}.05_graph_enriched.csv")

    full_out = os.path.join(output_dir, f"{run_tag}.FULL.csv")
    slim_out = os.path.join(output_dir, f"{run_tag}.GPT_SLIM.csv")
    preview_out = os.path.join(output_dir, f"{run_tag}.PREVIEW.csv")

    stages = [
        ("people_source_github", stage_people_source, seed_csv, stage1),
        ("canonical_schema_mapper", stage_canonical_mapper, stage1, stage2),
        ("long_running_enrichment_pass", stage_long_enrich, stage2, stage3),
        ("citation_velocity_calculator", stage_citation_velocity, stage3, stage4),
        ("deep_inference_graph_pass", stage_graph, stage4, stage5),
    ]

    t0 = time.time()
    print(f"[{_now()}] 🚀 RUN_SAFE started version={PIPELINE_VERSION}")
    print(f"[{_now()}] role={role}")
    print(f"[{_now()}] seed={os.path.abspath(seed_csv)}")
    print(f"[{_now()}] outdir={os.path.abspath(output_dir)}")

    for i, (name, fn, in_csv, out_csv) in enumerate(stages, start=1):
        print(f"[{_now()}] ▶️  stage {i}/{len(stages)} starting: {name}")
        _call_stage(fn, in_csv, out_csv)
        _log_stage(name, out_csv, t0, i, len(stages))

    _copy_csv(stage5, full_out)
    _write_slim(full_out, slim_out, GPT_SLIM_COLUMNS)
    _write_preview(full_out, preview_out, 25)
    _require_people(full_out)

    counts = _preview_counts(full_out)
    minutes = (time.time() - t0) / 60.0

    print(f"[{_now()}] 🏁 RUN COMPLETE")
    print(f"[{_now()}] FULL={os.path.abspath(full_out)}")
    print(f"[{_now()}] GPT_SLIM={os.path.abspath(slim_out)}")
    print(f"[{_now()}] PREVIEW={os.path.abspath(preview_out)}")
    print(
        f"[{_now()}] SUMMARY people={counts['rows']} emails={counts['emails']} phones={counts['phones']} "
        f"github={counts['github']} github_io={counts['github_io']} cvs={counts['cvs']} runtime_min={minutes:.2f}"
    )

    subj = f"AI Talent Engine run complete: {run_tag} ({counts['rows']} people)"
    body = "\n".join(
        [
            f"Role: {role}",
            f"Run tag: {run_tag}",
            f"Version: {PIPELINE_VERSION}",
            f"People rows: {counts['rows']}",
            f"Emails: {counts['emails']}",
            f"Phones: {counts['phones']}",
            f"GitHub: {counts['github']}",
            f"GitHub.io: {counts['github_io']}",
            f"CVs: {counts['cvs']}",
            f"Runtime (min): {minutes:.2f}",
            "",
            f"FULL CSV: {os.path.abspath(full_out)}",
            f"GPT-SLIM CSV: {os.path.abspath(slim_out)}",
            f"PREVIEW CSV: {os.path.abspath(preview_out)}",
        ]
    )
    _send_completion_email(subj, body)

    _open_artifacts(output_dir, preview_out, no_open=no_open)

    return {
        "role": role,
        "seed_csv": os.path.abspath(seed_csv),
        "output_dir": os.path.abspath(output_dir),
        "full_csv": os.path.abspath(full_out),
        "gpt_slim_csv": os.path.abspath(slim_out),
        "preview_csv": os.path.abspath(preview_out),
        "runtime_minutes": f"{minutes:.2f}",
    }


def _cli_main(argv: Optional[List[str]] = None) -> int:
    ap = argparse.ArgumentParser(description="Run SAFE Gold pipeline (seed + stages + outputs).")
    ap.add_argument("role", help="Role, e.g. Frontier_AI_Scientist")
    ap.add_argument("--debug", action="store_true", help="Verbose logging")
    ap.add_argument("--no-open", action="store_true", help="Do not open Finder / files on completion")
    args = ap.parse_args(argv)

    try:
        run_gold(args.role, debug=args.debug, no_open=args.no_open)
        return 0
    except Exception as e:
        print(f"🚫 RUN FAILED: {e}", file=sys.stderr)
        return 1


def main() -> None:
    raise SystemExit(_cli_main())


if __name__ == "__main__":
    main()
