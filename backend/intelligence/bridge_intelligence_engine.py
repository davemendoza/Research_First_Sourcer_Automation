# ============================================================
# AI Talent Engine — Phase 7 Bridge Intelligence Engine
# Computes betweenness centrality to identify strategic connectors
# Safe additive module
# ============================================================

from __future__ import annotations
import json
from pathlib import Path
from collections import defaultdict

GRAPH_FILE = Path("backend/storage/identity_graph.json")
CACHE_FILE = Path("backend/storage/intelligence/bridge_intelligence.json")

class BridgeIntelligenceEngine:

    def __init__(self):
        self.graph = {}
        self.centrality = {}

        if GRAPH_FILE.exists():
            self.graph = json.loads(GRAPH_FILE.read_text())

    def build_adj(self):

        adj = defaultdict(set)

        for edge in self.graph.get("edges", []):
            a = edge["source"]
            b = edge["target"]

            adj[a].add(b)
            adj[b].add(a)

        return adj

    def compute(self):

        adj = self.build_adj()

        centrality = {node: 0.0 for node in adj}

        nodes = list(adj.keys())

        for s in nodes:

            stack = []
            pred = {w: [] for w in nodes}
            sigma = dict.fromkeys(nodes, 0.0)
            sigma[s] = 1.0
            dist = dict.fromkeys(nodes, -1)
            dist[s] = 0

            queue = [s]

            while queue:

                v = queue.pop(0)
                stack.append(v)

                for w in adj[v]:

                    if dist[w] < 0:

                        queue.append(w)
                        dist[w] = dist[v] + 1

                    if dist[w] == dist[v] + 1:

                        sigma[w] += sigma[v]
                        pred[w].append(v)

            delta = dict.fromkeys(nodes, 0)

            while stack:

                w = stack.pop()

                for v in pred[w]:

                    delta[v] += (
                        sigma[v] / sigma[w]
                    ) * (1 + delta[w])

                if w != s:
                    centrality[w] += delta[w]

        self.centrality = centrality

        CACHE_FILE.write_text(json.dumps(centrality))

        return centrality

    def top_bridges(self, n=25):

        if not self.centrality:
            self.compute()

        ranked = sorted(
            self.centrality.items(),
            key=lambda x: x[1],
            reverse=True
        )

        return ranked[:n]


bridge_engine = BridgeIntelligenceEngine()
