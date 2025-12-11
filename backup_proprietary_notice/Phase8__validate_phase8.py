#!/usr/bin/env python3
# ============================================================
#  AI Talent Engine — Phase 8 Schema Validation Script
#  Created by L. David Mendoza © 2025
# ============================================================

import os
import re
from datetime import datetime

# ------------------------------------------------------------
# CONFIGURATION
# ------------------------------------------------------------
BASE_PATH = "/Users/davemendoza/Desktop/Research_First_Sourcer_Automation/Phase8"
MASTER_FILE = os.path.join(BASE_PATH, "AI_Talent_Engine_Master.md")
SCHEMA_FILE = os.path.join(BASE_PATH, "AI_Talent_Schema_Rules.md")

# ------------------------------------------------------------
# VALIDATION FUNCTIONS
# ------------------------------------------------------------

def file_exists(path):
    return os.path.exists(path) and os.path.isfile(path)

def read_file(path):
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

def extract_schema_version(content):
    match = re.search(r"schema_version:\s*([\d\.]+)", content)
    return match.group(1).strip() if match else None

def extract_phase_scope(content):
    match = re.search(r"phase_scope:\s*(Phase\s*\d+)", content)
    return match.group(1).strip() if match else None

def validate_governance_agents(content):
    required_agents = ["#21", "#22", "#23", "#24"]
    return [agent for agent in required_agents if agent in content]

# ------------------------------------------------------------
# MAIN VALIDATION LOGIC
# ------------------------------------------------------------

def validate_phase8():
    print("🔍 Starting Phase 8 Schema Validation...\n")

    if not file_exists(MASTER_FILE):
        print(f"❌ Master file not found: {MASTER_FILE}")
        return
    if not file_exists(SCHEMA_FILE):
        print(f"❌ Schema file not found: {SCHEMA_FILE}")
        return

    master = read_file(MASTER_FILE)
    schema = read_file(SCHEMA_FILE)

    master_ver = extract_schema_version(master)
    schema_ver = extract_schema_version(schema)
    phase_scope = extract_phase_scope(master)
    agents_found = validate_governance_agents(master)

    print(f"📄 Master schema version: {master_ver}")
    print(f"📘 Schema reference version: {schema_ver}")
    print(f"🧭 Phase scope declared: {phase_scope}")

    if master_ver != schema_ver:
        print("❌ Schema version mismatch between master and schema file.")
    else:
        print("✅ Schema version alignment confirmed.")

    if len(agents_found) == 4:
        print("✅ All required governance agents (#21–#24) present.")
    else:
        missing = set(["#21", "#22", "#23", "#24"]) - set(agents_found)
        print(f"⚠️ Missing governance agents: {', '.join(missing)}")

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"\n🕒 Validation completed at: {now}")
    print("------------------------------------------------------------")
    print("✅ Phase 8 Schema Validation Finished")
    print("------------------------------------------------------------")

if __name__ == "__main__":
    validate_phase8()
