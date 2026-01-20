#!/usr/bin/env python3
import pandas as pd, os, numpy as np

DATA_DIR = "data"
OUT_DIR = "output"
os.makedirs(OUT_DIR, exist_ok=True)

report = []

print("🔎 Scanning all CSVs in data/ for column type consistency...\n")
for f in os.listdir(DATA_DIR):
    if not f.endswith(".csv"): continue
    path = os.path.join(DATA_DIR, f)
    try:
        df = pd.read_csv(path, nrows=5)
        for c in df.columns:
            sample_vals = df[c].dropna().astype(str).head(5).tolist()
            dtype = str(df[c].dtype)
            inferred = "numeric" if np.issubdtype(df[c].dtype, np.number) else "string"
            report.append({
                "file": f,
                "column": c,
                "dtype": dtype,
                "inferred_type": inferred,
                "sample_values": "; ".join(sample_vals)
            })
    except Exception as e:
        print(f"⚠️ Could not read {f}: {e}")

outpath = os.path.join(OUT_DIR, "column_type_report.csv")
pd.DataFrame(report).to_csv(outpath, index=False)
print(f"✅ Column type audit written to {outpath}")
