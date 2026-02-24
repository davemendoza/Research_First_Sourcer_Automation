# ==================================================================================================
# AI TALENT ENGINE — VECTOR INDEX BUILDER
# © 2026 L. David Mendoza. All Rights Reserved.
# ==================================================================================================

import os
import json
import numpy as np
import hashlib

VECTOR_DIR = "vector_db"
INDEX_FILE = os.path.join(VECTOR_DIR, "faiss.index")
EMBED_FILE = os.path.join(VECTOR_DIR, "identity_embeddings.npy")
META_FILE = os.path.join(VECTOR_DIR, "identity_metadata.json")

SOURCE_FILE = "outputs/gold_standard.json"

EMBED_DIM = 384

os.makedirs(VECTOR_DIR, exist_ok=True)

def deterministic_embedding(text):
    h = hashlib.sha256(text.encode()).digest()
    np.random.seed(int.from_bytes(h[:4], "little"))
    return np.random.rand(EMBED_DIM).astype("float32")

def load_identities():
    if not os.path.exists(SOURCE_FILE):
        raise RuntimeError(f"Missing source file: {SOURCE_FILE}")
    with open(SOURCE_FILE, "r") as f:
        data = json.load(f)
    return data

def build_index():

    identities = load_identities()

    vectors = []
    metadata = []

    for identity in identities:

        name = identity.get("Name") or identity.get("name") or ""
        role = identity.get("Role") or identity.get("role") or ""
        company = identity.get("Company") or identity.get("company") or ""

        combined = f"{name} {role} {company}"

        vec = deterministic_embedding(combined)

        vectors.append(vec)

        metadata.append({
            "name": name,
            "role": role,
            "company": company
        })

    vectors = np.vstack(vectors)

    np.save(EMBED_FILE, vectors)

    with open(META_FILE, "w") as f:
        json.dump(metadata, f)

    try:
        import faiss

        index = faiss.IndexFlatL2(EMBED_DIM)
        index.add(vectors)
        faiss.write_index(index, INDEX_FILE)

        print("FAISS index built successfully")

    except Exception as e:

        print("FAISS not available, using numpy fallback index")
        np.save(INDEX_FILE + ".npy", vectors)

    print("Vector index population complete")

if __name__ == "__main__":
    build_index()
