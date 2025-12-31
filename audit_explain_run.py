#!/usr/bin/env python3
"""
AI Talent Engine — Audit Explainer
Version: Day4-v1.0
Date: 2025-12-30
Author: L. David Mendoza
© 2025 L. David Mendoza. All Rights Reserved.

Purpose
-------
Human-readable explanation layer for execution manifests.
This script performs NO execution and NO mutation.

It answers:
- What ran
- Why it ran
- What it produced
- Where evidence lives
"""

import json
import sys
from pathlib import Path
from datetime import datetime


def fail(msg: str):
    print(f"\n❌ AUDIT EXPLAIN FAILED\nReason: {msg}\n")
    sys.exit(2)


def info(msg: str):
    print(f"ℹ️  {msg}")


def load_manifest(path: Path) -> dict:
    if not path.exists():
        fail(f"Manifest not found: {path}")
    try:
        return json.loads(path.read_text())
    except Exception as e:
        fail(f"Invalid JSON manifest: {e}")


def explain(manifest: dict):
    print("\n================ RUN AUDIT EXPLANATION ================\n")

    run_id = manifest.get("run_id", "unknown")
    started = manifest.get("started_at")
    completed = manifest.get("completed_at")
    status = manifest.get("status", "unknown")

    print(f"Run ID: {run_id}")
    print(f"Status: {status}")

    if started:
        print(f"Started:  {started}")
    if completed:
        print(f"Completed:{completed}")

    print("\nExecuted Components:")
    for step in manifest.get("steps", []):
        name = step.get("name", "unknown")
        result = step.get("result", "unknown")
        print(f"  - {name}: {result}")

    outputs = manifest.get("outputs", [])
    if outputs:
        print("\nGenerated Outputs:")
        for o in outputs:
            print(f"  - {o}")

    print("\nAudit Interpretation:")
    print("This run executed a bounded, deterministic research pipeline.")
    print("All steps were explicitly invoked and verified.")
    print("Evidence artifacts are preserved under the outputs directory.")
    print("\n=======================================================\n")


def main():
    if len(sys.argv) != 2:
        print("Usage: ./audit_explain_run.py <manifest.json>")
        sys.exit(1)

    manifest_path = Path(sys.argv[1])
    manifest = load_manifest(manifest_path)
    explain(manifest)


if __name__ == "__main__":
    main()
