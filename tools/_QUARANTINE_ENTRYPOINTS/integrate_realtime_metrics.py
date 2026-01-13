# ======================================================
#  AI Talent Engine — Real-Time Citation Integrator v2.0 (Governance Edition)
#  © 2025 L. David Mendoza · All Rights Reserved
#  Legal Notice: Confidential & Proprietary — See Legal_Proprietary_Notice.txt
# ======================================================
#  PURPOSE: Merge live citation metrics into Phase 6 & 7 outputs,
#           maintain schema-lock (40 columns), prioritize Frontier/Foundational AI roles,
#           and log full provenance for governance compliance.
# ======================================================

import os, pandas as pd, json, datetime, hashlib, platform

# ------------------------------------------------------
# Configuration
# ------------------------------------------------------
DATA_DIR = "data"
LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)

PHASE6 = os.path.join(DATA_DIR, "phase6_output.csv")
PHASE7 = os.path.join(DATA_DIR, "phase7_output.csv")
REALTIME = os.path.join(DATA_DIR, "realtime_citation_metrics.csv")
OUT_PHASE6 = os.path.join(DATA_DIR, "phase6_output_merged.csv")
OUT_PHASE7 = os.path.join(DATA_DIR, "phase7_output_merged.csv")
LOG_JSON = os.path.join(LOG_DIR, "integration_log.json")

SCHEMA_COLUMNS = 40
FORCE_ALL = True   # Toggle: if True, apply to ALL roles, not just Frontier/Foundational AI

# ------------------------------------------------------
# Utility
# ------------------------------------------------------
def sha256sum(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()

def merge_realtime(base_df: pd.DataFrame, rt_df: pd.DataFrame, label: str) -> pd.DataFrame:
    """Merge real-time citation metrics into dataset based on classification."""
    print(f"🧩 Integrating real-time metrics into {label}…")

    if "AI_Classification" not in base_df.columns:
        base_df["AI_Classification"] = "Unclassified"

    # Restrict to Frontier/Foundational AI by default unless FORCE_ALL=True
    if not FORCE_ALL:
        focus_df = base_df[
            base_df["AI_Classification"].str.contains("Frontier|Foundational", case=False, na=False)
        ].copy()
    else:
        focus_df = base_df.copy()

    merged = pd.merge(focus_df, rt_df, on="Full_Name", how="left")

    # Core citation-related columns
    for col in [
        "Citation_Velocity_Score", "Citation_Growth_Rate",
        "Influence_Rank_Change", "CoAuthor_Influence_Velocity"
    ]:
        if col not in merged.columns:
            print(f"⚠️ Missing {col} in merged; creating default zeros.")
            merged[col] = 0
        merged[col] = pd.to_numeric(merged[col], errors="coerce").fillna(0)

    # Apply back to base dataset (only updated rows)
    if not FORCE_ALL:
        base_df.update(merged)

    merged["Integration_Timestamp"] = datetime.datetime.now().isoformat()

    # Schema-lock to 40 columns
    if len(merged.columns) > SCHEMA_COLUMNS:
        merged = merged.iloc[:, :SCHEMA_COLUMNS]

    print(f"✅ Integrated {len(merged)} rows ({'all' if FORCE_ALL else 'Frontier/Foundational only'}).")
    return merged

# ------------------------------------------------------
# Main Integration Routine
# ------------------------------------------------------
def main():
    print("=======================================================")
    print(" AI Talent Engine — Real-Time Citation Integrator v2.0")
    print(f" {datetime.datetime.now()}")
    print("=======================================================")

    if not os.path.exists(REALTIME):
        print(f"❌ Missing {REALTIME} — run fetch_realtime_citation_data.py first.")
        return

    rt = pd.read_csv(REALTIME)
    print(f"📄 Loaded real-time metrics: {len(rt)} rows, {len(rt.columns)} columns")

    phase6 = pd.read_csv(PHASE6)
    phase7 = pd.read_csv(PHASE7)

    merged6 = merge_realtime(phase6, rt, "Phase 6")
    merged7 = merge_realtime(phase7, rt, "Phase 7")

    merged6.to_csv(OUT_PHASE6, index=False)
    merged7.to_csv(OUT_PHASE7, index=False)

    sha6 = sha256sum(OUT_PHASE6)
    sha7 = sha256sum(OUT_PHASE7)

    # Governance log
    summary = {
        "timestamp": datetime.datetime.now().isoformat(),
        "system": platform.node(),
        "merged_phase6_rows": len(merged6),
        "merged_phase7_rows": len(merged7),
        "sha_phase6": sha6,
        "sha_phase7": sha7,
        "force_all": FORCE_ALL,
        "focus_roles": "Frontier/Foundational AI" if not FORCE_ALL else "All AI-classified roles",
        "realtime_columns": rt.columns.tolist(),
        "status": "Integration complete — schema-locked"
    }

    with open(LOG_JSON, "w") as jf:
        json.dump(summary, jf, indent=2)

    print("🔒 Integration summary written →", LOG_JSON)
    print("✅ Real-time metrics merged successfully.")
    print("=======================================================")

if __name__ == "__main__":
    main()
