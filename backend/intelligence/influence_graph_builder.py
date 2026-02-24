# ============================================================
# SIGNAL INTELLIGENCE PLATFORM — INFLUENCE GRAPH BUILDER
# File: influence_graph_builder.py
# Author: Dave Mendoza
# System: AI Talent Engine — Signal Intelligence Platform
# Layer: Frontier Intelligence Layer
# Purpose: Advanced frontier intelligence capability module
# Identity Key: Canonical identity authority
# Deterministic-safe
# © 2026 L. David Mendoza. All Rights Reserved.
# ============================================================


import json
from collections import defaultdict

class InfluenceGraphBuilder:

    def __init__(self, input_path="outputs/enriched_candidates.json"):
        self.input_path = input_path
        self.graph = defaultdict(set)

    def load_candidates(self):
        with open(self.input_path, "r") as f:
            return json.load(f)

    def build_graph(self):
        candidates = self.load_candidates()

        for c in candidates:
            identity = c.get("Identity_Key")
            collaborators = c.get("Coauthors", [])

            for collaborator in collaborators:
                self.graph[identity].add(collaborator)

        return self.graph

    def compute_influence_scores(self):
        scores = {}

        for node, edges in self.graph.items():
            scores[node] = len(edges)

        return scores

builder = InfluenceGraphBuilder()
