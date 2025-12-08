#!/usr/bin/env python3
"""
AI Talent Engine — Hiring Intelligence Summary Generator
Best-in-Class Build (v3.7)
"""

import json, os, datetime
from statistics import mean
from rich import print

OUTPUT_DIR = os.path.expanduser("~/Desktop/Research_First_Sourcer_Automation/output")
REPORT_PATH = os.path.join(OUTPUT_DIR, "Hiring_Intelligence_Summary_Report.md")

summary_data = []
timestamp = datetime.datetime.now(datetime.UTC).strftime("%Y-%m-%d %H:%M:%SZ")

print(f"\n📊 Generating [bold cyan]Hiring Intelligence Summary[/bold cyan]...")
print(f"📁 Source: {OUTPUT_DIR}\n")

# Read all JSON dossiers
for file in os.listdir(OUTPUT_DIR):
    if file.endswith(".json"):
        path = os.path.join(OUTPUT_DIR, file)
        try:
            with open(path) as f:
                data = json.load(f)
            name = data.get("name", "Unknown")
            score = data.get("composite_score", 0)
            rec = data.get("recommendation", "❔ Unknown")
            evidences = data.get("Evidence_Map_JSON", [])
            confs = [ev.get("confidence", 0) for ev in evidences if isinstance(ev, dict)]
            avg_conf = round(mean(confs), 3) if confs else 0.0
            strengths = [e["statement"] for e in evidences if e.get("strength_or_weakness") == "Strength"]
            weaknesses = [e["statement"] for e in evidences if e.get("strength_or_weakness") == "Weakness"]
            summary_data.append({
                "name": name,
                "score": score,
                "recommendation": rec,
                "avg_confidence": avg_conf,
                "strengths": strengths,
                "weaknesses": weaknesses
            })
            print(f"✅ Loaded {file} ({len(evidences)} evidence items)")
        except Exception as e:
            print(f"❌ Error loading {file}: {e}")

# Write Markdown report
with open(REPORT_PATH, "w") as r:
    r.write(f"# Hiring Intelligence Summary Report\n\n")
    r.write(f"**Generated:** {timestamp}\n\n")
    r.write(f"**Validated Dossiers:** {len(summary_data)}\n\n")
    r.write("---\n\n")
    for item in summary_data:
        r.write(f"## {item['name']}\n")
        r.write(f"- **Composite Score:** {item['score']}\n")
        r.write(f"- **Average Confidence:** {item['avg_confidence']}\n")
        r.write(f"- **Recommendation:** {item['recommendation']}\n\n")
        if item["strengths"]:
            r.write("### Strengths\n")
            for s in item["strengths"]:
                r.write(f"- {s}\n")
            r.write("\n")
        if item["weaknesses"]:
            r.write("### Weaknesses\n")
            for w in item["weaknesses"]:
                r.write(f"- {w}\n")
            r.write("\n")
        r.write("---\n\n")
    r.write("### 🧠 Overall AI Talent Insights\n")
    r.write("This summary consolidates validated candidate dossiers from the Research-First Sourcer Automation framework. "
            "Each candidate's evidence map, schema version, and confidence metrics are derived directly from validated JSON artifacts.\n")

print(f"\n✨ [bold green]Summary report generated:[/bold green] {REPORT_PATH}")
os.system(f"open -a 'TextEdit' '{REPORT_PATH}'")
print("📖 Report opened for review.\n")
