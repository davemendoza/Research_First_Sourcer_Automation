# ============================================================
# AI TALENT ENGINE — SIGNAL INTELLIGENCE PLATFORM
# File: ecosystem_gravity_engine.py
# Author: Dave Mendoza
# Layer: Intelligence Layer
# Purpose: Compute ecosystem dominance and gravity scores
# Copyright: © 2026 L. David Mendoza. All Rights Reserved.
# ============================================================

import json
from pathlib import Path
from collections import defaultdict

GRAPH = Path("backend/storage/identity_graph.json")

class EcosystemGravityEngine:

    def compute(self):

        if not GRAPH.exists():
            return {}

        graph = json.loads(GRAPH.read_text())

        gravity = defaultdict(int)

        for node in graph.get("nodes", []):
            gravity[node.get("cluster", "unknown")] += 1

        return dict(gravity)

gravity_engine = EcosystemGravityEngine()
