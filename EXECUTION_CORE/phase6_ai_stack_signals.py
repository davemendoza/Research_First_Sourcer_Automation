import csv
import json
from pathlib import Path

TAXONOMY_PATH = Path("SCHEMA/ai_stack_taxonomy.json")

def _load_taxonomy():
    if not TAXONOMY_PATH.exists():
        raise RuntimeError(f"Missing taxonomy file: {TAXONOMY_PATH}")

    taxonomy = json.load(open(TAXONOMY_PATH))
    if "categories" not in taxonomy or not isinstance(taxonomy["categories"], dict):
        raise RuntimeError(f"Malformed taxonomy structure: {TAXONOMY_PATH}")

    for name, block in taxonomy["categories"].items():
        if not isinstance(block, dict):
            raise RuntimeError(f"Malformed taxonomy entry: {name}")
        for req in ("signals", "weight", "enabled"):
            if req not in block:
                raise RuntimeError(f"Missing {req} in taxonomy entry: {name}")

    return taxonomy["categories"]

def process_csv(input_csv: str, output_csv: str) -> str:
    in_path = Path(input_csv)
    out_path = Path(output_csv)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    if not in_path.exists():
        raise RuntimeError(f"Phase 6 input missing: {in_path}")

    _load_taxonomy()  # validate only

    with in_path.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        fieldnames = reader.fieldnames

    if not fieldnames:
        raise RuntimeError("Phase 6 input CSV has no columns")

    with out_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"[OK] Phase 6 output written → {out_path}")
    return str(out_path)
