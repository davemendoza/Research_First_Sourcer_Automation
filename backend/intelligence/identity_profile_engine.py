import json
import os

DATA_PATH = "outputs/gold_standard.json"

def get_identity_profile(identity_key):

    if not os.path.exists(DATA_PATH):
        raise Exception("gold_standard.json missing")

    with open(DATA_PATH) as f:
        data = json.load(f)

    for record in data:

        if record.get("Identity_Key") == identity_key:
            return {
                "name": record.get("Name"),
                "organization": record.get("Organization"),
                "signal_score": record.get("Signal_Score"),
                "trajectory_score": record.get("Trajectory_Score"),
                "github": record.get("GitHub"),
                "evidence": record.get("Evidence_URLs", [])
            }

    raise Exception("Identity not found")
