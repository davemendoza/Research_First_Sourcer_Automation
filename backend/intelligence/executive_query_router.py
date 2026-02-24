from hybrid_scoring_engine import score_candidate
from identity_fusion_engine import fuse_identity
from trajectory_engine import trajectory_score
from faiss_loader import faiss_loader

def execute_query(query_text):

    index = faiss_loader.load_or_create()

    dummy_vector = [0.1] * 768

    ids, similarity = faiss_loader.search(dummy_vector, k=20)

    candidates = []

    for i, sim in zip(ids, similarity):

        candidate = {
            "id": int(i),
            "embedding_similarity": float(sim),
            "citations": 1000 + i,
            "h_index": 10 + i,
            "github_stars": 50 + i,
            "determinant_signals": 0.75,
            "trajectory_score": trajectory_score(i),
            "organization_tier": 1
        }

        fused = fuse_identity(candidate)

        candidate["FAI_score"] = score_candidate(candidate)

        candidates.append(candidate)

    candidates.sort(key=lambda x: x["FAI_score"], reverse=True)

    return candidates
