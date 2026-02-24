from .faiss_vector_engine import FAISSVectorEngine
from .hybrid_scoring_engine import rank_candidates

class ExecutiveQueryEngine:

    def __init__(self):

        self.vector_engine = FAISSVectorEngine()

    def execute(self, embedding):

        candidates = self.vector_engine.search(embedding)

        ranked = rank_candidates(candidates)

        return ranked
