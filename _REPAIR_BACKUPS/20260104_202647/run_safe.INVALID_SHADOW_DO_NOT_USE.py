#!/usr/bin/env python3
"""
AI Talent Engine – Safe Demo Runner (Hardened, Non-Coupled)
© 2025 L. David Mendoza

Purpose:
- Run scenarios safely without importing brittle internals
- Enforce schema lock indirectly
- Write execution manifest
"""

import sys
import subprocess
from pathlib import Path

from manifest_writer import write_manifest


def main():
    if len(sys.argv) != 2:
        sys.exit("USAGE: python3 run_safe.py <scenario>")

    scenario = sys.argv[1]

    # Run scenario as a subprocess (NO IMPORT COUPLING)
    cmd = [
        sys.executable,
        "people_scenario_resolver.py",
        "--scenario",
        scenario,
    ]

    print(f"▶️ Running scenario: {scenario}")
    result = subprocess.run(cmd)

    if result.returncode != 0:
        sys.exit(f"❌ Scenario failed with exit code {result.returncode}")

    # Manifest path
    manifest_path = Path("outputs") / "manifest.json"
    manifest_path.parent.mkdir(parents=True, exist_ok=True)

    # Manifest payload
    manifest_payload = {
        "scenario": scenario,
        "status": "completed",
        "runner": "run_safe.py",
    }

    write_manifest(manifest_path, manifest_payload)

    print("✅ DEMO RUN COMPLETE")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
