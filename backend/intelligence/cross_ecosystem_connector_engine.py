###############################################################################
# CROSS ECOSYSTEM CONNECTOR ENGINE
# © 2026 L. David Mendoza. All Rights Reserved.
###############################################################################

import networkx as nx
import json
from pathlib import Path

DATA_PATH = Path(__file__).resolve().parents[1] / "storage" / "identity_graph.json"

class CrossConnectorEngine:

    def find_connectors(self):

        graph = json.loads(DATA_PATH.read_text())

        G = nx.Graph()

        for edge in graph["edges"]:
            G.add_edge(edge["source"], edge["target"])

        bet = nx.betweenness_centrality(G)

        ranked = sorted(bet.items(), key=lambda x: x[1], reverse=True)

        return ranked[:20]
