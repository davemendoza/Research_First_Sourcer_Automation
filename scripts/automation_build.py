#!/usr/bin/env python3
# ============================================================
#  AI Talent Engine – Phase 8 Automation Build Controller
#  Created by L. David Mendoza © 2025
# ============================================================

"""
automation_build.py
-------------------
Central automation runner for Phase 8 of the AI Talent Engine.

Functions:
• Executes Phase 8 schema validation (validate_phase8.py)
• Generates and stores a JSON validation summary in /outputs/
• Produces a human-readable audit log with governance checks
• Prepares environment variables for downstream analytics
"""

import os
import json
import subprocess
from datetime import datetime

# ------------------------------------------------------------
# CONFIGURATION
# ------------------------------------------------------------
BASE_ROOT = "/Users/davemendoza/Desktop/Research_First_Sourcer_Automation"
PHASE_PATH = os.path.join(BASE_ROOT, "Phase8")
OUTPUT_PATH = os.path.join(BASE_ROOT, "outputs")
VALIDATION_SCRIPT = os.path.join(PHASE_PATH, "validate_phase8.py")
JSON_OUTPUT = os.path.join(OUTPUT_PATH, "phase8_validation.json")
LOG_FILE = os.path.join(OUTPUT_PATH, "phase8_audit_log.txt")

os.makedirs(OUTPUT_PATH, exist_ok=True)

# ------------------------------------------------------------
# UTILITIES
# ------------------------------------------------------------

def run_validation():
    """Run the Phase 8 validator and capture stdout."""
    print("🚀 Running Phase 8 validation...")
    result = subprocess.run(["python3", VALIDATION_SCRIPT],
                            capture_output=True, text=True)
    output = result.stdout.strip()
    print(output)
    return output

def parse_validation_output(output: str):
    """Extract basic values from the validator console output."""
    data = {
        "timestamp": datetime.now().isoformat(),
        "schema_master_version": None,
        "schema_reference_version": None,
        "phase_scope": None,
        "governance_complete": False,
        "validation_passed": "✅" in output,
    }

    for line in output.splitlines():
        if "Master schema version:" in line:
            data["schema_master_version"] = line.split(":")[-1].strip()
        elif "Schema reference version:" in line:
            data["schema_reference_version"] = line.split(":")[-1].strip()
        elif "Phase scope declared:" in line:
            data["phase_scope"] = line.split(":")[-1].strip()
        elif "All required governance agents" in line:
            data["governance_complete"] = True

    return data

def write_json_report(data: dict):
    """Write structured validation results to /outputs/phase8_validation.json."""
    with open(JSON_OUTPUT, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)
    print(f"✅ JSON validation report written to: {JSON_OUTPUT}")

def write_audit_log(output: str):
    """Append a plain-text audit trail entry."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"\n[{timestamp}] Phase 8 Validation Run\n")
        f.write(output + "\n" + ("-" * 60) + "\n")
    print(f"📝 Audit log updated: {LOG_FILE}")

# ------------------------------------------------------------
# MAIN EXECUTION
# ------------------------------------------------------------
def main():
    print("============================================================")
    print("🧠  AI Talent Engine – Phase 8 Automation Build Controller")
    print("============================================================")

    validation_output = run_validation()
    parsed = parse_validation_output(validation_output)

    write_json_report(parsed)
    write_audit_log(validation_output)

    print("\n📊 Summary:")
    for k, v in parsed.items():
        print(f"• {k}: {v}")

    print("\n✅ Phase 8 automation build complete.\n")

if __name__ == "__main__":
    main()
