#!/usr/bin/env python3
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
