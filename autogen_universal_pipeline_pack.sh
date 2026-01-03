#!/usr/bin/env bash
set -euo pipefail

# AI Talent Engine — Universal Pipeline Pack (Autogen)
# © 2025 L. David Mendoza
# Version: v1.0.0-universal-pack
#
# Purpose:
# - Hardwire canonical 82-column schema (JSON writer-of-record)
# - Provide one canonical run path for demo/scenario runs
# - Enforce deterministic artifact layout
# - Require GPT Slim evaluation output for any successful run
# - Provide child-proof terminal commands
#
# Non-negotiables:
# - Full-file generation only
# - Fail closed on missing schema/artifacts
# - No placeholder data

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$REPO_ROOT"

mkdir -p tools runners schemas outputs/manifests outputs/people outputs/leads

write_exec () {
  local path="$1"
  local tmp="${path}.tmp"
  mkdir -p "$(dirname "$path")"
  cat > "$tmp"
  mv "$tmp" "$path"
  chmod 755 "$path"
  echo "[WROTE+X] $path"
}

write_file () {
  local path="$1"
  local tmp="${path}.tmp"
  mkdir -p "$(dirname "$path")"
  cat > "$tmp"
  mv "$tmp" "$path"
  chmod 644 "$path"
  echo "[WROTE] $path"
}

# ------------------------------------------------------------
# 1) Canonical schema loader (82 columns)
# ------------------------------------------------------------
write_exec "tools/schema_loader.py" <<'PY'
#!/usr/bin/env python3
"""
AI Talent Engine — Canonical Schema Loader
© 2025 L. David Mendoza
Version: v1.0.0

Loads the locked canonical people schema from:
  schemas/canonical_people_schema_82.json

Fail-closed if missing or malformed.
"""

from __future__ import annotations
import json
import os
from typing import List, Dict, Any

SCHEMA_PATH = os.path.join("schemas", "canonical_people_schema_82.json")

class SchemaError(RuntimeError):
    pass

def load_schema() -> Dict[str, Any]:
    if not os.path.exists(SCHEMA_PATH):
        raise SchemaError(
            f"Canonical schema JSON missing: {SCHEMA_PATH}\n"
            "Action: run:\n"
            "  python3 tools/extract_canonical_schema_82.py"
        )
    with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    if data.get("count") != 82 or "columns" not in data:
        raise SchemaError(f"Canonical schema JSON invalid or wrong count: expected 82, got {data.get('count')}")

    cols = data["columns"]
    if not isinstance(cols, list) or len(cols) != 82:
        raise SchemaError("Canonical schema JSON 'columns' must be a list of length 82.")

    names = [c.get("name") for c in cols]
    if any((not isinstance(n, str) or not n.strip()) for n in names):
        raise SchemaError("Canonical schema column names must be non-empty strings.")
    if len(set(names)) != 82:
        raise SchemaError("Canonical schema contains duplicate column names.")

    return data

def canonical_column_names() -> List[str]:
    data = load_schema()
    return [c["name"] for c in data["columns"]]
PY

# ------------------------------------------------------------
# 2) Manifest writer
# ------------------------------------------------------------
write_exec "tools/manifest.py" <<'PY'
#!/usr/bin/env python3
"""
AI Talent Engine — Run Manifest Writer
© 2025 L. David Mendoza
Version: v1.0.0
"""

from __future__ import annotations
import hashlib
import json
import os
from datetime import datetime, timezone
from typing import Dict, Any

def _sha256_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()

def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")

def write_manifest(manifest_path: str, payload: Dict[str, Any]) -> None:
    os.makedirs(os.path.dirname(manifest_path), exist_ok=True)
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, sort_keys=True)

def build_manifest(run_id: str, scenario: str, mode: str, artifacts: Dict[str, str]) -> Dict[str, Any]:
    hashed = {}
    for k, p in artifacts.items():
        if p and os.path.exists(p):
            hashed[k] = {"path": p, "sha256": _sha256_file(p)}
        else:
            hashed[k] = {"path": p, "sha256": None}
    return {
        "run_id": run_id,
        "scenario": scenario,
        "mode": mode,
        "created_utc": utc_now(),
        "artifacts": hashed,
    }
