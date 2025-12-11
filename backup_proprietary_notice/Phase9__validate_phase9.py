#!/usr/bin/env python3
# © 2025 Dave Mendoza, DBA AI Craft, Inc. All rights reserved. Strictly proprietary; no copying, derivative works, reverse engineering, redistribution, or commercial/personal use permitted without written authorization. Governed by Colorado, USA law.
"""
AI Talent Engine — Phase 9 Multi-File Validator
Validates schema metadata, governance integrity, and section completeness.
"""

import os, json, re, datetime

BASE_DIR = "/Users/davemendoza/Desktop/Research_First_Sourcer_Automation"
PHASE_DIR = f"{BASE_DIR}/Phase9"
DOCS_DIR = f"{BASE_DIR}/docs"
OUTPUT_FILE = f"{BASE_DIR}/outputs/phase9_validation.json"
AUDIT_LOG = f"{BASE_DIR}/outputs/phase9_audit_log.txt"

FILES_TO_VALIDATE = [
    f"{PHASE_DIR}/AI_Talent_Engine_Master.md",
    f"{PHASE_DIR}/AI_Talent_Schema_Rules.md",
    f"{DOCS_DIR}/AI_Talent_Review_Template.md",
    f"{DOCS_DIR}/README_SYSTEM_SPEC.md"
]

# ------------------------------------------------------------------
def extract(key, text):
    match = re.search(rf"^{key}:\s*(.+)$", text, re.MULTILINE)
    return match.group(1).strip() if match else None

def read(path):
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

def check_governance_agents(text):
    required = ["#21", "#22", "#23", "#24"]
    return all(agent in text for agent in required)

def validate_file(path, ref_version=None):
    text = read(path)
    data = {
        "file": os.path.basename(path),
        "schema_version": extract("schema_version", text),
        "schema_reference": extract("schema_reference", text),
        "phase_scope": extract("phase_scope", text),
        "maintainer": extract("maintainer", text),
        "governance_ok": check_governance_agents(text),
    }
    data["schema_match"] = (data["schema_version"] == ref_version) if ref_version else True
    data["validation_passed"] = all([
        bool(data["schema_version"]),
        bool(data["schema_reference"]),
        bool(data["phase_scope"]),
        bool(data["maintainer"]),
        data["governance_ok"],
        data["schema_match"]
    ])
    return data

def main():
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    results = {"timestamp": datetime.datetime.now().isoformat(), "files": []}

    # reference version = first file with a version
    reference_version = None

    for path in FILES_TO_VALIDATE:
        if os.path.exists(path):
            data = validate_file(path, reference_version)
            if not reference_version and data["schema_version"]:
                reference_version = data["schema_version"]
            results["files"].append(data)
        else:
            results["files"].append({"file": os.path.basename(path), "error": "File not found", "validation_passed": False})

    results["reference_schema_version"] = reference_version
    results["all_passed"] = all(f.get("validation_passed", False) for f in results["files"])

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=4)

    # Write audit log
    with open(AUDIT_LOG, "a", encoding="utf-8") as log:
        log.write(f"[{results['timestamp']}] Phase9 validation run — passed={results['all_passed']}\n")

    print("🔍 Phase 9 Validation Report")
    print(json.dumps(results, indent=4))
    print(f"✅ Output written → {OUTPUT_FILE}")
    print(f"📝 Audit updated → {AUDIT_LOG}")

if __name__ == "__main__":
    main()

Proprietary Rights Notice
------------------------
All code, scripts, GitHub repositories, documentation, data, and GPT-integrated components of the AI Talent Engine – Signal Intelligence and Research_First_Sourcer_Automation Python Automation Sourcing Framework are strictly proprietary. All intellectual property rights, copyrights, trademarks, and related rights are exclusively owned by Dave Mendoza, DBA AI Craft, Inc.
No individual or entity may copy, reproduce, distribute, modify, create derivative works, reverse engineer, decompile, or otherwise use any part of this system, software, or associated materials for personal or commercial purposes without explicit written authorization from Dave Mendoza.
All rights reserved. Unauthorized use may result in legal action.
This statement is governed by the laws of the State of Colorado, USA.
