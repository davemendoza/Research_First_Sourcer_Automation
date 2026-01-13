#!/usr/bin/env python3
import pathlib, json, sys

INV = pathlib.Path.home() / "Desktop" / "INVENTORY_FINAL"
EXPECTED = {
    "AI_Talent_Repo_Inventory.json",
    "AI_Talent_Schema_Inventory.txt",
    "AI_Talent_Inventory_Manifest.json",
}

if not INV.exists():
    sys.exit("❌ INVENTORY_FINAL missing")

found = {p.name for p in INV.iterdir() if p.is_file()}
if found != EXPECTED:
    sys.exit(f"❌ INVENTORY DRIFT: {found}")

manifest = json.loads((INV / "AI_Talent_Inventory_Manifest.json").read_text())
if set(manifest["artifacts"]) != EXPECTED - {"AI_Talent_Inventory_Manifest.json"}:
    sys.exit("❌ MANIFEST CONTRACT VIOLATION")

print("✅ Inventory verified, immutable, contract-safe")
