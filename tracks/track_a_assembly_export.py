import argparse
import pandas as pd
from contracts.canonical_people_schema import enforce_canonical


def main():
    ap = argparse.ArgumentParser(
        description="Track A — Assembly / Export (Phase v1.3)"
    )
    ap.add_argument("--input", required=True, help="Track B output CSV")
    ap.add_argument("--output", required=True, help="Final assembled CSV")
    args = ap.parse_args()

    print("========================================")
    print(" Track A — Assembly / Export")
    print("========================================")

    df = pd.read_csv(args.input)
df = enforce_canonical(df)
    df.to_csv(args.output, index=False)

    print("Track A OK")
    print(f"Final output: {args.output}")
    print("========================================")


if __name__ == "__main__":
    main()
