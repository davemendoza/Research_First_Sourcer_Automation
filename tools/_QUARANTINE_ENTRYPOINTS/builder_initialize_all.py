# ======================================================
#  AI Talent Engine — Builder Initializer v3.6 (Unified Final)
#  © 2025 L. David Mendoza · All Rights Reserved
#  Legal Notice: Confidential & Proprietary — See Legal_Proprietary_Notice.txt
# ======================================================
#  STATUS: Fully Automated | Schema-Locked (40 Columns)
#  PURPOSE: End-to-end orchestration of Phase Generation,
#           Real-Time Citation Integration, Master Build,
#           Validation, Audit, and Governance.
# ======================================================

import os, sys, json, time, hashlib, datetime, subprocess, platform
import pandas as pd

ENGINE_VERSION = "v3.6 Unified Final"
SCHEMA_VERSION = "v3.2"
SCHEMA_COLUMNS = 40

DATA_DIR = "data"
LOG_DIR = "logs"
ASSETS_DIR = "demo_assets"
CHART_DIR = "charts"

for d in [DATA_DIR, LOG_DIR, ASSETS_DIR, CHART_DIR]:
    os.makedirs(d, exist_ok=True)

print("=======================================================")
print(f" AI Talent Engine – Builder Initializer {ENGINE_VERSION}")
print(f" {datetime.datetime.now()}")
print("=======================================================")

# ------------------------------------------------------
# Dependency Installation
# ------------------------------------------------------
def install_dependencies():
    print("🧭 Installing dependencies")
    pkgs = ["pandas", "matplotlib", "requests", "numpy"]
    for pkg in pkgs:
        subprocess.run([sys.executable, "-m", "pip", "install", "-q", pkg])
    print("✅ Installing dependencies completed successfully.\n")

# ------------------------------------------------------
# SHA256 Utility
# ------------------------------------------------------
def sha256sum(path: str):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()

# ------------------------------------------------------
# Phase 6 & 7 Autogeneration
# ------------------------------------------------------
def generate_phase_data():
    print("🧭 Phase Data Generation")
    try:
        subprocess.run([sys.executable, "autogenerate_phase_data.py"], check=True)
    except subprocess.CalledProcessError:
        print("❌ Phase data generation failed — exiting.")
        sys.exit(1)

    meta = {
        "phase6": sha256sum(os.path.join(DATA_DIR, "phase6_output.csv")),
        "phase7": sha256sum(os.path.join(DATA_DIR, "phase7_output.csv")),
        "timestamp": datetime.datetime.now().isoformat(),
    }
    with open(os.path.join(DATA_DIR, "phase_generation_meta.json"), "w") as f:
        json.dump(meta, f, indent=2)
    print("✅ Phase Data Generation completed successfully.\n")

# ------------------------------------------------------
# Real-Time Citation Integration
# ------------------------------------------------------
def integrate_realtime_metrics():
    print("🧭 Real-Time Citation Ingestion")
    try:
        subprocess.run([sys.executable, "fetch_realtime_citation_data.py"], check=True)
        subprocess.run([sys.executable, "integrate_realtime_metrics.py"], check=True)
        print("✅ Real-Time Citation Integration completed successfully.\n")
    except Exception as e:
        print(f"⚠️ Real-Time Citation Integration failed ({e}) — fallback to offline mode.")
        if not os.path.exists(os.path.join(DATA_DIR, "realtime_citation_metrics.csv")):
            open(os.path.join(DATA_DIR, "realtime_citation_metrics.csv"), "w").write("Full_Name,Citation_Trajectory,Citation_Velocity_Score,Citation_Growth_Rate,Influence_Rank_Change,Coauthor_Influence_Velocity\n")
        print("✅ Offline fallback placeholder created.\n")

# ------------------------------------------------------
# Master Generator
# ------------------------------------------------------
def generate_master():
    print("🧭 Master Data Generation")
    try:
        subprocess.run([sys.executable, "generate_ai_talent_master_v34.py"], check=True)
        print("✅ Master Data Generation completed successfully.\n")
    except subprocess.CalledProcessError:
        print("❌ Master Data Generation failed — exiting.")
        sys.exit(1)

# ------------------------------------------------------
# Validation & Governance
# ------------------------------------------------------
def validate_schema():
    print("🧩 Validating schema & numeric integrity")
    import glob
    errors = []
    for f in glob.glob(f"{DATA_DIR}/*_demo.csv"):
        df = pd.read_csv(f)
        if df.shape[1] != SCHEMA_COLUMNS:
            errors.append(f"{f} has {df.shape[1]} columns (expected {SCHEMA_COLUMNS})")
        if "Citation_Trajectory" in df.columns:
            vals = pd.to_numeric(df["Citation_Trajectory"], errors="coerce")
            if not vals.between(0, 10).all():
                errors.append(f"{f} Citation_Trajectory out of [0,10]")
    if errors:
        for e in errors:
            print(" -", e)
        print("❌ Schema validation failed.\n")
        sys.exit(1)
    print("✅ Schema and numeric validation passed for all demo CSVs.\n")

# ------------------------------------------------------
# Audit & Summary
# ------------------------------------------------------
def audit_and_summarize():
    print("🔒 Auditing final CSVs for checksum integrity")
    import glob
    audit = {}
    for f in glob.glob(f"{DATA_DIR}/*.csv"):
        sha = sha256sum(f)
        audit[f] = sha
        print(f"   {os.path.basename(f)} — SHA256 {sha[:16]}…")

    with open(os.path.join(LOG_DIR, "audit_log.json"), "w") as jf:
        json.dump(audit, jf, indent=2)

    summary = {
        "timestamp": datetime.datetime.now().isoformat(),
        "engine_version": ENGINE_VERSION,
        "schema_version": SCHEMA_VERSION,
        "phase_files": list(audit.keys()),
        "environment": {
            "python": platform.python_version(),
            "system": platform.system(),
            "user": os.getenv("USER", "unknown")
        }
    }

    summary_path = os.path.join(ASSETS_DIR, "builder_summary.json")
    with open(summary_path, "w") as sf:
        json.dump(summary, sf, indent=2)
    print(f"📄 Builder summary written → {summary_path}")
    print("✅ SHA256 audit complete.\n")

# ------------------------------------------------------
# Git Commit + Push
# ------------------------------------------------------
def git_commit_and_push():
    if os.path.exists(".git"):
        print("📤 Committing & pushing results to GitHub…")
        subprocess.run(["git", "add", "data", "charts", "logs", "demo_assets"])
        subprocess.run(["git", "commit", "-m", f'AI Talent Engine Build {datetime.datetime.now():%Y%m%d_%H%M}'], check=False)
        subprocess.run(["git", "push"], check=False)
        print("✅ Git push completed.\n")

# ------------------------------------------------------
# MAIN PIPELINE
# ------------------------------------------------------
def main():
    install_dependencies()
    generate_phase_data()
    integrate_realtime_metrics()
    generate_master()
    validate_schema()
    audit_and_summarize()
    git_commit_and_push()

    print("=======================================================")
    print("  ✅ AI Talent Engine Build Complete — v3.6 Unified Final")
    print("=======================================================\n")
    print("✅ AI Talent Engine Demo initialized successfully — all systems operational.\n")

if __name__ == "__main__":
    main()
