#!/usr/bin/env python3
import json, pathlib, hashlib, sys

INV = pathlib.Path.home() / "Desktop" / "INVENTORY_FINAL"
FILES = [
    "AI_Talent_Repo_Inventory.json",
    "AI_Talent_Schema_Inventory.txt",
    "AI_Talent_Inventory_Manifest.json",
]

for f in FILES[:-1]:
    if not (INV / f).exists():
        sys.exit(f"❌ Missing required inventory file: {f}")

manifest = {
    "location": "INVENTORY_FINAL",
    "contract": "exactly three files, no timestamps, no zips",
    "artifacts": FILES[:-1],
    "hashes": {
        f: hashlib.sha256((INV / f).read_bytes()).hexdigest()
        for f in FILES[:-1]
    }
}

(INV / FILES[-1]).write_text(json.dumps(manifest, indent=2))
print("✅ Manifest repaired and aligned to contract")
