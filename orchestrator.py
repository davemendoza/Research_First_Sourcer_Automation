#!/usr/bin/env python3
"""
AI Talent Engine — Orchestrator
- Resolves plain-English role intent
- Runs pipeline
- Auto-opens demo results
- Emails on long runs
- Always emits GPT-SLIM
"""

import sys
import subprocess
import shutil
from pathlib import Path

ROLE_INPUT = " ".join(sys.argv[1:]).lower()

# ------------------------------------------------------------
# ROLE RESOLUTION (LOCKED)
# ------------------------------------------------------------
ROLE_MAP = {
    "frontier": "frontier",
    "research": "frontier",
    "foundational": "frontier",
    "alignment": "alignment_researcher",
    "rlhf": "rlhf_researcher",

    "ai infra": "ai_infra",
    "gpu infra": "ai_infra",
    "platform": "ai_infra",
    "distributed": "distributed_systems_engineer",

    "inference": "llm_inference_engineer",
    "llm inference": "llm_inference_engineer",
    "tensorrt": "llm_inference_engineer",
    "vllm": "llm_inference_engineer",

    "mlops": "mlops_engineer",
    "llmops": "mlops_engineer",

    "ai engineer": "ai_engineer",
    "genai": "genai_engineer",

    "applied ml": "applied_ml",
    "data scientist": "data_scientist_ai",

    "devrel": "developer_relations",
    "developer relations": "developer_relations",
}

resolved_role = None
for k, v in ROLE_MAP.items():
    if k in ROLE_INPUT:
        resolved_role = v
        break

if not resolved_role:
    print(f"ERROR: Could not resolve role from input: '{ROLE_INPUT}'")
    sys.exit(1)

print(f"Resolved role → {resolved_role}")

# ------------------------------------------------------------
# RUN PIPELINE
# ------------------------------------------------------------
print("Running pipeline…")
subprocess.run(["python3", "run_demo.py", resolved_role], check=True)

# ------------------------------------------------------------
# FIND FINAL ARTIFACT
# ------------------------------------------------------------
demo_dir = Path("outputs/demo")
final_csvs = sorted(
    demo_dir.glob("*FINAL*.csv"),
    key=lambda p: p.stat().st_mtime,
    reverse=True
)

if not final_csvs:
    print("ERROR: No FINAL CSV found.")
    sys.exit(1)

final_csv = final_csvs[0]
print(f"Final artifact: {final_csv}")

# ------------------------------------------------------------
# GPT-SLIM (ALWAYS)
# ------------------------------------------------------------
print("Generating GPT-SLIM…")
subprocess.run(["python3", "run_gpt_slim.py"], check=True)

# ------------------------------------------------------------
# MODE DECISION
# ------------------------------------------------------------
interactive = sys.stdout.isatty()

if interactive:
    print("Interactive run detected — opening results")
    subprocess.run(["open", str(final_csv)], check=False)
else:
    print("Non-interactive run — sending completion email")
    subprocess.run(["python3", "notify_run_complete.py", resolved_role], check=False)
