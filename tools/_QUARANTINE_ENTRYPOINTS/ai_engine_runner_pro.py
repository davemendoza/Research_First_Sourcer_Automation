from contracts.canonical_people_schema import enforce_canonical
#!/usr/bin/env python3
"""
AI Talent Engine – Permanent Build (v1.0)
✅ Auto-detects and merges Phase 6 + Phase 7 + MASTER_SEED_HUBS
✅ Normalizes and ranks composite Signal_Score
✅ Outputs /output/final_talent_ranking_<timestamp>.csv
"""

import os, sys, pandas as pd, numpy as np, datetime as dt
from sklearn.preprocessing import MinMaxScaler

ROOT = os.path.expanduser("~/Desktop/Research_First_Sourcer_Automation")
DATADIR = os.path.join(ROOT, "data")
OUTDIR = os.path.join(ROOT, "output")
os.makedirs(OUTDIR, exist_ok=True)

# expected inputs
FILES = {
    "phase6": os.path.join(DATADIR, "phase6_output_fixed.csv"),
    "phase7": os.path.join(DATADIR, "frontier_phase7_enriched_fixed.csv"),
    "seed":   os.path.join(DATADIR, "AI_Talent_Landscape_Seed_Hubs.xlsx"),
}

def safe_load(path, sheet=None):
    if not os.path.exists(path):
        print(f"⚠️  Missing: {path}")
        return pd.DataFrame()
    if path.endswith(".csv"):
        return pd.read_csv(path)
    if path.endswith(".xlsx"):
        x = pd.ExcelFile(path)
        target = sheet or "MASTER_SEED_HUBS"
        if target not in x.sheet_names:
            print(f"⚠️  Sheet '{target}' not found in {path}. Found: {x.sheet_names}")
            return pd.DataFrame()
        return x.parse(target)
    return pd.DataFrame()

def normalize_cols(df):
    df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]
    return df

def compute_signal(df):
    # choose numeric columns likely to represent scores
    score_cols = [c for c in df.columns if "score" in c or "signal" in c or "weight" in c]
    score_cols = [c for c in score_cols if pd.api.types.is_numeric_dtype(df[c])]
    if not score_cols:
        print("⚠️  No numeric score columns detected.")
        df["signal_score"] = 0
        return df
    scaler = MinMaxScaler(feature_range=(0,100))
    df["signal_score"] = scaler.fit_transform(df[score_cols].sum(axis=1).values.reshape(-1,1))
    df["signal_score"] = df["signal_score"].round(2)
    return df

def merge_all():
    dfs = []
    for key, path in FILES.items():
        print(f"📂 Loading {key}: {os.path.basename(path)}")
        if key == "seed":
            df = safe_load(path, sheet="MASTER_SEED_HUBS")
        else:
            df = safe_load(path)
        if not df.empty:
            df = normalize_cols(df)
            df["source_tag"] = key
            dfs.append(df)
    if not dfs:
        print("❌ No valid data sources found.")
        sys.exit(1)
    merged = pd.concat(dfs, ignore_index=True)
    merged = merged.loc[:, ~merged.columns.duplicated()]
    return merged

def main():
    print("🚀 Running AI Talent Engine Pro ...")
    df = merge_all()
    df = compute_signal(df)

    keep_cols = [c for c in df.columns if any(k in c for k in
                 ["name","org","affiliation","role","url","signal","source","tier","citation","skill","github","linkedin","resume"])]
    ranked = df[keep_cols].copy()
    ranked = ranked.sort_values("signal_score", ascending=False)
    ranked["rank"] = range(1, len(ranked)+1)

    ts = dt.datetime.now().strftime("%Y%m%d_%H%M%S")
    outpath = os.path.join(OUTDIR, f"final_talent_ranking_{ts}.csv")
ranked = enforce_canonical(ranked)
    ranked.to_csv(outpath, index=False)
    print(f"✅ Final ranked CSV written: {outpath}")

    try:
        os.system(f"open '{outpath}'")
    except Exception as e:
        print(f"⚠️ Could not auto-open: {e}")

if __name__ == "__main__":
    main()
