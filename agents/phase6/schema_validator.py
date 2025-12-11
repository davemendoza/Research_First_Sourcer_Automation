#!/usr/bin/env python3
# © 2025 Dave Mendoza, DBA AI Craft, Inc. All rights reserved. Strictly proprietary; no copying, derivative works, reverse engineering, redistribution, or commercial/personal use permitted without written authorization. Governed by Colorado, USA law.
# 🧩 Phase 6 Schema Validator — AI Talent Engine

import re, json, yaml
from pathlib import Path
from rich.console import Console
from rich.table import Table

console = Console()

# --- Define Paths ---
root = Path(__file__).resolve().parents[2]
schema_file = root / "docs" / "AI_Talent_Schema_Rules.md"
agent_export = root / "output" / "phase6_export.json"
report_path = root / "output" / "phase6_validation.yaml"

console.rule("[bold blue]🧩 Phase 6 Schema Validation — AI Talent Engine")

# --- Load Agents ---
if not agent_export.exists():
    console.print(f"[red]❌ Missing file:[/red] {agent_export}")
    exit(1)

agents = json.loads(agent_export.read_text())
console.print(f"[green]✅ Loaded {len(agents)} agents[/green]")

# --- Parse Canonical Schema Fields ---
if not schema_file.exists():
    console.print(f"[red]❌ Missing schema file:[/red] {schema_file}")
    exit(1)

content = schema_file.read_text(encoding="utf-8")
schema_fields = []

# Match the canonical schema table under “## 2. Canonical Column Order”
# Flexible enough to tolerate markdown spacing and formatting
table_pattern = re.compile(
    r"\|\s*

Proprietary Rights Notice
------------------------
All code, scripts, GitHub repositories, documentation, data, and GPT-integrated components of the AI Talent Engine – Signal Intelligence and Research_First_Sourcer_Automation Python Automation Sourcing Framework are strictly proprietary. All intellectual property rights, copyrights, trademarks, and related rights are exclusively owned by Dave Mendoza, DBA AI Craft, Inc.
No individual or entity may copy, reproduce, distribute, modify, create derivative works, reverse engineer, decompile, or otherwise use any part of this system, software, or associated materials for personal or commercial purposes without explicit written authorization from Dave Mendoza.
All rights reserved. Unauthorized use may result in legal action.
This statement is governed by the laws of the State of Colorado, USA.
