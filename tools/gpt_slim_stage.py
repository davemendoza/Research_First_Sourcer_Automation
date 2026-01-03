#!/usr/bin/env python3
"""
AI Talent Engine — GPT Slim Stage (Mandatory)
© 2025 L. David Mendoza
Version: v1.1.0-slim-csv

Produces:
- outputs/leads/run_<run_id>/gpt_slim_request.json
- outputs/leads/run_<run_id>/gpt_slim_result.json

Fail-closed if runner missing or output missing.
"""

from __future__ import annotations
import json
import os
import subprocess
from typing import Dict, Any

def write_json(path: str, obj: Dict[str, Any]) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2, sort_keys=True)

def run_gpt_slim(run_dir: str, scenario: str, leads_csv: str, slim_csv: str, schema_json: str) -> Dict[str, str]:
    req = os.path.join(run_dir, "gpt_slim_request.json")
    out = os.path.join(run_dir, "gpt_slim_result.json")

    request_obj = {
        "scenario": scenario,
        "leads_csv": leads_csv,
        "slim_csv": slim_csv,
        "canonical_schema_json": schema_json,
        "required": True
    }
    write_json(req, request_obj)

    runner = "gpt_slim_runner.py"
    if not os.path.exists(runner):
        raise RuntimeError(
            "GPT Slim runner missing at repo root: gpt_slim_runner.py\n"
            "This stage is mandatory."
        )

    cmd = ["python3", runner, "--request", req, "--out", out]
    p = subprocess.run(cmd, capture_output=True, text=True)
    if p.returncode != 0:
        raise RuntimeError("GPT Slim runner failed:\n" + p.stdout + "\n" + p.stderr)

    if not os.path.exists(out):
        raise RuntimeError("GPT Slim output missing after successful runner execution: " + out)

    return {"request": req, "result": out}
