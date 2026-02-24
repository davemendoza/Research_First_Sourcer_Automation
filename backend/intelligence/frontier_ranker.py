# ============================================================
# AI TALENT ENGINE — FRONTIER AUTHORITY RANKER
# © 2026 L. David Mendoza. All Rights Reserved.
# ============================================================

from backend.intelligence.frontier_authority_scoring import FrontierAuthorityScorer

class FrontierRanker:

    def __init__(self):
        self.scorer = FrontierAuthorityScorer()

    def rank(self, identities):

        ranked = []

        for identity in identities:

            scores = self.scorer.score_identity(identity)

            identity["frontier_authority_index"] = scores["frontier_authority_index"]
            identity["trajectory_velocity_score"] = scores["trajectory_velocity"]
            identity["ecosystem_influence_score"] = scores["ecosystem_influence"]

            ranked.append(identity)

        ranked.sort(
            key=lambda x: x.get("frontier_authority_index", 0),
            reverse=True
        )

        return ranked
