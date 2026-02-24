# ============================================================
# SIGNAL INTELLIGENCE PLATFORM — RESEARCH IMPACT FORECASTER
# File: research_impact_forecaster.py
# Author: Dave Mendoza
# System: AI Talent Engine — Signal Intelligence Platform
# Layer: Frontier Intelligence Layer
# Purpose: Advanced frontier intelligence capability module
# Identity Key: Canonical identity authority
# Deterministic-safe
# © 2026 L. David Mendoza. All Rights Reserved.
# ============================================================


import json
import math

class ResearchImpactForecaster:

    def __init__(self, input_path="outputs/enriched_candidates.json"):
        self.input_path = input_path

    def load_candidates(self):
        with open(self.input_path, "r") as f:
            return json.load(f)

    def forecast(self):
        candidates = self.load_candidates()
        forecasts = {}

        for c in candidates:
            identity = c["Identity_Key"]
            citations = c.get("Total_Citations", 0)
            recent = c.get("Recent_Citations", citations * 0.2)

            momentum = recent / max(citations, 1)
            projected = citations * (1 + momentum)

            forecasts[identity] = {
                "Momentum": momentum,
                "Projected_Citations": projected
            }

        return forecasts

forecaster = ResearchImpactForecaster()
