import os

def persist_snapshot(df, snapshots_dir, stage, run_id):
    os.makedirs(snapshots_dir, exist_ok=True)
    path = os.path.join(
        snapshots_dir,
        f"{stage}_snapshot_{run_id}.csv"
    )
    df.to_csv(path, index=False)
    return path
