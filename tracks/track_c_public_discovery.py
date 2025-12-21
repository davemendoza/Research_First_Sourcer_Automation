import argparse
import pandas as pd
from utils.runtime import create_run_context
from utils.snapshot import persist_snapshot


def main():
    ap = argparse.ArgumentParser(
        description="Track C — Public Discovery (point-in-time, Phase v1.3)"
    )
    ap.add_argument(
        "--input",
        required=True,
        help="Path to seed hub Excel or CSV file"
    )
    ap.add_argument(
        "--sheet",
        required=False,
        help="Worksheet name for Excel seed hub (required if Excel has multiple sheets)"
    )
    ap.add_argument(
        "--outputs-root",
        default="outputs",
        help="Root output directory"
    )
    args = ap.parse_args()

    ctx = create_run_context(args.outputs_root)

    # Load input
    if args.input.lower().endswith((".xlsx", ".xls")):
        if not args.sheet:
            raise ValueError(
                "Excel input detected but --sheet was not provided."
            )
        df = pd.read_excel(args.input, sheet_name=args.sheet)
    else:
        df = pd.read_csv(args.input)

    # Ensure stable row identity
    if "Person_ID" not in df.columns:
        df.insert(0, "Person_ID", range(1, len(df) + 1))

    # Provenance tagging (point-in-time only)
    df["Provenance_Source"] = "SeedHub"
    df["Provenance_Run_ID"] = ctx.run_id
    df["Provenance_Stage"] = "TrackC"

    # Snapshot persistence (after provenance tagging)
    snapshot_path = persist_snapshot(
        df=df,
        snapshots_dir=ctx.snapshots_dir,
        stage="track_c_after_provenance",
        run_id=ctx.run_id
    )

    # Persist Track C output
    output_path = f"{ctx.run_dir}/track_c_output.csv"
    df.to_csv(output_path, index=False)

    print("Track C OK")
    print(f"Snapshot: {snapshot_path}")
    print(f"Output:   {output_path}")


if __name__ == "__main__":
    main()
