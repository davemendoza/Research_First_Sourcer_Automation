import json

DATA_PATH = "outputs/gold_standard.json"

def resolve_evidence(identity_key):

    with open(DATA_PATH) as f:
        data = json.load(f)

    for record in data:
        if record.get("Identity_Key") == identity_key:
            return record.get("Evidence_URLs", [])

    return []
