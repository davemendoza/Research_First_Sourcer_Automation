import json

DATA_PATH = "outputs/gold_standard.json"

def latest_discoveries(limit=25):

    with open(DATA_PATH) as f:
        data = json.load(f)

    return sorted(
        data,
        key=lambda x: x.get("Discovery_Date", ""),
        reverse=True
    )[:limit]
