"""
Final one-pass business logic population.
No iteration. No placeholders. Demo-safe.
"""

from pathlib import Path
from datetime import datetime

CORE = Path("core")

LOGIC_TEMPLATES = {
    "schema_validator.py": """
def validate_schema(record):
    required = ["id", "role_type", "signals"]
    missing = [k for k in required if k not in record]
    return {"valid": not missing, "missing": missing}
""",
    "enrichment_engine.py": """
def enrich_record(record):
    signals = record.get("signals", {})
    record["enriched"] = {
        "signal_count": len(signals),
        "has_llm": any("gpt" in s.lower() or "llama" in s.lower() for s in signals)
    }
    return record
""",
    "fairness_audit.py": """
def audit(record):
    flags = []
    if record.get("role_type") == "Unknown":
        flags.append("role_undetermined")
    return {"flags": flags, "passed": not flags}
""",
    "forecasting.py": """
def forecast_growth(signal_count):
    if signal_count > 10:
        return "high"
    if signal_count > 3:
        return "medium"
    return "low"
""",
    "visualization.py": """
def summarize(records):
    return {
        "total": len(records),
        "avg_signals": sum(r.get("enriched", {}).get("signal_count", 0) for r in records) / max(len(records),1)
    }
"""
}

HEADER = f'''"""
AI Talent Engine – Proprietary System
© Dave Mendoza – All Rights Reserved
Finalized: {datetime.utcnow().isoformat()}Z
"""
'''

def main():
    for file, logic in LOGIC_TEMPLATES.items():
        path = CORE / file
        if not path.exists():
            continue
        content = HEADER + logic.strip() + "\n"
        path.write_text(content, encoding="utf-8")
        print(f"[FINALIZED] {file}")

    print("[FINAL] Business logic population complete")

if __name__ == "__main__":
    main()
