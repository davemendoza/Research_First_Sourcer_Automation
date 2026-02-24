# ============================================================
# SIGNAL INTELLIGENCE PLATFORM — LAB CLUSTER MAPPER
# File: lab_cluster_mapper.py
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

class LabClusterMapper:

    def __init__(self, input_path="outputs/enriched_candidates.json"):
        self.input_path = input_path

    def load_candidates(self):
        with open(self.input_path, "r") as f:
            return json.load(f)

    def map_clusters(self):
        candidates = self.load_candidates()
        clusters = defaultdict(list)

        for c in candidates:
            org = c.get("Organization", "Unknown")
            clusters[org].append(c["Identity_Key"])

        return clusters

mapper = LabClusterMapper()
