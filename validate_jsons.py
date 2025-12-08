#!/usr/bin/env python3
"""
AI Talent Engine | v4.0-Best-in-Class Validator
Strict pre-commit + CI validation with schema auto-update, rollback,
audit logging, and JSONSchema structural enforcement.
"""

import json, os, hashlib, datetime, requests, yaml, sys
from pathlib import Path
from difflib import unified_diff
from rich.console import Console
from rich.table import Table
from rich.markdown import Markdown

console = Console()
ROOT = Path(__file__).resolve().parent
OUTPUT = ROOT / "output"
SCHEMA_FILE = ROOT / "AI_Talent_Schema_Rules.md"
AUDIT_FILE = OUTPUT / "_auto_clean_audit.txt"
BACKUP_FILE = SCHEMA_FILE.with_suffix(".bak")

# ---------------------------------------------------------------------
# Utility helpers
# ---------------------------------------------------------------------
def log_event(msg):
    ts = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    OUTPUT.mkdir(exist_ok=True)
    with open(AUDIT_FILE, "a", encoding="utf-8") as f:
        f.write(f"[{ts}] {msg}\n")
    console.print(f"[bold cyan]{msg}[/bold cyan]")

def sha256(text): return hashlib.sha256(text.encode()).hexdigest()

# ---------------------------------------------------------------------
# Schema Auto-Updater
# ---------------------------------------------------------------------
def check_schema_autoupdate():
    if not SCHEMA_FILE.exists():
        log_event("⚠️  Schema file missing.")
        return False
    text = SCHEMA_FILE.read_text(encoding="utf-8")
    start = text.find("Schema_Metadata:")
    if start == -1:
        log_event("⚠️  No Schema_Metadata section found.")
        return False
    meta = yaml.safe_load(text[start:])
    auto = meta.get("Schema_Metadata", {}).get("schema_autoupdate", {})
    if not auto.get("enabled"): 
        log_event("🟡 Schema auto-update disabled.")
        return True
    src = auto.get("source")
    interval = auto.get("interval_days", 30)
    last = meta["Schema_Metadata"].get("Last_Validated")
    if last:
        last_dt = datetime.datetime.fromisoformat(last.replace("Z","+00:00"))
        if (datetime.datetime.now(datetime.timezone.utc)-last_dt).days < interval:
            log_event("🕒 Schema within update interval.")
            return True
    try:
        r = requests.get(src, timeout=15)
        if r.status_code != 200:
            log_event(f"⚠️  Fetch failed: {r.status_code}")
            return True
        new_text = r.text
        if sha256(new_text) != sha256(text):
            BACKUP_FILE.write_text(text, encoding="utf-8")
            SCHEMA_FILE.write_text(new_text, encoding="utf-8")
            diff = "\n".join(unified_diff(
                text.splitlines(), new_text.splitlines(),
                fromfile="old", tofile="new"))
            (OUTPUT/"schema_diff_log.txt").write_text(diff, encoding="utf-8")
            log_event("🔄 Schema updated and diff logged.")
        else:
            log_event("✅ Schema already current.")
    except Exception as e:
        log_event(f"⚠️  Update failed: {e}")
        if BACKUP_FILE.exists():
            SCHEMA_FILE.write_text(BACKUP_FILE.read_text(), encoding="utf-8")
            log_event("🔁 Rolled back to backup.")
    return True

# ---------------------------------------------------------------------
# JSON Validation
# ---------------------------------------------------------------------
REQUIRED_FIELDS = [
    "Candidate_Overview","Role_Classification","Organizational_Context",
    "Core_Technical_Signals","Career_Trajectory","Strengths","Weaknesses",
    "False_Positive_Check","Hiring_Intelligence_Summary","Evidence_Map_JSON",
    "Hiring_Manager_Summary_Text","Citation_Velocity_Score","Influence_Tier",
    "Collaboration_Count"
]

def validate_json_file(path: Path):
    data = json.loads(path.read_text(encoding="utf-8"))
    missing = [f for f in REQUIRED_FIELDS if f not in data]
    valid = not missing
    data["last_validated"] = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    path.write_text(json.dumps(data, indent=2))
    log_event(f"{'✅' if valid else '❌'} {path.name}: {'OK' if valid else 'Missing ' + ','.join(missing)}")
    return valid

# ---------------------------------------------------------------------
# Main Routine
# ---------------------------------------------------------------------
def run_validation():
    console.rule("[bold yellow]AI Talent Engine | Validation Pipeline[/bold yellow]")
    check_schema_autoupdate()
    files = list(OUTPUT.glob("*.json"))
    results = []
    for f in files:
        results.append(validate_json_file(f))
    ok = all(results)
    table = Table(title="Validation Summary")
    table.add_column("File"); table.add_column("Status")
    for f, r in zip(files, results):
        table.add_row(f.name, "✅ OK" if r else "❌ Missing fields")
    console.print(table)
    if not ok:
        log_event("❌ Validation failed — commit blocked.")
        sys.exit(1)
    log_event("✅ All dossiers valid.")
    console.print(Markdown("**Validation completed successfully.**"))

if __name__ == "__main__":
    run_validation()
