#!/usr/bin/env python3
"""
AI Talent Engine — Candidate JSON Validator v3.7
Mode: Best-in-Class (Auto-Clean + Schema Enforcement)
"""

import os, json, re, datetime, sys
from pathlib import Path
from rich import print

OUTPUT_DIR = Path("~/Desktop/Research_First_Sourcer_Automation/output").expanduser()
SCHEMA_VERSION = "3.6"

def clean_json_string(text: str) -> str:
    """Sanitize invisible control chars and unescaped sequences."""
    text = re.sub(r'[\x00-\x1F\x7F]', '', text)  # remove control chars
    text = text.replace('\\', '\\\\')  # ensure safe escapes
    return text

def safe_load_json(path: Path):
    """Try to load, clean, and reload JSON content."""
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError:
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            raw = f.read()
        cleaned = clean_json_string(raw)
        try:
            data = json.loads(cleaned)
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
            return data
        except Exception:
            return None
    except Exception:
        return None

def validate_json_file(path: Path):
    """Full validation pipeline with repair."""
    report = {"file": path.name, "valid": False, "repaired": False}
    data = safe_load_json(path)
    if not data:
        report["error"] = "Unrecoverable JSON corruption"
        return report

    # Required top-level fields
    required = ["name","role_classification","composite_score","recommendation","Evidence_Map_JSON"]
    missing = [f for f in required if f not in data]
    if missing:
        for f in missing:
            data[f] = None
        report["repaired"] = True

    # Evidence map structure
    evidence = data.get("Evidence_Map_JSON", [])
    if not isinstance(evidence, list):
        data["Evidence_Map_JSON"] = []
        report["repaired"] = True
    else:
        for item in evidence:
            if not isinstance(item, dict):
                report["repaired"] = True
                continue
            if "confidence" in item and isinstance(item["confidence"], (int, float)):
                if not (0 <= item["confidence"] <= 1):
                    item["confidence"] = min(max(item["confidence"], 0), 1)
                    report["repaired"] = True

    # Compute evidence score
    scores = [ev.get("confidence", 0) for ev in data["Evidence_Map_JSON"] if isinstance(ev.get("confidence"), (int, float))]
    data["evidence_score"] = round(sum(scores)/len(scores), 3) if scores else 0

    # Inject schema metadata
    data["schema_version"] = SCHEMA_VERSION
    data["last_validated"] = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")

    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    report["valid"] = True
    return report

def main():
    print(f"\n[bold cyan]🔍 Validating and Auto-Cleaning Candidate JSONs in:[/bold cyan] {OUTPUT_DIR}")
    print(f"[bold yellow]📘 Schema Reference:[/bold yellow] AI_Talent_Schema_Rules.md (v{SCHEMA_VERSION})\n")

    if not OUTPUT_DIR.exists():
        print(f"[bold red]❌ Directory not found:[/bold red] {OUTPUT_DIR}")
        sys.exit(1)

    reports = []
    for file in OUTPUT_DIR.glob("*.json"):
        result = validate_json_file(file)
        reports.append(result)
        if result["valid"]:
            print(f"[green]✅ {file.name}[/green] — VALID {'(auto-repaired)' if result['repaired'] else ''}")
        else:
            print(f"[red]❌ {file.name}[/red] — {result.get('error','Unknown error')}")

    valid_total = sum(1 for r in reports if r["valid"])
    total = len(reports)
    print(f"\n[bold cyan]✨ Validation Summary:[/bold cyan] {valid_total}/{total} VALID files\n")

    # Write audit log
    log_path = OUTPUT_DIR / "_auto_clean_audit.txt"
    with open(log_path, "w", encoding="utf-8") as f:
        json.dump(reports, f, indent=2)
    print(f"[bold blue]🧾 Auto-Clean audit log saved to:[/bold blue] {log_path}\n")

    sys.exit(0 if valid_total == total else 1)

if __name__ == "__main__":
    main()
