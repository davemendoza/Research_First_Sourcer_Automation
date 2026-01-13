#!/usr/bin/env python3
"""
run_safe.py
---------------------------------------
Purpose:
Safely orchestrate a full people pipeline run for a single scenario.

Order of operations (LOCKED):
1. Scenario resolution
2. Upstream input contract check (people_enriched.csv must exist)
3. Name resolution pass (CACHE-SAFE SKIP when upstream unchanged)
4. Canonical schema mapping
5. Phase 6: AI stack signal extraction
6. Phase 7: OSS contribution intelligence
7. Canonical CSV writing (writer of record)
8. Terminal preview (best-effort)

This file performs NO enrichment logic itself.
"""

import subprocess
import sys
from pathlib import Path

# ---- SHADOW EXECUTION GUARDRAIL (DO NOT REMOVE) ----
_THIS_FILE = Path(__file__).resolve()
if _THIS_FILE.parent.name != "EXECUTION_CORE":
    print("❌ FATAL: Shadow run_safe.py invoked (wrong location).", file=sys.stderr)
    print(f"Running: {_THIS_FILE}", file=sys.stderr)
    print("Expected location: <repo>/EXECUTION_CORE/run_safe.py", file=sys.stderr)
    print("Fix: remove/rename duplicate run_safe.py files.", file=sys.stderr)
    sys.exit(1)
# ---------------------------------------------------

ROOT = Path(__file__).resolve().parents[1]
EXEC = ROOT / "EXECUTION_CORE"

# Core pipeline components (paths are authoritative)
SCENARIO_RESOLVER = EXEC / "people_scenario_resolver.py"
NAME_PASS = EXEC / "name_resolution_pass.py"
SCHEMA_MAPPER = EXEC / "canonical_schema_mapper.py"
PHASE6 = EXEC / "phase6_ai_stack_signals.py"
PHASE7 = EXEC / "phase7_oss_contribution_intel.py"
WRITER = EXEC / "canonical_people_writer.py"
PREVIEW = EXEC / "talent_intel_preview.py"

# Artifact contract
UPSTREAM = ROOT / "people_enriched.csv"

# Working artifacts (single-run, deterministic)
NAMED = ROOT / "people_named.csv"
MAPPED = ROOT / "people_mapped.csv"
PHASE6_OUT = ROOT / "people_phase6.csv"
PHASE7_OUT = ROOT / "people_phase7.csv"


def run(cmd, label):
    print(f"\n▶ {label}")
    result = subprocess.run(cmd, text=True)
    if result.returncode != 0:
        print(f"✖ FAILED: {label}", file=sys.stderr)
        sys.exit(1)


def require_file(path: Path, label: str):
    if not path.exists():
        print(f"❌ Missing required file: {label}: {path}", file=sys.stderr)
        sys.exit(1)


def should_skip_name_resolution(upstream_csv: Path, named_csv: Path) -> bool:
    """
    Cache-safe skip rule (demo-speed, correctness-preserving):

    Skip Name Resolution only if:
    - named_csv exists, AND
    - named_csv is newer than upstream_csv

    This guarantees that if upstream changes (new data, new evidence),
    Name Resolution runs again automatically.

    No flags. No assumptions. Deterministic.
    """
    if not named_csv.exists():
        return False
    try:
        return named_csv.stat().st_mtime >= upstream_csv.stat().st_mtime
    except OSError:
        return False


def main():
    if len(sys.argv) != 2:
        print("Usage: run_safe.py <scenario_name>", file=sys.stderr)
        sys.exit(1)

    scenario = sys.argv[1]

    # 1. Scenario resolution
    require_file(SCENARIO_RESOLVER, "Scenario resolver")
    proc = subprocess.run(
        ["python3", str(SCENARIO_RESOLVER), scenario],
        capture_output=True,
        text=True,
    )
    if proc.returncode != 0:
        print(proc.stderr, file=sys.stderr)
        sys.exit(1)

    resolved = {}
    for line in proc.stdout.splitlines():
        if "=" in line:
            k, v = line.split("=", 1)
            resolved[k.strip()] = v.strip()

    if "SCENARIO_PREFIX" not in resolved:
        print("❌ Scenario resolver did not emit SCENARIO_PREFIX", file=sys.stderr)
        sys.exit(1)

    prefix = resolved["SCENARIO_PREFIX"]

    # 2. Upstream input contract check
    if not UPSTREAM.exists():
        print("❌ Missing required upstream input: people_enriched.csv", file=sys.stderr)
        sys.exit(1)

    # 3. Name resolution pass (cache-safe skip)
    require_file(NAME_PASS, "Name resolution pass")
    if should_skip_name_resolution(UPSTREAM, NAMED):
        print("\n⚡ Skipping Name Resolution Pass (cached, upstream unchanged)")
        tmp_named = NAMED
    else:
        tmp_named = NAMED
        run(
            ["python3", str(NAME_PASS), str(UPSTREAM), str(tmp_named)],
            "Name Resolution Pass",
        )

    # 4. Canonical schema mapping
    require_file(SCHEMA_MAPPER, "Canonical schema mapper")
    run(
        ["python3", str(SCHEMA_MAPPER), str(tmp_named), str(MAPPED)],
        "Canonical Schema Mapping",
    )

    # 5. Phase 6
    require_file(PHASE6, "Phase 6")
    run(
        ["python3", str(PHASE6), str(MAPPED), str(PHASE6_OUT)],
        "Phase 6: AI Stack Signal Extraction",
    )

    # 6. Phase 7
    require_file(PHASE7, "Phase 7")
    run(
        ["python3", str(PHASE7), str(PHASE6_OUT), str(PHASE7_OUT)],
        "Phase 7: OSS Contribution Intelligence",
    )

    # 7. Canonical CSV writer (writer of record)
    require_file(WRITER, "Canonical people writer")
    output_dir = ROOT / "outputs"
    run(
        ["python3", str(WRITER), str(PHASE7_OUT), str(output_dir), prefix],
        "Canonical CSV Writer",
    )

    # 8. Terminal preview (best-effort)
    if PREVIEW.exists():
        run(
            ["python3", str(PREVIEW), str(PHASE7_OUT)],
            "Talent Intelligence Preview",
        )

    print("\n✔ PIPELINE COMPLETE (Phase 6 & 7 WIRED)")


if __name__ == "__main__":
    main()
