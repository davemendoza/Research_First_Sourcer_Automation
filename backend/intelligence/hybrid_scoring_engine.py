############################################################
# hybrid_scoring_engine.py — Frontier Authority Index Engine
############################################################

import math
from typing import Dict, List

WEIGHTS = {
    "embedding_similarity": 0.25,
    "determinant_authority": 0.20,
    "citation_impact": 0.15,
    "artifact_impact": 0.10,
    "graph_centrality": 0.10,
    "trajectory_velocity": 0.10,
    "evidence_confidence": 0.05,
    "role_alignment": 0.05
}

def normalize_log(value, max_value):
    if value <= 0:
        return 0
    return min(math.log(1+value)/math.log(1+max_value), 1)

def normalize_linear(value, max_value):
    if max_value == 0:
        return 0
    return min(value/max_value,1)

def compute_fai(candidate: Dict):

    scores = {}

    scores["embedding_similarity"] = candidate.get("embedding_similarity",0)

    scores["determinant_authority"] = candidate.get("determinant_score",0)/10

    citations = candidate.get("citation_count",0)
    h = candidate.get("h_index",0)

    scores["citation_impact"] = (
        normalize_log(citations,100000)*0.6 +
        normalize_log(h,200)*0.4
    )

    stars = candidate.get("github_stars",0)
    repos = candidate.get("repo_count",0)

    scores["artifact_impact"] = (
        normalize_log(stars,300000)*0.7 +
        normalize_log(repos,500)*0.3
    )

    scores["graph_centrality"] = candidate.get("graph_centrality",0)

    scores["trajectory_velocity"] = normalize_log(
        candidate.get("citation_velocity",0),5000
    )

    scores["evidence_confidence"] = normalize_linear(
        candidate.get("evidence_sources",0),25
    )

    scores["role_alignment"] = candidate.get("role_alignment_score",0.5)

    fai = 0

    for k,v in scores.items():
        fai += v * WEIGHTS[k]

    fai = fai * 100

    return round(fai,2), scores

def rank_candidates(candidates: List[Dict]):

    results = []

    for c in candidates:

        fai, breakdown = compute_fai(c)

        c["fai_score"] = fai
        c["score_breakdown"] = breakdown

        results.append(c)

    results.sort(key=lambda x: x["fai_score"], reverse=True)

    return results
