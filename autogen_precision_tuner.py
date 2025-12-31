#!/usr/bin/env python3
import pandas as pd, numpy as np, os, yaml, datetime
from sklearn.preprocessing import MinMaxScaler

with open("config.yaml", "r") as f:
    cfg = yaml.safe_load(f)

DATA_DIR = cfg["data_dir"]
OUT_DIR = cfg["output_dir"]
weights = cfg["scoring_weights"]
os.makedirs(OUT_DIR, exist_ok=True)

print("Running Precision Track - Weighted Scoring Engine")

files = sorted([f for f in os.listdir(DATA_DIR) if f.endswith(".csv")])
SRC = os.path.join(DATA_DIR, files[-1])
print(f"Using dataset: {SRC}")

df = pd.read_csv(SRC)

for col in weights.keys():
    if col not in df.columns:
        df[col] = 0

scaler = MinMaxScaler()
scaled = scaler.fit_transform(df[list(weights.keys())])
df_scaled = pd.DataFrame(scaled, columns=list(weights.keys()))
df["final_signal_score"] = np.sum([df_scaled[c]*w for c,w in weights.items()], axis=0)

df = df.sort_values("final_signal_score", ascending=False).reset_index(drop=True)
df.insert(0,"rank",np.arange(1,len(df)+1))

ts=datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
outfile=os.path.join(OUT_DIR,f"precision_ranked_{ts}.csv")
df.to_csv(outfile,index=False)

print(f"Precision weighted ranking saved -> {outfile}")
print(f"Ranked {len(df)} candidates.")
