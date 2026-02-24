import os

def verify_indexes():

    required = [
        "vector_db/faiss.index",
        "outputs/ecosystem_graph.json",
        "outputs/gold_standard.json"
    ]

    missing = [f for f in required if not os.path.exists(f)]

    if missing:
        raise Exception(f"Missing intelligence files: {missing}")

    return True
