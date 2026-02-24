import json
from datetime import datetime

OUTPUT_DIR = "../../outputs"

def generate_report(query, candidates):

    report = {
        "query": query,
        "timestamp": str(datetime.now()),
        "results": candidates
    }

    path = OUTPUT_DIR + "/executive_report.json"

    with open(path, "w") as f:
        json.dump(report, f, indent=2)

    return path
