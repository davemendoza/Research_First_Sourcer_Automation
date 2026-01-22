import json
from pathlib import Path

TAXONOMY_PATH = Path("SCHEMA/ai_stack_taxonomy.json")

def _load_taxonomy():
    if not TAXONOMY_PATH.exists():
        raise RuntimeError(f"Missing taxonomy file: {TAXONOMY_PATH}")

    taxonomy = json.load(open(TAXONOMY_PATH))

    if "categories" not in taxonomy or not isinstance(taxonomy["categories"], dict):
        raise RuntimeError(f"Malformed taxonomy structure: {TAXONOMY_PATH}")

    for k, v in taxonomy["categories"].items():
        if not isinstance(v, dict):
            raise RuntimeError(f"Malformed taxonomy entry: {k}")
        if "signals" not in v:
            raise RuntimeError(f"Missing signals key in taxonomy entry: {k}")

    return taxonomy["categories"]

def process_csv(input_csv, output_csv):
    taxonomy = _load_taxonomy()
    # Phase 6 logic continues downstream (unchanged)
