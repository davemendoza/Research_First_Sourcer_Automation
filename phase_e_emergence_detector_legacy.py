"""
Phase E Emergence Detector
Flags emerging voices based on first-time appearance or role escalation.
"""

from collections import defaultdict

def detect_emergence(records: list, historical_index: dict):
    emergence = []
    seen = defaultdict(set)

    for r in historical_index:
        seen[r["name"]].add(r["role"])

    for r in records:
        prior_roles = seen.get(r["name"], set())
        if not prior_roles:
            emergence.append({**r, "signal": "NEW_VOICE"})
        elif r["role"] == "speaker" and "speaker" not in prior_roles:
            emergence.append({**r, "signal": "ROLE_ESCALATION"})

    return emergence
