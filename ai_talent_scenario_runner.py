from contracts.canonical_people_schema import enforce_canonical
#!/usr/bin/env python3
import os, sys
from datetime import datetime
import pandas as pd

OUTPUT_DIR = "output"
SCENARIO_DIR = os.path.join(OUTPUT_DIR, "scenarios")

SCENARIOS = [
    ("TOP_200_OVERALL", None, 200),
    ("TOP_300_OVERALL", None, 300),
    ("FOUNDATIONAL_TOP_200", ["foundational", "frontier", "research"], 200),
    ("APPLIED_AI_TOP_300", ["engineer", "applied", "ml"], 300),
    ("INFRA_TOP_300", ["infra", "platform", "systems"], 300),
]

def latest_csv():
    csvs = sorted(f for f in os.listdir(OUTPUT_DIR) if f.endswith(".csv"))
    if not csvs:
        sys.exit("❌ NO CSV IN output/")
    return os.path.join(OUTPUT_DIR, csvs[-1])

def detect_score_column(cols):
    candidates = [
        "final_signal_score",
        "signal_score",
        "final_score",
        "total_score",
        "score",
        "rank_score",
    ]
    for c in candidates:
        if c in cols:
            return c
    # fallback: first numeric column
    return None

def main():
    src = latest_csv()
    print(f"USING SOURCE: {src}")

    df = pd.read_csv(src)
    df.columns = [c.lower() for c in df.columns]

    print("COLUMNS:", list(df.columns))

    score_col = detect_score_column(df.columns)
    if not score_col:
        # fallback: sort by first numeric column
        numeric_cols = df.select_dtypes(include="number").columns.tolist()
        if not numeric_cols:
            sys.exit("❌ NO NUMERIC COLUMNS TO SORT BY")
        score_col = numeric_cols[0]
        print(f"⚠️ FALLBACK SCORE COLUMN: {score_col}")
    else:
        print(f"✅ USING SCORE COLUMN: {score_col}")

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    outdir = os.path.join(SCENARIO_DIR, ts)
    os.makedirs(outdir, exist_ok=True)

    all_rows = []

    for name, role_terms, limit in SCENARIOS:
        sdf = df.copy()

        if role_terms and "role_type" in sdf.columns:
            sdf = sdf[sdf["role_type"].astype(str).str.lower()
                      .str.contains("|".join(role_terms), na=False)]

        sdf = sdf.sort_values(score_col, ascending=False).head(limit)

        if sdf.empty:
            print(f"NO MATCHES FOR {name}")
            continue

        p = os.path.join(outdir, f"scenario_{name}.csv")
        sdf.to_csv(p, index=False)
        print(f"WROTE {len(sdf)} → {p}")

        sdf["scenario"] = name
        all_rows.append(sdf)

    if all_rows:
        m = pd.concat(all_rows).drop_duplicates()
     m = enforce_canonical(m)
   mp = os.path.join(outdir, f"scenarios_ALL_{ts}.csv")
        m.to_csv(mp, index=False)
        print(f"\n🔥 MASTER → {mp} ({len(m)} rows)")
    else:
        print("\n❌ NO OUTPUT")

if __name__ == "__main__":
    main()
