"""
ENTRYPOINT: python3 -m EXECUTION_CORE.talent_intelligence
DO NOT run directly.
"""

from EXECUTION_CORE.talent_intel_preview import run_preview

def main():
    run_preview(total=50)

if __name__ == "__main__":
    main()
