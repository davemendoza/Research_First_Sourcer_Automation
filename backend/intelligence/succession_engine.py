"""
Frontier Succession Intelligence Engine
Fully integrated with FAISS vector DB and registries
"""

import os
import json
import numpy as np
import faiss
from datetime import datetime

BASE = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))

IDENTITY_REGISTRY = os.path.join(BASE, "outputs", "identity_registry.json")
TRAJECTORY_REGISTRY = os.path.join(BASE, "outputs", "trajectory_registry.json")
EVIDENCE_REGISTRY = os.path.join(BASE, "outputs", "evidence_registry.json")
VECTOR_SIGNAL_REGISTRY = os.path.join(BASE, "outputs", "vector_signal_registry.json")

FAISS_INDEX = os.path.join(BASE, "vector_db", "faiss.index")
EMBEDDINGS = os.path.join(BASE, "vector_db", "identity_embeddings.npy")

OUTPUT = os.path.join(BASE, "outputs", "succession_registry.json")

TOP_K = 10

def load_json(path):
    if not os.path.exists(path):
        return {}
    with open(path, "r") as f:
        return json.load(f)

def load_faiss():
    if not os.path.exists(FAISS_INDEX):
        raise RuntimeError("FAISS index not found")
    return faiss.read_index(FAISS_INDEX)

def load_embeddings():
    if not os.path.exists(EMBEDDINGS):
        raise RuntimeError("Embeddings not found")
    return np.load(EMBEDDINGS)

def compute_successors():

    identity = load_json(IDENTITY_REGISTRY)
    trajectory = load_json(TRAJECTORY_REGISTRY)

    if not identity:
        return {}

    index = load_faiss()
    embeddings = load_embeddings()

    keys = list(identity.keys())

    successors = {}

    for i, key in enumerate(keys):

        vector = embeddings[i].reshape(1, -1)

        distances, indices = index.search(vector, TOP_K)

        candidates = []

        for j, idx in enumerate(indices[0]):

            if idx == i:
                continue

            if idx >= len(keys):
                continue

            candidate_key = keys[idx]

            similarity = float(1 - distances[0][j])

            trajectory_score = trajectory.get(candidate_key, {}).get("trajectory_score", 0.5)

            readiness = similarity * trajectory_score

            candidates.append({
                "identity_key": candidate_key,
                "similarity": similarity,
                "trajectory_score": trajectory_score,
                "readiness_score": readiness
            })

        candidates.sort(key=lambda x: x["readiness_score"], reverse=True)

        successors[key] = candidates[:5]

    return successors

def generate():

    successors = compute_successors()

    registry = {
        "generated_at": datetime.utcnow().isoformat(),
        "total_identities": len(successors),
        "successors": successors
    }

    with open(OUTPUT, "w") as f:
        json.dump(registry, f, indent=2)

    return registry

if __name__ == "__main__":
    print(generate())
