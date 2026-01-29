#!/usr/bin/env python3
# =====================================================================
# RESEARCH FIRST SOURCER AUTOMATION
# run_safe.py — execution gatekeeper
#
# © 2026 L. David Mendoza. All Rights Reserved.
# =====================================================================

import sys
from pathlib import Path

from EXECUTION_CORE.phase5_passthrough import process_csv as phase5_process_csv
from EXECUTION_CORE.phase6_ai_stack_signals import run_phase6
from EXECUTION_CORE.phase7_oss_contribution_intel import run_phase7


REPO_ROOT = Path("/Users/davemendoza/Desktop/Research_First_Sourcer_Automation")


def _fail(msg: str) -> None:
    raise RuntimeError(msg)


def _assert_repo_root() -> None:
    if Path.cwd().resolve() != REPO_ROOT:
        _fail(
            "ERROR: Must run from canonical repo root.\n"
            f"Expected: {REPO_ROOT}\n"
            f"Actual:   {Path.cwd().resolve()}"
        )


def _run_scenario(role_slug: str) -> None:
    p4_seed = (
        REPO_ROOT
        / "OUTPUTS"
        / "scenario"
        / role_slug
        / f"{role_slug}_04_seed.csv"
    )

    if not p4_seed.exists():
        _fail(
            "Scenario run cannot start Phase 5 because Phase 4 seed is missing.\n"
            f"Expected Phase 4 seed path:\n{p4_seed}\n\n"
            "Next action:\n"
            f"  python3 EXECUTION_CORE/phase4_seed_builder.py "
            f"--role {role_slug} --input <FULL_INPUT_CSV>"
        )

    scenario_dir = REPO_ROOT / "OUTPUTS" / "scenario" / role_slug
    scenario_dir.mkdir(parents=True, exist_ok=True)

    # Phase 5 (scenario ONLY)
    p5_out = Path(
        phase5_process_csv(str(p4_seed), str(scenario_dir))
    ).resolve()

    # Phase 6
    p6_out = Path(run_phase6(p5_out)).resolve()

    # Phase 7
    p7_out = Path(run_phase7(p6_out)).resolve()

    print("[SUCCESS] Scenario run complete")
    print(f"Final output → {p7_out}")


def _run_demo(frontier_slug: str) -> None:
    demo_dir = REPO_ROOT / "OUTPUTS" / "demo" / frontier_slug

    full_csvs = list(demo_dir.glob("*.FULL.csv"))
    if not full_csvs:
        _fail(
            "Demo run failed: no FULL demo CSV found.\n"
            f"Expected under:\n{demo_dir}"
        )

    demo_input = full_csvs[0].resolve()

    # Demo NEVER runs Phase 5
    p6_out = Path(run_phase6(demo_input)).resolve()
    p7_out = Path(run_phase7(p6_out)).resolve()

    print("[SUCCESS] Demo run complete")
    print(f"Final output → {p7_out}")


def main(argv) -> None:
    _assert_repo_root()

    if len(argv) != 3:
        _fail(
            "Usage:\n"
            "  python3 -m EXECUTION_CORE.run_safe scenario <role_slug>\n"
            "  python3 -m EXECUTION_CORE.run_safe demo <frontier_slug>"
        )

    mode = argv[1]
    slug = argv[2]

    if mode == "scenario":
        _run_scenario(slug)
        return

    if mode == "demo":
        _run_demo(slug)
        return

    _fail(f"Unknown mode: {mode}")


if __name__ == "__main__":
    main(sys.argv)
