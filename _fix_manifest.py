from pathlib import Path
import json
from datetime import datetime

def write_run_manifest(scenario: str, run_id: str):
    manifest_dir = Path("outputs/manifests")
    manifest_dir.mkdir(parents=True, exist_ok=True)

    manifest_path = manifest_dir / f"run_manifest_{scenario}_{run_id}.json"

    payload = {
        "scenario": scenario,
        "run_id": run_id,
        "timestamp_utc": datetime.utcnow().isoformat(),
        "status": "success",
        "artifacts": {
            "leads_master": f"outputs/leads/run_{run_id}/LEADS_MASTER_{scenario}_{run_id}.csv",
            "people_master": "outputs/people/people_master.csv"
        }
    }

    manifest_path.write_text(json.dumps(payload, indent=2))
    print(f"✅ RUN MANIFEST written → {manifest_path}")
    return manifest_path