PY

# ------------------------------------------------------------
# 3) GPT Slim stage (mandatory)
# ------------------------------------------------------------
write_exec "tools/gpt_slim_stage.py" <<'PY'
#!/usr/bin/env python3
"""
AI Talent Engine — GPT Slim Stage (Mandatory)
© 2025 L. David Mendoza
Version: v1.0.0

This module is intentionally fail-closed.

It produces:
- outputs/leads/run_<run_id>/gpt_slim_request.json
- outputs/leads/run_<run_id>/gpt_slim_result.json

If GPT Slim runner is not available, the run is NOT considered successful.
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

def run_gpt_slim(run_dir: str, scenario: str, leads_csv: str, schema_json: str) -> Dict[str, str]:
    req = os.path.join(run_dir, "gpt_slim_request.json")
    out = os.path.join(run_dir, "gpt_slim_result.json")

    request_obj = {
        "scenario": scenario,
        "leads_csv": leads_csv,
        "canonical_schema_json": schema_json,
        "required": True
    }
    write_json(req, request_obj)

    runner = "gpt_slim_runner.py"
    if not os.path.exists(runner):
        raise RuntimeError(
            "GPT Slim runner missing at repo root: gpt_slim_runner.py\n"
            "This stage is mandatory. Provide the runner or wire it into the repo."
        )

    cmd = ["python3", runner, "--request", req, "--out", out]
    p = subprocess.run(cmd, capture_output=True, text=True)
    if p.returncode != 0:
        raise RuntimeError("GPT Slim runner failed:\n" + p.stdout + "\n" + p.stderr)

    if not os.path.exists(out):
        raise RuntimeError("GPT Slim output missing after successful runner execution: " + out)

    return {"request": req, "result": out}
PY

# ------------------------------------------------------------
# 4) People scenario resolver (canonical schema enforcement)
# ------------------------------------------------------------
write_exec "people_scenario_resolver.py" <<'PY'
#!/usr/bin/env python3
"""
AI Talent Engine — People Scenario Resolver (Canonical, Schema-First)
© 2025 L. David Mendoza
Version: v1.0.0-universal

Guarantees:
- Always emits ALL canonical 82 columns in correct order
- Never emits fewer columns
- Demo mode bounds enforced by run_safe.py (25–50)
- Produces people_master.csv as canonical people artifact
"""

from __future__ import annotations

import os
import uuid
import pandas as pd
from typing import List, Dict

from tools.schema_loader import canonical_column_names

CANON_COLS = canonical_column_names()

def _new_run_id() -> str:
    return uuid.uuid4().hex[:12]

def generate_people_for_scenario(scenario: str, n: int) -> pd.DataFrame:
    # Deterministic placeholders are forbidden. We emit empty fields for unavailable public data.
    # This generator produces minimal rows; enrichment layers can populate later.
    rows: List[Dict[str, str]] = []
    for i in range(n):
        row = {c: "" for c in CANON_COLS}
        row["Person_ID"] = f"{scenario}_{i+1:04d}"
        row["Role_Type"] = scenario
        rows.append(row)
    return pd.DataFrame(rows, columns=CANON_COLS)

def write_people_master(df: pd.DataFrame, out_path: str) -> None:
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    df.to_csv(out_path, index=False)

def run_people(scenario: str, mode: str, outdir: str, min_rows: int, max_rows: int) -> str:
    if mode == "demo":
        n = max(min_rows, 25)
    else:
        n = max(min_rows, 25)

    n = min(n, max_rows)

    df = generate_people_for_scenario(scenario, n)

    if list(df.columns) != CANON_COLS:
        raise RuntimeError("Schema violation: people dataframe columns differ from canonical 82 spine.")

    out_path = os.path.join(outdir, "people_master.csv")
    write_people_master(df, out_path)
    return out_path
PY

# ------------------------------------------------------------
# 5) run_safe.py (single canonical pipeline)
# ------------------------------------------------------------
write_exec "run_safe.py" <<'PY'
#!/usr/bin/env python3
"""
AI Talent Engine — Safe Runner (Canonical, Single Path)
© 2025 L. David Mendoza
Version: v1.0.0-universal

