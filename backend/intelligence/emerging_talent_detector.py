# ============================================================
# SIGNAL INTELLIGENCE PLATFORM — EMERGING TALENT DETECTOR
# File: emerging_talent_detector.py
# Author: Dave Mendoza
# System: AI Talent Engine — Signal Intelligence Platform
# Layer: Frontier Intelligence Layer
# Purpose: Advanced frontier intelligence capability module
# Identity Key: Canonical identity authority
# Deterministic-safe
# © 2026 L. David Mendoza. All Rights Reserved.
# ============================================================


import json

class EmergingTalentDetector:

    def __init__(self, input_path="outputs/enriched_candidates.json"):
        self.input_path = input_path

    def load_candidates(self):
        with open(self.input_path, "r") as f:
            return json.load(f)

    def detect(self):
        candidates = self.load_candidates()
        emerging = []

        for c in candidates:
            citations = c.get("Total_Citations", 0)
            velocity = c.get("Citation_Velocity", citations * 0.3)

            if velocity > citations * 0.25:
                emerging.append(c["Identity_Key"])

        return emerging

detector = EmergingTalentDetector()
