# =============================================================================
# FILE: EXECUTION_CORE/talent_intelligence.py
# PURPOSE: Interview-grade preview entrypoint (CSV-independent)
# INVOCATION (canonical): python3 -m EXECUTION_CORE.talent_intelligence
# =============================================================================

from .talent_intel_preview import run_preview

def main() -> int:
    run_preview(total=50)
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
