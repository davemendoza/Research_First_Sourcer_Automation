import os
from datetime import datetime, timezone
from dataclasses import dataclass

def utc_ts():
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")

@dataclass
class RunContext:
    run_id: str
    run_dir: str
    snapshots_dir: str

def create_run_context(outputs_root="outputs"):
    run_id = f"run_{utc_ts()}"
    run_dir = os.path.join(outputs_root, run_id)
    snapshots_dir = os.path.join(run_dir, "snapshots")
    os.makedirs(snapshots_dir, exist_ok=True)
    return RunContext(run_id, run_dir, snapshots_dir)
