# ============================================================
# AI TALENT ENGINE — ECOSYSTEM INTELLIGENCE ENGINE
# Ecosystem Graph Intelligence Layer
# © 2026 L. David Mendoza. All Rights Reserved.
# ============================================================

import json
import os
from typing import Dict, Any, List

from backend.storage.identity_graph_store import IdentityGraphStore
from backend.storage.telemetry_registry import TelemetryRegistry


class EcosystemIntelligenceEngine:
    """
    Production Ecosystem Intelligence Engine

    Provides ecosystem-level analysis of identity graph,
    clustering, influence, and ecosystem structure.
    """

    def __init__(self):

        self.identity_store = IdentityGraphStore()
        self.telemetry = TelemetryRegistry()

        self.graph_path = os.path.join(
            os.path.dirname(__file__),
            "..",
            "storage",
            "identity_graph.json"
        )

        self.graph_path = os.path.abspath(self.graph_path)


    def load_graph(self) -> Dict[str, Any]:

        if not os.path.exists(self.graph_path):

            return {
                "nodes": [],
                "edges": []
            }

        with open(self.graph_path, "r") as f:
            graph = json.load(f)

        return graph


    def analyze_ecosystem(self) -> Dict[str, Any]:

        graph = self.load_graph()

        nodes = graph.get("nodes", [])
        edges = graph.get("edges", [])

        company_counts = {}

        for node in nodes:

            company = node.get("company", "Independent")

            if company not in company_counts:
                company_counts[company] = 0

            company_counts[company] += 1


        ecosystem = {
            "total_nodes": len(nodes),
            "total_edges": len(edges),
            "company_distribution": company_counts
        }

        self.telemetry.record_event(
            "ecosystem_analysis",
            ecosystem
        )

        return ecosystem


    def get_cluster_summary(self) -> Dict[str, Any]:

        ecosystem = self.analyze_ecosystem()

        return {
            "clusters": ecosystem.get("company_distribution", {}),
            "node_count": ecosystem.get("total_nodes", 0),
            "edge_count": ecosystem.get("total_edges", 0)
        }
