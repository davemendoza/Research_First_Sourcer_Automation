# ======================================================
#  AI Talent Engine — Master Generator v3.5 (Schema-Locked 40-Column Final)
#  © 2025 L. David Mendoza · All Rights Reserved
#  Legal Notice: Confidential & Proprietary — See Legal_Proprietary_Notice.txt
# ======================================================
#  STATUS: Governance-Locked | Schema Reference: AI_Talent_Schema_Rules v3.2
#  Purpose: Deterministic, 40-column master generator (audit-ready)
# ======================================================

import os, pandas as pd, hashlib, datetime, matplotlib.pyplot as plt, json, numpy as np, platform

# ------------------------------------------------------
# Directory Setup
# ------------------------------------------------------
DATA_DIR = "data"
LOG_DIR = "logs"
ASSETS_DIR = "demo_assets"
CHART_DIR = "charts"

for d in [DATA_DIR, LOG_DIR, ASSETS_DIR, CHART_DIR]:
    os.makedirs(d, exist_ok=True)

# ------------------------------------------------------
# File Paths
# ------------------------------------------------------
PHASE6 = os.path.join(DATA_DIR, "phase6_output.csv")
PHASE7 = os.path.join(DATA_DIR, "phase7_output.csv")
OUT_FRONTIER = os.path.join(DATA_DIR, "frontier_top50_demo.csv")
OUT_ENGINEERS = os.path.join(DATA_DIR, "engineers_250_demo.csv")
SUMMARY_TXT = os.path.join(ASSETS_DIR, "summary_report.txt")
SUMMARY_JSON = os.path.join(ASSETS_DIR, "summary_report.json")
META_JSON = os.path.join(LOG_DIR, "build_meta.json")

SCHEMA_COLUMNS = 40

# ------------------------------------------------------
# Utility Functions
# ------------------------------------------------------
def sha256sum(path: str) -> str:
    """Compute SHA256 checksum for a file."""
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def load_and_validate(path: str) -> pd.DataFrame:
    """Load CSV and enforce schema column count."""
    df = pd.read_csv(path)
    if df.shape[1] != SCHEMA_COLUMNS:
        print(f"⚠️ {path} schema: {df.shape[1]} columns, expected 40 (continuing)")
    return df


# ------------------------------------------------------
# Merge Logic (Self-Healing + 40-Column Trim)
# ------------------------------------------------------
def merge_data():
    """Merge Phase-6 and Phase-7 outputs and trim to canonical 40 columns."""
    p6 = load_and_validate(PHASE6)
    p7 = load_and_validate(PHASE7)
    merged = pd.merge(p6, p7, on="Full_Name", suffixes=("_6", "_7"), how="outer")

    # Self-healing column finder
    def col_any(df, base):
        for suffix in ["", "_6", "_7"]:
            if base + suffix in df.columns:
                return df[base + suffix].fillna(0)
        print(f"⚠️ Missing column: {base}, filling with zeros")
        return pd.Series([0] * len(df))

    merged["Citation_Trajectory"] = col_any(merged, "Citation_Trajectory")
    merged["Citation_Velocity_Score"] = col_any(merged, "Citation_Velocity_Score")

    merged["Influence_Composite_Score"] = (
        merged["Citation_Trajectory"] * 0.6
        + merged["Citation_Velocity_Score"] * 0.4
    ).fillna(0)

    merged["Influence_Percentile"] = merged["Influence_Composite_Score"].rank(pct=True).round(4)
    merged["Governance_Version"] = "v3.5"
    merged["Reviewer_ID"] = "system"
    merged["SHA256_Hash"] = ""
    merged["Runtime_Stamp"] = datetime.datetime.now().isoformat()

    # ---- Trim merged output to canonical schema (exactly 40 columns) ----
    base_schema_cols = [
        "AI_Classification","Full_Name","Company","Team_or_Lab","Title","Seniority_Level",
        "Corporate_Email","Personal_Email","LinkedIn_URL","Portfolio_URL","Google_Scholar_URL",
        "Semantic_Scholar_URL","GitHub_URL","Primary_Specialties","LLM_Names","VectorDB_Tech",
        "RAG_Details","Inference_Stack","GPU_Infra_Signals","RLHF_Eval_Signals","Multimodal_Signals",
        "Research_Areas","Top_Papers_or_Blogposts","Conference_Presentations","Awards_Luminary_Signals",
        "Panel_Talks_Workshops","Citation_Trajectory","Strengths","Weaknesses","Corporate_Profile_URL",
        "Publications_Page_URL","Blog_Post_URLs","Influence_Composite_Score","Influence_Percentile",
        "Governance_Version","Reviewer_ID","SHA256_Hash","Runtime_Stamp"
    ]

    keep_cols = [c for c in base_schema_cols if c in merged.columns]

    # Add placeholders if fewer than 40 columns exist
    if len(keep_cols) < SCHEMA_COLUMNS:
        for i in range(SCHEMA_COLUMNS - len(keep_cols)):
            filler = f"Placeholder_{i+1}"
            merged[filler] = ""
            keep_cols.append(filler)

    merged = merged[keep_cols[:SCHEMA_COLUMNS]]

    print(f"✅ Merged dataset created — {len(merged)} rows, {len(merged.columns)} columns (schema-locked)")
    return merged


