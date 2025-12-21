"""
Phase G Signal Scoring
Produces numeric scores from input-driven signals:
- Base score per signal type (NEW_VOICE, ROLE_ESCALATION, etc.)
- Multiplied by role criticality weight
- Cluster bonus if member of a detected cluster

No speculation: scores are purely derived from observed input events.
"""

from __future__ import annotations
from typing import Dict, List, Any
from phase_g_role_weighting import weight_for_role

BASE_SIGNAL_SCORES = {
    "NEW_VOICE": 2.0,
    "ROLE_ESCALATION": 3.0,
    "ACCELERATION": 2.5,
    "NEW_SIGNAL": 2.5,
    "STAGNATION": 0.5,
    "": 1.0,
}

def score_events(events: List[Dict[str, Any]], role_weights: Dict[str, float], cluster_members: Dict[str, int]) -> Dict[str, Dict[str, Any]]:
    """
    cluster_members: name -> number_of_clusters_involved
    """
    scores: Dict[str, Dict[str, Any]] = {}

    for e in events:
        name = e["name"]
        sig = (e.get("signal") or "").strip()
        base = float(BASE_SIGNAL_SCORES.get(sig, 1.0))
        rw = weight_for_role(e.get("role_type", "Unknown"), role_weights)

        cluster_bonus = 0.0
        if name in cluster_members:
            # Bonus scales gently to avoid runaway scoring
            cluster_bonus = 1.0 + min(2.0, 0.5 * cluster_members[name])

        total = base * rw + cluster_bonus

        if name not in scores:
            scores[name] = {
                "name": name,
                "role_type": e.get("role_type", "Unknown"),
                "events": [],
                "base_sum": 0.0,
                "cluster_bonus": 0.0,
                "role_weight": rw,
                "escalation_score": 0.0,
            }

        scores[name]["events"].append({
            "signal": sig,
            "base": base,
            "role_weight": rw,
            "source": e.get("source", ""),
            "affiliation": e.get("affiliation", ""),
            "year": e.get("year"),
            "cluster_bonus_applied": cluster_bonus,
            "total_event_score": total,
        })

        scores[name]["base_sum"] += base * rw
        scores[name]["cluster_bonus"] = max(scores[name]["cluster_bonus"], cluster_bonus)
        scores[name]["escalation_score"] = sum(ev["total_event_score"] for ev in scores[name]["events"])

    # Deterministic ordering of per-person events
    for name in scores:
        scores[name]["events"].sort(key=lambda x: ((x.get("year") or 0), x["source"], x["signal"]))

    ordered = {k: scores[k] for k in sorted(scores.keys(), key=lambda s: s.lower())}
    return ordered
