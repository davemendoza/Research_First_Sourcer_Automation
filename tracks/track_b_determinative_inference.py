import argparse
import pandas as pd


def main():
    ap = argparse.ArgumentParser(
        description="Track B — Determinative Inference (point-in-time, Phase v1.3)"
    )
    ap.add_argument("--input", required=True, help="Track C output CSV")
    ap.add_argument("--output", required=True, help="Track B output CSV")
    ap.add_argument(
        "--temporal-flags",
        nargs="*",
        default=[],
        help="Externally supplied temporal flags (NEW_SIGNAL, ACCELERATION, CLUSTERED_ACTIVITY)"
    )
    args = ap.parse_args()

    df = pd.read_csv(args.input)

    # Determinative inference remains deterministic and point-in-time
    df["Determinative_Flags"] = ",".join(args.temporal_flags)

    df.to_csv(args.output, index=False)

    print("Track B OK")
    print(f"Output: {args.output}")


if __name__ == "__main__":
    main()