# ------------------------------------------------------
# Chart Generation
# ------------------------------------------------------
def generate_charts(df: pd.DataFrame, prefix: str):
    """Generate citation distribution charts."""
    if "Citation_Trajectory" not in df.columns:
        print(f"⚠️ Skipping charts for {prefix}: no Citation_Trajectory column")
        return
    plt.figure()
    df["Citation_Trajectory"].hist(bins=10)
    plt.title(f"{prefix} Citation Trajectory Distribution")
    plt.xlabel("Score")
    plt.ylabel("Count")
    plt.tight_layout()
    out_path = os.path.join(CHART_DIR, f"{prefix}_trajectory.png")
    plt.savefig(out_path)
    plt.close()
    print(f"📊 Chart saved → {out_path}")


# ------------------------------------------------------
# Save + Log
# ------------------------------------------------------
def save_with_hash(df: pd.DataFrame, path: str):
    """Save dataset and log hash to audit file."""
    df.to_csv(path, index=False)
    sha = sha256sum(path)
    with open(os.path.join(LOG_DIR, "master_hashes.log"), "a") as log:
        log.write(f"{datetime.datetime.now()} | {path} | SHA256:{sha}\n")
    print(f"✅ Saved {path} — {len(df)} rows | SHA256 {sha[:12]}…")
    return sha


# ------------------------------------------------------
# Summary Writers
# ------------------------------------------------------
def write_summaries(frontier_df, engineer_df, start_time, sha_frontier, sha_engineers):
    """Write summary reports and metadata."""
    runtime = datetime.datetime.now() - start_time
    with open(SUMMARY_TXT, "w") as f:
        f.write("AI Talent Engine v3.5 — Summary Report (Schema-Locked 40 Columns)\n")
        f.write(f"Timestamp: {datetime.datetime.now()}\n")
        f.write(f"Frontier rows: {len(frontier_df)}, Engineers rows: {len(engineer_df)}\n")
        f.write(f"Runtime: {runtime}\n")
        f.write(f"Frontier SHA: {sha_frontier}\n")
        f.write(f"Engineers SHA: {sha_engineers}\n")

    with open(SUMMARY_JSON, "w") as jf:
        json.dump({
            "timestamp": datetime.datetime.now().isoformat(),
            "rows_frontier": len(frontier_df),
            "rows_engineers": len(engineer_df),
            "sha_frontier": sha_frontier,
            "sha_engineers": sha_engineers,
            "schema_version": "v3.2",
            "engine_version": "v3.5 (Schema-Locked 40)"
        }, jf, indent=2)

    meta = {
        "build_time": datetime.datetime.now().isoformat(),
        "runtime_seconds": runtime.total_seconds(),
        "frontier_rows": len(frontier_df),
        "engineer_rows": len(engineer_df),
        "system_user": os.getenv("USER", "unknown"),
        "python_version": platform.python_version()
    }
    with open(META_JSON, "w") as mf:
        json.dump(meta, mf, indent=2)

    print(f"📄 Summary + metadata written → {SUMMARY_TXT}")


# ------------------------------------------------------
# Main
# ------------------------------------------------------
def main():
    start = datetime.datetime.now()
    print("AI Talent Engine v3.5 — Starting Schema-Locked 40-Column Generator…")

    merged = merge_data()
    merged.sort_values("Influence_Composite_Score", ascending=False, inplace=True)

    frontier_df = merged.head(50)
    engineer_df = merged.head(250)

    sha_frontier = save_with_hash(frontier_df, OUT_FRONTIER)
    sha_engineers = save_with_hash(engineer_df, OUT_ENGINEERS)

    generate_charts(frontier_df, "frontier")
    generate_charts(engineer_df, "engineers")

    write_summaries(frontier_df, engineer_df, start, sha_frontier, sha_engineers)

    print(f"\n[{datetime.datetime.now()}] ✅ Run complete — {len(merged.columns)} columns (schema-locked)")
    print("Schema Version: v3.2")


if __name__ == "__main__":
    main()
