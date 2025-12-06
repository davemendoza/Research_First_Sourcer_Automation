# ==========================================================
# 🧩 Phase 6 Loader — AI Talent Engine
# Purpose: Central orchestration for Phase 6 agent loading,
# parsing, schema validation, and enrichment readiness.
# ==========================================================

import json
import re
from pathlib import Path
from rich.console import Console
from rich.table import Table

console = Console()

# ----------------------------------------------------------
# Paths
# ----------------------------------------------------------
DOC_PATH = Path("docs/AI_Talent_Engine_Phase6_Master.md")
EXPORT_PATH = Path("output/phase6_export.json")
VALIDATION_REPORT = Path("output/phase6_validation.yaml")

# ----------------------------------------------------------
# 1. Extract agents from Phase 6 markdown
# ----------------------------------------------------------
def extract_phase6_agents():
    console.print("[bold blue]📘 Parsing Phase 6 Master Document...[/bold blue]")

    if not DOC_PATH.exists():
        console.print(f"[red]❌ Missing document:[/red] {DOC_PATH}")
        return []

    content = DOC_PATH.read_text()
    pattern = r"(\d+)\s*·\s*(.+)"
    matches = re.findall(pattern, content)

    agents = []
    for num, name in matches:
        num_int = int(num)
        if 17 <= num_int <= 26:
            agents.append({
                "id": f"Agent_{num.zfill(2)}",
                "name": name.strip(),
                "phase": 6,
                "status": "active"
            })

    EXPORT_PATH.parent.mkdir(exist_ok=True)
    json.dump(agents, open(EXPORT_PATH, "w"), indent=2)

    console.print(f"[green]✅ Parsed {len(agents)} Phase 6 agents[/green]")
    console.print(f"[blue]📦 Exported → {EXPORT_PATH}[/blue]\n")

    return agents

# ----------------------------------------------------------
# 2. Display parsed results
# ----------------------------------------------------------
def display_table(agents):
    table = Table(title="Phase 6 Agent Export", show_lines=True)
    table.add_column("ID", justify="center", style="bold")
    table.add_column("Name", style="cyan")
    table.add_column("Phase", justify="center")
    table.add_column("Status", style="green")

    for a in agents:
        table.add_row(a["id"], a["name"], str(a["phase"]), a["status"])

    console.print(table)

# ----------------------------------------------------------
# 3. Main
# ----------------------------------------------------------
if __name__ == "__main__":
    console.rule("[bold cyan]Phase 6 Loader — Agent Extraction[/bold cyan]")
    agents = extract_phase6_agents()
    display_table(agents)
    console.print("\n[bold yellow]Next →[/bold yellow] Run [cyan]schema_validator.py[/cyan] or [cyan]schema_enricher.py[/cyan].")
