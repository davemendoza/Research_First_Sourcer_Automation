#!/usr/bin/env python3
import pandas as pd, os

DATA_DIR, OUT_DIR = "data", "output"

def main():
    print("🔍 Auditing data directory...\n")
    stats = []
    for f in os.listdir(DATA_DIR):
        if not f.endswith(".csv"): continue
        path = os.path.join(DATA_DIR, f)
        try:
            df = pd.read_csv(path)
            stats.append({
                "file": f, "rows": len(df), "columns": len(df.columns),
                "has_email": "email" in df.columns,
                "has_signal_score": "signal_score" in df.columns
            })
        except Exception as e:
            print(f"⚠️ Could not read {f}: {e}")
    pd.DataFrame(stats).to_csv(os.path.join(OUT_DIR, "inventory_audit_summary.csv"), index=False)
    print("✅ Audit complete.")

if __name__ == "__main__": main()
