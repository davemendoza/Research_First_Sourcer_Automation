"""
Executive Intelligence Service Layer
"""

from backend.intelligence.graph_intelligence import GraphIntelligenceEngine
from backend.intelligence.evidence_engine import EvidenceEngine

class ExecutiveIntelligenceService:

    def __init__(self, graph_data):

        self.nodes = graph_data["nodes"]
        self.edges = graph_data["edges"]

        self.graph_engine = GraphIntelligenceEngine(
            self.nodes,
            self.edges
        )

        self.evidence_engine = EvidenceEngine(self.edges)

    def executive_summary(self):

        return {
            "narrative": self.graph_engine.generate_narrative(),
            "top_bridges": self.graph_engine.top_bridges(),
            "degree": self.graph_engine.degree_centrality()
        }

    def edge_evidence(self, source, target):

        return self.evidence_engine.evidence_for_edge(
            source,
            target
        )
