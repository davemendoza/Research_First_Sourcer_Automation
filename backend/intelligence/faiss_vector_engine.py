import faiss
import numpy as np
import os

INDEX_PATH = "vector_db/faiss.index"

def load_index():

    if not os.path.exists(INDEX_PATH):

        dim = 768
        index = faiss.IndexFlatIP(dim)
        faiss.write_index(index, INDEX_PATH)

    return faiss.read_index(INDEX_PATH)

def search(vector, top_k=20):

    index = load_index()

    D,I = index.search(np.array([vector]).astype('float32'), top_k)

    return I[0], D[0]
