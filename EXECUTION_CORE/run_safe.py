#!/usr/bin/env python3
"""
run_safe.py
====================================================
SINGLE AUTHORITATIVE PIPELINE ENTRYPOINT (LOCKED)

Responsibilities:
- Orchestrate exactly ONE people pipeline execution
- Write exactly ONE canonical CSV
- Invoke preview exactly ONCE (best-effort)
- NEVER recurse
- NEVER re-enter itself
- NEVER write multiple CSVs per run

This file is the WRITER OF RECORD.
All shell / demo / scenario paths must call THIS file only.

If this file misbehaves, the system is broken.
"""

import sys
import subprocess
from pathlib import Path

# ------------------------------------------------------------------
# HARD SHADOW GUARD (ABSOLUTE)
# ------------------------------------------------------------------
THIS_FILE = Path(__file__).resolve()
if THIS_FILE.parent.name != "EXECUTION_CORE":
    print("❌ FATAL: Shadow run_safe.py executed", file=sys.stderr)
    print(f"Found at: {THIS_FILE}", file=sys.stderr)
    print("Expected: <repo>/EXECUTION_CORE/run_safe.py", file=sys.stderr)
    sys.exit(1)

# ------------------------------------------------------------------
# ROOTS
# ------------------------------------------------------------------
REPO_ROOT = THIS_FILE.parents[1]
EXEC = REPO_ROOT / "EXECUTION_CORE"
OUTPUTS = REPO_ROOT / "outputs"

# ------------------------------------------------------------------
# PIPELINE COMPONENTS (AUTHORITATIVE)
# ------------------------------------------------------------------
SCENARIO_RESOLVER = EXEC / "people_scenario_resolver.py"
NAME_PASS = EXEC / "name_resolution_pass.py"
SCHEMA_MAPPER = EXEC / "canonical_schema_mapper.py"
PHASE6 = EXEC / "phase6_ai_stack_signals.py"
PHASE7 = EXEC / "phase7_oss_contribution_intel.py"
WRITER = EXEC / "canonical_people_writer.py"
PREVIEW = EXEC / "talent_intel_preview.py"

# ------------------------------------------------------------------
# CONTRACT FILES
# ------------------------------------------------------------------
UPSTREAM = REPO_ROOT / "people_enriched.csv"
NAMED = REPO_ROOT / "people_named.csv"
MAPPED = REPO_ROOT / "people_mapped.csv"
PHASE6_OUT = REPO_ROOT / "people_phase6.csv"
PHASE7_OUT = REPO_ROOT / "people_phase7.csv"

# ------------------------------------------------------------------
# UTILS
# ------------------------------------------------------------------
def die(msg):
    print(f"❌ {msg}", file=sys.stderr)
    sys.exit(1)

def require(path: Path, label: str):
    if not path.exists():
        die(f"Missing required file [{label}]: {path}")

def run(cmd, label):
    print(f"\n▶ {label}")
    res = subprocess.run(cmd, cwd=str(REPO_ROOT))
    if res.returncode != 0:
        die(f"{label} FAILED")

def should_skip_name_resolution(upstream: Path, named: Path) -> bool:
    if not named.exists():
        return False
    return named.stat().st_mtime >= upstream.stat().st_mtime

# ------------------------------------------------------------------
# MAIN
# ------------------------------------------------------------------
def main(argv):
    if len(argv) != 2:
        die("Usage: run_safe.py <scenario_name>")

    scenario = argv[1]

    # --------------------------------------------------------------
    # 1. Scenario resolution
    # --------------------------------------------------------------
    require(SCENARIO_RESOLVER, "Scenario Resolver")

    proc = subprocess.run(
        [sys.executable, str(SCENARIO_RESOLVER), scenario],
        capture_output=True,
        text=True,
    )
    if proc.returncode != 0:
        die(proc.stderr.strip())

    resolved = {}
    for line in proc.stdout.splitlines():
        if "=" in line:
            k, v = line.split("=", 1)
            resolved[k.strip()] = v.strip()

    prefix = resolved.get("SCENARIO_PREFIX")
    if not prefix:
        die("Scenario resolver did not emit SCENARIO_PREFIX")

    # --------------------------------------------------------------
    # 2. Upstream contract
    # --------------------------------------------------------------
    require(UPSTREAM, "people_enriched.csv")

    # --------------------------------------------------------------
    # 3. Name Resolution (idempotent)
    # --------------------------------------------------------------
    require(NAME_PASS, "Name Resolution Pass")
    if should_skip_name_resolution(UPSTREAM, NAMED):
        print("\n⚡ Skipping Name Resolution Pass (cached)")
    else:
        run(
            [sys.executable, str(NAME_PASS), str(UPSTREAM), str(NAMED)],
            "Name Resolution Pass",
        )

    # --------------------------------------------------------------
    # 4. Schema Mapping
    # --------------------------------------------------------------
    require(SCHEMA_MAPPER, "Schema Mapper")
    run(
        [sys.executable, str(SCHEMA_MAPPER), str(NAMED), str(MAPPED)],
        "Canonical Schema Mapping",
    )

    # --------------------------------------------------------------
    # 5. Phase 6
    # --------------------------------------------------------------
    require(PHASE6, "Phase 6")
    run(
        [sys.executable, str(PHASE6), str(MAPPED), str(PHASE6_OUT)],
        "Phase 6: AI Stack Signal Extraction",
    )

    # --------------------------------------------------------------
    # 6. Phase 7
    # --------------------------------------------------------------
    require(PHASE7, "Phase 7")
    run(
        [sys.executable, str(PHASE7), str(PHASE6_OUT), str(PHASE7_OUT)],
        "Phase 7: OSS Contribution Intelligence",
    )

    # --------------------------------------------------------------
    # 7. SINGLE CSV WRITE (LOCKED)
    # --------------------------------------------------------------
    require(WRITER, "Canonical People Writer")
    OUTPUTS.mkdir(exist_ok=True)

    run(
        [
            sys.executable,
            str(WRITER),
            str(PHASE7_OUT),
            str(OUTPUTS),
            prefix,
        ],
        "Canonical CSV Writer",
    )

    canonical_csv = OUTPUTS / f"{prefix}_CANONICAL.csv"
    if not canonical_csv.exists():
        die(f"Canonical CSV not found: {canonical_csv}")

    print(f"\n✔ Wrote canonical CSV: {canonical_csv}")
    print(f"Rows/Columns verified by writer")

    # --------------------------------------------------------------
    # 8. Preview (NON-BLOCKING, NON-RECURSIVE)
    # --------------------------------------------------------------
    if PREVIEW.exists():
        print("\n▶ Talent Intelligence Preview")
        subprocess.run(
            [
                sys.executable,
                str(PREVIEW),
                str(canonical_csv),
                "demo",
                prefix,
            ],
            cwd=str(REPO_ROOT),
        )

    print("\n✔ PIPELINE COMPLETE — SINGLE ENTRYPOINT GUARANTEED")

# ------------------------------------------------------------------
if __name__ == "__main__":
    main(sys.argv)
