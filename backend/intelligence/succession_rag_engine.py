"""
Succession RAG explanation engine
"""

import json, os
from datetime import datetime

BASE = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))

SUCCESSION = os.path.join(BASE,"outputs","succession_registry.json")
EVIDENCE = os.path.join(BASE,"outputs","evidence_registry.json")

OUTPUT = os.path.join(BASE,"outputs","succession_rag_registry.json")

def load(path):
    if not os.path.exists(path):
        return {}
    with open(path) as f:
        return json.load(f)

def generate():

    succession = load(SUCCESSION)
    evidence = load(EVIDENCE)

    explanations = {}

    for incumbent, candidates in succession.get("successors", {}).items():

        explanations[incumbent] = []

        for c in candidates:

            identity = c["identity_key"]

            ev = evidence.get(identity, [])

            explanations[incumbent].append({
                "identity": identity,
                "reason": "High capability similarity and trajectory alignment",
                "evidence_count": len(ev)
            })

    registry = {
        "generated_at": datetime.utcnow().isoformat(),
        "explanations": explanations
    }

    with open(OUTPUT,"w") as f:
        json.dump(registry,f,indent=2)

    return registry

if __name__ == "__main__":
    print(generate())
