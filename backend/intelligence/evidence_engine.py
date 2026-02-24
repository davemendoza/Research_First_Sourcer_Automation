"""
Evidence trace extraction
"""

class EvidenceEngine:

    def __init__(self, edges):
        self.edges = edges

    def evidence_for_edge(self, source, target):

        for e in self.edges:

            if (
                (e["source"] == source and e["target"] == target)
                or
                (e["source"] == target and e["target"] == source)
            ):

                return {
                    "type": e.get("type", "unknown"),
                    "evidence_url": e.get("source_url"),
                    "confidence": e.get("weight", 1.0)
                }

        return None
