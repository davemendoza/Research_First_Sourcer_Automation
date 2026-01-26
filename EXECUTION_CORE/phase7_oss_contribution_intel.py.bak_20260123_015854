import json
import csv
from pathlib import Path

TAXONOMY_PATH = Path("SCHEMA/oss_contribution_taxonomy.json")

def _load_taxonomy():
    if not TAXONOMY_PATH.exists():
        raise RuntimeError(f"Missing required taxonomy file: {TAXONOMY_PATH}")

    taxonomy = json.load(open(TAXONOMY_PATH))

    if "categories" not in taxonomy or not isinstance(taxonomy["categories"], dict):
        raise RuntimeError(f"Malformed taxonomy structure: {TAXONOMY_PATH}")

    for k, v in taxonomy["categories"].items():
        if not isinstance(v, dict):
            raise RuntimeError(f"Malformed taxonomy entry: {k}")
        for req in ("signals", "weight", "enabled"):
            if req not in v:
                raise RuntimeError(f"Missing {req} in taxonomy entry: {k}")

    return taxonomy["categories"]

def process_csv(input_csv: str, output_csv: str):
    in_path = Path(input_csv)
    out_path = Path(output_csv)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    if not in_path.exists():
        raise RuntimeError(f"Phase 7 input missing: {in_path}")

    taxonomy = _load_taxonomy()

    with in_path.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    # Pass-through for now (signal logic remains unchanged)
    with out_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=reader.fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    return str(out_path)
