import numpy as np

class VectorSimilarityEngine:

    def similarity(self, query, embeddings):

        sims = embeddings @ query.T

        return sims
