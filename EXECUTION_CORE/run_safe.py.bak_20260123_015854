from pathlib import Path

from EXECUTION_CORE.phase5_passthrough import process_csv as phase5_process_csv
from EXECUTION_CORE.phase6_ai_stack_signals import process_csv as phase6_process_csv
from EXECUTION_CORE.phase7_oss_contribution_intel import process_csv as phase7_process_csv

def main(argv):
    role_slug = argv[1].lower().replace(" ", "_")

    base = Path("OUTPUTS") / "scenario" / role_slug
    base.mkdir(parents=True, exist_ok=True)

    p4 = base / "frontier_ai_research_scientist_04_seed.csv"
    p5 = base / "frontier_ai_research_scientist_05_phase5.csv"
    p6 = base / "frontier_ai_research_scientist_06_phase6.csv"
    p7 = base / "frontier_ai_research_scientist_07_phase7.csv"

    # Phase 5
    p5_out = phase5_process_csv(str(p4), str(p5))
    if not Path(p5_out).exists():
        raise RuntimeError("Phase 5 failed to write output")

    # Phase 6
    p6_out = phase6_process_csv(str(p5_out), str(p6))
    if not Path(p6_out).exists():
        raise RuntimeError("Phase 6 failed to write output")

    # Phase 7
    p7_out = phase7_process_csv(str(p6_out), str(p7))
    if not Path(p7_out).exists():
        raise RuntimeError("Phase 7 failed to write output")

    print("[SUCCESS] Scenario run complete")
    print(f"Final output -> {p7_out}")

if __name__ == "__main__":
    import sys
    main(sys.argv)
