import json
import faiss
import numpy as np
import os

INDEX_PATH = "vector_db/faiss.index"
DATA_PATH = "outputs/gold_standard.json"

def load_index():
    if not os.path.exists(INDEX_PATH):
        raise RuntimeError("FAISS index missing")
    return faiss.read_index(INDEX_PATH)

def load_data():
    with open(DATA_PATH, "r") as f:
        return json.load(f)

def vector_search(query_vector, k=10):
    index = load_index()
    distances, indices = index.search(query_vector, k)
    data = load_data()

    results = []
    for idx in indices[0]:
        if idx < len(data):
            results.append(data[idx])

    return results
