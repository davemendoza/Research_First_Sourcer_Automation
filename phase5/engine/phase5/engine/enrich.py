import pandas as pd
from .utils import safe_text, count_matches

LLM_TERMS = [
    "llm", "large language model", "gpt-4", "gpt4", "gpt-3", "gpt3",
    "llama", "llama 2", "llama2", "llama 3", "mistral", "mixtral", "dbrx",
    "claude", "gemini", "qwen", "phi"
]

RLHF_TERMS = [
    "rlhf", "reinforcement learning from human feedback", "reward model",
    "reward modeling", "preference model", "ppo", "dpo",
    "alignment", "safety tuning", "constitutional ai"
]

RAG_TERMS = [
    "rag", "retrieval augmented generation", "retrieval-augmented generation",
    "retrieval system", "retrieval workflow", "retrieval pipeline",
    "knowledge base", "kb retrieval", "semantic search", "semantic retrieval",
    "langchain", "llamaindex", "llama index"
]

VECTOR_TERMS = [
    "pinecone", "weaviate", "qdrant", "milvus", "faiss",
    "lancedb", "vespa", "pgvector", "redis vector", "elastic vector",
    "opensearch vector", "vector db", "vector database"
]

INFRA_TERMS = [
    "cuda", "nvidia", "tensorrt", "tensorrt-llm", "triton",
    "deepspeed", "fsdp", "zero-1", "zero2", "zero-3",
    "distributed training", "kubernetes", "k8s", "ray serve", "ray",
    "gpu cluster", "gpu orchestration", "slurm", "inference serving"
]

ML_TERMS = [
    "machine learning", "ml engineer", "sklearn", "xgboost",
    "regression", "classification", "supervised learning",
    "unsupervised learning", "recommendation system"
]

RESEARCH_TERMS = [
    "research scientist", "researcher", "published", "paper",
    "arxiv", "neurips", "iclr", "icml", "acl", "emnlp", "cvpr"
]


def compute_signal_buckets(desc: str) -> dict:
    return {
        "llm": count_matches(desc, LLM_TERMS),
        "rlhf": count_matches(desc, RLHF_TERMS),
        "rag": count_matches(desc, RAG_TERMS),
        "vector": count_matches(desc, VECTOR_TERMS),
        "infra": count_matches(desc, INFRA_TERMS),
        "ml": count_matches(desc, ML_TERMS),
        "research": count_matches(desc, RESEARCH_TERMS),
    }


def build_strengths(row: pd.Series, sig: dict) -> str:
    strengths = []
    role = safe_text(row.get("primary_role", ""))

    if sig["llm"] > 0:
        strengths.append("Clear evidence of LLM experience across model, inference, or prompt design.")
    if sig["rlhf"] > 0:
        strengths.append("Hands-on work with RLHF or alignment methods such as reward models, PPO, or DPO.")
    if sig["rag"] > 0 or sig["vector"] > 0:
        strengths.append("Experience with RAG or retrieval systems backed by vector databases.")
    if sig["infra"] > 0:
        strengths.append("Exposure to GPU and infrastructure stack for training or serving models at scale.")
    if sig["research"] > 0:
        strengths.append("Research-oriented background with publications or foundational model work.")
    if sig["ml"] > 0 and not strengths:
        strengths.append("Solid general machine learning foundations.")

    if not strengths:
        strengths.append("Profile suggests technical potential but with limited explicit AI stack details.")

    if "Foundational AI" in role:
        strengths.append("Suitable for high-end research or frontier model teams.")
    elif "Infrastructure" in role:
        strengths.append("Aligned to infra or distributed systems roles where reliability and scale matter.")
    elif "Applied LLM" in role or "GenAI" in role:
        strengths.append("Good fit for applied LLM engineer roles shipping user-facing AI features.")
    elif "RAG / Retrieval" in role:
        strengths.append("Well suited to knowledge systems or RAG-centric projects.")

    return " ".join(strengths)


def build_weaknesses(row: pd.Series, sig: dict) -> str:
    weaknesses = []
    role = safe_text(row.get("primary_role", ""))

    if sig["llm"] == 0:
        weaknesses.append("Limited explicit evidence of LLM architecture or fine-tuning work.")
    if sig["rlhf"] == 0:
        weaknesses.append("No clear signals of RLHF or preference-learning experiments.")
    if sig["rag"] == 0 and sig["vector"] == 0:
        weaknesses.append("No strong indicators of RAG pipelines or vector search implementation.")
    if sig["infra"] == 0:
        weaknesses.append("Infrastructure and GPU stack depth is not clearly demonstrated.")
    if sig["research"] == 0 and "Foundational AI" in role:
        weaknesses.append("Foundational AI positioning would be stronger with explicit publications or venues.")
    if sum(sig.values()) == 0:
        weaknesses.append("Profile relies more on high-level claims than concrete stack details.")

    if len(weaknesses) > 4:
        weaknesses = weaknesses[:4]

    return " ".join(weaknesses)


def assign_recommendation(row: pd.Series, sig: dict):
    score = float(row.get("signal_strength", 0))
    tier = safe_text(row.get("tier", ""))

    if "Foundational AI" in tier and score >= 800:
        return "Strong Submit", 95
    if ("Foundational AI" in tier or "Advanced AI" in tier) and score >= 500:
        return "Submit", 88
    if score >= 250:
        return "Consider", 75
    if score >= 120:
        return "Borderline", 65
    return "Do Not Submit", 55


def enrich_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    strengths_list = []
    weaknesses_list = []
    rec_labels = []
    rec_conf = []
    llm_s, rlhf_s, rag_s, vec_s, infra_s, ml_s, res_s = [], [], [], [], [], [], []

    for _, row in df.iterrows():
        desc = row.get("description", "")
        sig = compute_signal_buckets(desc)

        llm_s.append(sig["llm"])
        rlhf_s.append(sig["rlhf"])
        rag_s.append(sig["rag"])
        vec_s.append(sig["vector"])
        infra_s.append(sig["infra"])
        ml_s.append(sig["ml"])
        res_s.append(sig["research"])

        strengths = build_strengths(row, sig)
        weaknesses = build_weaknesses(row, sig)
        rec_label, rec_conf_p = assign_recommendation(row, sig)

        strengths_list.append(strengths)
        weaknesses_list.append(weaknesses)
        rec_labels.append(rec_label)
        rec_conf.append(rec_conf_p)

    df["LLM_Signals"] = llm_s
    df["RLHF_Signals"] = rlhf_s
    df["RAG_Signals"] = rag_s
    df["VectorDB_Signals"] = vec_s
    df["Infra_Signals"] = infra_s
    df["ML_Signals"] = ml_s
    df["Research_Signals"] = res_s

    df["Strengths"] = strengths_list
    df["Weaknesses"] = weaknesses_list
    df["Recommendation"] = rec_labels
    df["Recommendation_Confidence"] = rec_conf

    return df
