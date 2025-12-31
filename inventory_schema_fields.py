#!/usr/bin/env python3
import os, pandas as pd

ROOT = os.path.expanduser("~/Desktop/Research_First_Sourcer_Automation/data")
inventory = {}
print(f"🔍 Scanning data folder: {ROOT}")

for root, dirs, files in os.walk(ROOT):
    for f in files:
        if not (f.endswith(".csv") or f.endswith(".xlsx")):
            continue
        path = os.path.join(root, f)
        try:
            if f.endswith(".csv"):
                df = pd.read_csv(path, nrows=3)
            else:
                x = pd.ExcelFile(path)
                for sheet in x.sheet_names:
                    df = x.parse(sheet, nrows=3)
                    inventory[f"{f}:{sheet}"] = list(df.columns)
                continue
            inventory[f] = list(df.columns)
        except Exception as e:
            print(f"⚠️  Could not read {f}: {e}")

# flatten and deduplicate columns
all_cols = sorted({c.strip() for cols in inventory.values() for c in cols if isinstance(c, str)})
inv_path = os.path.join(ROOT, "talent_schema_inventory.csv")
pd.DataFrame({"All_Columns": all_cols}).to_csv(inv_path, index=False)

print(f"\n✅ Inventory complete: {len(inventory)} files scanned.")
print(f"🧱 Total unique columns: {len(all_cols)}")
print(f"📄 Saved schema inventory: {inv_path}\n")
for name, cols in list(inventory.items())[:5]:
    print(f"📘 {name} → {len(cols)} columns")
