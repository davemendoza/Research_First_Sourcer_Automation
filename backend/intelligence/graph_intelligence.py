"""
AI Talent Engine – Graph Intelligence Engine
© 2026 L. David Mendoza. All Rights Reserved.

Computes:
- Degree centrality
- Betweenness centrality
- Bridge detection
- Executive narrative
"""

import math
from collections import defaultdict, deque

class GraphIntelligenceEngine:

    def __init__(self, nodes, edges):
        self.nodes = {n["id"]: n for n in nodes}
        self.edges = edges
        self.adj = defaultdict(set)

        for e in edges:
            self.adj[e["source"]].add(e["target"])
            self.adj[e["target"]].add(e["source"])

    # Degree centrality
    def degree_centrality(self):
        return {
            node: len(neighbors)
            for node, neighbors in self.adj.items()
        }

    # Betweenness centrality (simplified)
    def betweenness_centrality(self):

        bc = defaultdict(float)

        for s in self.nodes:

            stack = []
            pred = defaultdict(list)
            sigma = defaultdict(int)
            dist = defaultdict(lambda: -1)

            sigma[s] = 1
            dist[s] = 0

            queue = deque([s])

            while queue:
                v = queue.popleft()
                stack.append(v)

                for w in self.adj[v]:

                    if dist[w] < 0:
                        queue.append(w)
                        dist[w] = dist[v] + 1

                    if dist[w] == dist[v] + 1:
                        sigma[w] += sigma[v]
                        pred[w].append(v)

            delta = defaultdict(float)

            while stack:
                w = stack.pop()
                for v in pred[w]:
                    delta[v] += (
                        sigma[v] / sigma[w]
                    ) * (1 + delta[w])

                if w != s:
                    bc[w] += delta[w]

        return bc

    def top_bridges(self, count=5):
        bc = self.betweenness_centrality()

        return sorted(
            bc.items(),
            key=lambda x: x[1],
            reverse=True
        )[:count]

    def generate_narrative(self):

        degree = self.degree_centrality()
        bridges = self.top_bridges()

        top_node = max(degree, key=degree.get)

        cluster_counts = defaultdict(int)

        for node in self.nodes.values():
            cluster_counts[node.get("cluster", "Unknown")] += 1

        dominant_cluster = max(cluster_counts, key=cluster_counts.get)

        bridge_name = self.nodes[bridges[0][0]]["label"] if bridges else "Unknown"

        return (
            f"Network dominated by {dominant_cluster} cluster. "
            f"Primary influence node is {self.nodes[top_node]['label']}. "
            f"Key bridge identity is {bridge_name}, connecting multiple ecosystems."
        )
