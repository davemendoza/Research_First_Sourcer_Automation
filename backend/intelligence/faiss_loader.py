import os
import faiss
import numpy as np

INDEX_PATH = os.path.join(os.path.dirname(__file__), "../../outputs/faiss.index")

class FAISSLoader:

    def __init__(self):
        self.index = None

    def load_or_create(self, dim=768):

        if os.path.exists(INDEX_PATH):
            self.index = faiss.read_index(INDEX_PATH)
        else:
            self.index = faiss.IndexFlatIP(dim)
            faiss.write_index(self.index, INDEX_PATH)

        return self.index

    def search(self, vector, k=20):

        if self.index is None:
            self.load_or_create()

        vector = np.array([vector]).astype("float32")
        scores, ids = self.index.search(vector, k)

        return ids[0].tolist(), scores[0].tolist()

faiss_loader = FAISSLoader()
