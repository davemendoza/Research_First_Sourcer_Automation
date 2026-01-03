from contracts.canonical_people_schema import enforce_canonical
#!/usr/bin/env python3
import pandas as pd, os

SRC1 = "data/phase6_output_fixed_clean.csv"
SRC2 = "data/frontier_phase7_enriched_fixed.csv"
DST = "data/merged_enriched_talent.csv"

df1 = pd.read_csv(SRC1)
df2 = pd.read_csv(SRC2)
merged = pd.concat([df1, df2], ignore_index=True)
merged.drop_duplicates(subset=["full_name", "organization"], inplace=True)
merged = enforce_canonical(merged)
merged.to_csv(DST, index=False)
print(f"✅ Enriched merged dataset written: {DST}")
