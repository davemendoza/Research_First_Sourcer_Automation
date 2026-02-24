# ============================================================
# AI TALENT ENGINE — SIGNAL INTELLIGENCE PLATFORM
# File: trajectory_forecast_engine.py
# Author: Dave Mendoza
# Layer: Autonomous Intelligence Layer
# Purpose: Predict future frontier engineers using signal velocity
# Copyright: © 2026 L. David Mendoza. All Rights Reserved.
# ============================================================

import json
from pathlib import Path
from collections import defaultdict

GRAPH = Path("backend/storage/identity_graph.json")

class TrajectoryForecastEngine:

    def __init__(self):
        self.graph = {}
        if GRAPH.exists():
            self.graph = json.loads(GRAPH.read_text())

    def forecast(self, limit=25):

        score = defaultdict(int)

        for edge in self.graph.get("edges", []):
            score[edge["source"]] += 1
            score[edge["target"]] += 1

        ranked = sorted(score.items(), key=lambda x: x[1], reverse=True)

        return ranked[:limit]

trajectory_engine = TrajectoryForecastEngine()
