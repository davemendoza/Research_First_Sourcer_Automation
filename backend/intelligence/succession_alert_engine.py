class SuccessionAlertEngine:

    def evaluate(self, candidate):

        score = candidate.get("FAI_score", 0)

        if score > 0.85:
            return {
                "alert": True,
                "priority": "HIGH"
            }

        return {
            "alert": False,
            "priority": "NONE"
        }
