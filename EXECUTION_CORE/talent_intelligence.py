# =============================================================================
# FILE: talent_intelligence.py
# PURPOSE: Always print interview-grade preview, no CSV required.
# INVOCATION: python3 EXECUTION_CORE/talent_intelligence.py
# =============================================================================

from talent_intel_preview import run_preview

def main() -> int:
    run_preview(total=50)
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
