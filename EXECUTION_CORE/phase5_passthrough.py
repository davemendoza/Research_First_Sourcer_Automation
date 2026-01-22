import csv
from pathlib import Path

def process_csv(input_csv: str, output_csv: str) -> str:
    in_path = Path(input_csv)
    out_path = Path(output_csv)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    if not in_path.exists():
        raise RuntimeError(f"Phase 5 input missing: {in_path}")

    with in_path.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        fieldnames = reader.fieldnames

    if not fieldnames:
        raise RuntimeError("Phase 5 input CSV has no columns")

    with out_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"[OK] Phase 5 output written -> {out_path}")
    return str(out_path)
