import json
from pathlib import Path

TAXONOMY_PATH = Path("SCHEMA/ai_stack_taxonomy.json")

def _load_taxonomy():
    if not TAXONOMY_PATH.exists():
        raise RuntimeError(f"Missing taxonomy file: {TAXONOMY_PATH}")

    taxonomy = json.load(open(TAXONOMY_PATH))

    if "categories" not in taxonomy:
        raise RuntimeError(f"Malformed taxonomy structure: {TAXONOMY_PATH}")

    categories = taxonomy["categories"]

    if not isinstance(categories, dict):
        raise RuntimeError(f"Malformed taxonomy structure: {TAXONOMY_PATH}")

    for name, block in categories.items():
        if not isinstance(block, dict):
            raise RuntimeError(f"Malformed taxonomy entry: {name}")
        if "signals" not in block:
            raise RuntimeError(f"Missing signals key in taxonomy entry: {name}")

    return categories

def process_csv(input_csv, output_csv):
    taxonomy = _load_taxonomy()
    # Phase 6 logic continues downstream (unchanged)
