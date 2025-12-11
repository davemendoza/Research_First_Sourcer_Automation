#!/usr/bin/env python3
# © 2025 Dave Mendoza, DBA AI Craft, Inc. All rights reserved. Strictly proprietary; no copying, derivative works, reverse engineering, redistribution, or commercial/personal use permitted without written authorization. Governed by Colorado, USA law.
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

Proprietary Rights Notice
------------------------
All code, scripts, GitHub repositories, documentation, data, and GPT-integrated components of the AI Talent Engine – Signal Intelligence and Research_First_Sourcer_Automation Python Automation Sourcing Framework are strictly proprietary. All intellectual property rights, copyrights, trademarks, and related rights are exclusively owned by Dave Mendoza, DBA AI Craft, Inc.
No individual or entity may copy, reproduce, distribute, modify, create derivative works, reverse engineer, decompile, or otherwise use any part of this system, software, or associated materials for personal or commercial purposes without explicit written authorization from Dave Mendoza.
All rights reserved. Unauthorized use may result in legal action.
This statement is governed by the laws of the State of Colorado, USA.
