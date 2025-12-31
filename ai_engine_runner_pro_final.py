#!/usr/bin/env python3
import pandas as pd, numpy as np, os, datetime
from sklearn.preprocessing import MinMaxScaler

SRC = "data/merged_enriched_talent.csv"
OUTDIR = "output"
os.makedirs(OUTDIR, exist_ok=True)

print("🚀 Loading dataset:", SRC)
df = pd.read_csv(SRC)

# Ensure key columns exist
for col in ["signal_score", "influence_math", "influence_percentile"]:
    if col not in df.columns:
        df[col] = 0

# Convert to numeric safely (avoid UNKNOWN / strings)
for col in ["signal_score", "influence_math", "influence_percentile"]:
    df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

# Normalize and compute composite score
scaler = MinMaxScaler()
scaled = scaler.fit_transform(df[["signal_score", "influence_math", "influence_percentile"]])
df["final_signal_score"] = np.mean(scaled, axis=1)

# Rank and export
df = df.sort_values("final_signal_score", ascending=False).reset_index(drop=True)
df.insert(0, "rank", np.arange(1, len(df) + 1))

ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
outfile = os.path.join(OUTDIR, f"final_talent_ranking_{ts}.csv")
df.to_csv(outfile, index=False)

print(f"✅ Final ranked dataset written to {outfile}")
print(f"🧠 Total candidates ranked: {len(df)}")
print("Top columns:", list(df.columns)[:12])
