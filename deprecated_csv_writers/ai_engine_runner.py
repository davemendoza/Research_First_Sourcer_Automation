from contracts.canonical_people_schema import enforce_canonical
#!/usr/bin/env python3
import os, sys, datetime, pandas as pd
from sklearn.preprocessing import MinMaxScaler
from pathlib import Path

ROOT = Path(os.path.expanduser("~/Desktop/Research_First_Sourcer_Automation"))
OUTDIR = ROOT / "output"
OUTDIR.mkdir(exist_ok=True)

# -------------------------
# DATA SOURCE RESOLUTION
# -------------------------
# DEMO (default):
#   data/AI_Talent_Landscape_Seed_Hubs.xlsx
#
# REAL:
#   export AITE_REAL_DATAFILE=/absolute/path/to/real.xlsx
#
DEFAULT_DATAFILE = ROOT / "data" / "AI_Talent_Landscape_Seed_Hubs.xlsx"
DATAFILE = Path(os.environ.get("AITE_REAL_DATAFILE", DEFAULT_DATAFILE))

if not DATAFILE.exists():
    print(f"❌ Datafile not found: {DATAFILE}")
    sys.exit(1)

# -------------------------
# SCORING LOGIC
# -------------------------

def safe_weighted_signal(row):
    weights = {
        "Seed_Hub_Class": 0.25,
        "Category": 0.25,
        "Source": 0.15,
        "Watchlist_Flag": 0.10,
        "Primary_Enumeration_Target": 0.15,
        "Python_Adapter": 0.10,
    }

    def encode(v):
        if pd.isna(v):
            return 0
        if isinstance(v, (int, float)):
            return float(v)
        return sum(ord(c) for c in str(v)[:6]) / 1000.0

    return sum(encode(row.get(col, 0)) * w for col, w in weights.items())


def load_excel():
    xl = pd.ExcelFile(DATAFILE)
    normalized = {s.strip().lower(): s for s in xl.sheet_names}
    key = "master_seed_hubs"
    if key not in normalized:
        print("❌ Missing MASTER_SEED_HUBS sheet in", DATAFILE)
        sys.exit(1)

    df = xl.parse(normalized[key])
    print(f"📂 Loaded {len(df)} rows from {DATAFILE.name}")
    return df


def compute_signal_scores(df):
    df = df.copy()
    df["Signal_Score"] = df.apply(safe_weighted_signal, axis=1)
    scaler = MinMaxScaler(feature_range=(60, 100))
    df["Signal_Score"] = scaler.fit_transform(df[["Signal_Score"]])
    df["Signal_Score"] = df["Signal_Score"].round(2)
    return df.sort_values("Signal_Score", ascending=False)


def main():
    scenario = "default"
    if "--scenario" in sys.argv:
        scenario = sys.argv[sys.argv.index("--scenario") + 1]

    print(f"🚀 AI Talent Engine")
    print(f"   Scenario : {scenario}")
    print(f"   Datafile : {DATAFILE}")

    df = load_excel()
    ranked = compute_signal_scores(df)

    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    outpath = OUTDIR / f"results_{scenario}_{ts}.csv"
ranked = enforce_canonical(ranked)
    ranked.to_csv(outpath, index=False)

    print(f"✅ CSV written: {outpath}")


if __name__ == "__main__":
    main()
