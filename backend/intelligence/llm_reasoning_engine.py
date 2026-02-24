import json
import math

class LLMReasoningEngine:

    def __init__(self):
        pass

    def explain_score(self, candidate):

        explanation = {
            "identity": candidate.get("identity"),
            "FAI_score": candidate.get("FAI_score"),
            "components": {
                "vector_similarity": candidate.get("vector_score"),
                "authority": candidate.get("authority_score"),
                "trajectory": candidate.get("trajectory_score"),
                "evidence": candidate.get("evidence_score")
            },
            "interpretation": self._interpret(candidate)
        }

        return explanation

    def _interpret(self, candidate):

        score = candidate.get("FAI_score", 0)

        if score > 0.9:
            return "Frontier-tier candidate with exceptional authority and trajectory."

        if score > 0.75:
            return "High-value candidate with strong frontier alignment."

        if score > 0.5:
            return "Promising candidate with moderate frontier signals."

        return "Developing candidate requiring further validation."
