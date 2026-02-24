###############################################################################
# INFLUENCE METRICS ENGINE
# © 2026 L. David Mendoza. All Rights Reserved.
###############################################################################

import networkx as nx
import json
from pathlib import Path

DATA_PATH = Path(__file__).resolve().parents[1] / "storage" / "identity_graph.json"

class InfluenceMetricsEngine:

    def __init__(self):
        self.G = nx.Graph()
        if DATA_PATH.exists():
            graph = json.loads(DATA_PATH.read_text())
            for node in graph["nodes"]:
                self.G.add_node(node["id"], **node)
            for edge in graph["edges"]:
                self.G.add_edge(edge["source"], edge["target"], **edge)

    def compute_metrics(self):

        pagerank = nx.pagerank(self.G)
        eigen = nx.eigenvector_centrality(self.G, max_iter=1000)
        betweenness = nx.betweenness_centrality(self.G)
        degree = dict(self.G.degree())

        metrics = {}

        for node in self.G.nodes():
            metrics[node] = {
                "pagerank": pagerank.get(node, 0),
                "eigenvector": eigen.get(node, 0),
                "betweenness": betweenness.get(node, 0),
                "degree": degree.get(node, 0)
            }

        return metrics
