###############################################################################
# COMMUNITY DETECTION ENGINE
# © 2026 L. David Mendoza. All Rights Reserved.
###############################################################################

import networkx as nx
import json
from pathlib import Path
import community as community_louvain

DATA_PATH = Path(__file__).resolve().parents[1] / "storage" / "identity_graph.json"

class CommunityDetectionEngine:

    def detect(self):

        G = nx.Graph()
        graph = json.loads(DATA_PATH.read_text())

        for edge in graph["edges"]:
            G.add_edge(edge["source"], edge["target"])

        partition = community_louvain.best_partition(G)

        return partition