One canonical pipeline for:
- demo <scenario>
- scenario <scenario>

Guarantees:
- Preflight duplicate guard must pass
- Canonical 82 schema must exist
- Deterministic artifact contract
- GPT Slim stage is mandatory for success
"""

from __future__ import annotations

import argparse
import os
import sys
import uuid
from datetime import datetime, timezone

from tools.schema_loader import load_schema
from tools.manifest import build_manifest, write_manifest
from tools.gpt_slim_stage import run_gpt_slim
from people_scenario_resolver import run_people

def utc_stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")

def new_run_id() -> str:
    return f"{utc_stamp()}_{uuid.uuid4().hex[:8]}"

def ensure_preflight_ok() -> None:
    # Must exist and be executable.
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
        max_rows=50 if mode == "demo" else 5000,
    )

    # Leads master is currently the same artifact as people_master until lead enrichment is wired.
    leads_master = os.path.join(leads_dir, f"LEADS_MASTER_{scenario}_{run_id}.csv")
    # Copy people_master to leads_master deterministically.
    import shutil
    shutil.copyfile(people_master, leads_master)

    slim = run_gpt_slim(
        run_dir=leads_dir,
        scenario=scenario,
        leads_csv=leads_master,
        schema_json=os.path.join("schemas", "canonical_people_schema_82.json"),
    )

    manifest = build_manifest(
        run_id=run_id,
        scenario=scenario,
        mode=mode,
        artifacts={
            "people_master_csv": people_master,
            "leads_master_csv": leads_master,
            "gpt_slim_request_json": slim["request"],
            "gpt_slim_result_json": slim["result"],
            "canonical_schema_json": os.path.join("schemas", "canonical_people_schema_82.json"),
        },
    )
    write_manifest(manifest_path, manifest)

    print("✅ RUN OK")
    print("people_master:", people_master)
    print("leads_master:", leads_master)
    print("manifest:", manifest_path)
    print("gpt_slim_result:", slim["result"])
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
PY

# ------------------------------------------------------------
# 6) Child-proof command launcher
# ------------------------------------------------------------
write_exec "start" <<'SH'
#!/usr/bin/env bash
set -euo pipefail
cd /Users/davemendoza/Desktop/Research_First_Sourcer_Automation

echo "🚀 AI Talent Engine ready"
echo "Commands:"
echo "  run demo frontier"
echo "  run demo ai_engineer"
echo "  run real frontier"
echo "  run dry frontier"
echo "  confirm last"

function run() {
  local mode="$1"
  local scenario="$2"
  if [[ "$mode" == "demo" ]]; then
    python3 run_safe.py "$scenario" --mode demo
  elif [[ "$mode" == "real" ]]; then
    python3 run_safe.py "$scenario" --mode real
  elif [[ "$mode" == "dry" ]]; then
    python3 run_safe.py "$scenario" --mode demo --dry-run
  else
    echo "Unknown mode: $mode"
    return 2
  fi
}

function confirm() {
  local last
  last="$(ls -t outputs/leads/run_*/gpt_slim_result.json 2>/dev/null | head -n 1 || true)"
  if [[ -z "$last" ]]; then
    echo "No GPT Slim results found."
    return 1
  fi
  echo "Last GPT Slim result:"
  echo "  $last"
}

export -f run
export -f confirm

echo "Type: run demo frontier"
SH

echo "============================================"
echo "Universal pipeline pack generated."
echo "Next commands (copy/paste):"
echo "  chmod +x autogen_universal_pipeline_pack.sh"
echo "  bash autogen_universal_pipeline_pack.sh"
echo "  python3 run_safe.py frontier --mode demo"
echo "============================================"
