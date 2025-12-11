#!/usr/bin/env python3
# ============================================================
#  AI Talent Engine – Review Template Validator (Fast Mode)
#  Created by L. David Mendoza © 2025
# ============================================================

import os, re, json
from datetime import datetime

BASE_ROOT = "/Users/davemendoza/Desktop/Research_First_Sourcer_Automation"
TEMPLATE_FILE = os.path.join(BASE_ROOT, "docs", "AI_Talent_Review_Template.md")
SCHEMA_FILE = os.path.join(BASE_ROOT, "Phase8", "AI_Talent_Schema_Rules.md")
OUTPUT_FILE = os.path.join(BASE_ROOT, "outputs", "review_template_validation.json")

def read(path): 
    with open(path, "r", encoding="utf-8") as f: 
        return f.read()

def extract(key, text):
    m = re.search(rf"^{key}:\s*(.+)$", text, flags=re.MULTILINE)
    return m.group(1).strip() if m else None

def agents_ok(text):
    return all(tag in text for tag in ["#21", "#22", "#23", "#24"])

def has_sections(text):
    required = [
        "CANDIDATE OVERVIEW (HEADER)",
        "EVIDENCE TIER LEDGER",
        "EVALUATION SECTIONS",
        "HIRING MANAGER SUBMITTAL DECISION",
        "REVIEWER & PROVENANCE",
        "VERSION CONTROL & GOVERNANCE"
    ]
    return {s: bool(re.search(rf"{re.escape(s)}", text)) for s in required}

def validate():
    template = read(TEMPLATE_FILE)
    schema = read(SCHEMA_FILE)
    results = {
        "timestamp": datetime.now().isoformat(),
        "schema_version": extract("schema_version", template),
        "schema_ref": extract("schema_reference", template),
        "phase_scope": extract("phase_scope", template),
        "maintainer": extract("maintainer", template),
        "governance_ok": agents_ok(template),
        "schema_match": extract("schema_version", template) == extract("schema_version", schema),
        "sections": has_sections(template)
    }
    results["all_sections_present"] = all(results["sections"].values())
    results["validation_passed"] = results["schema_match"] and results["governance_ok"] and results["all_sections_present"]
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=4)
    print("🔍 Review Template Validation Report")
    print(json.dumps(results, indent=4))
    print(f"✅ Output written → {OUTPUT_FILE}")

if __name__ == "__main__":
    validate()
