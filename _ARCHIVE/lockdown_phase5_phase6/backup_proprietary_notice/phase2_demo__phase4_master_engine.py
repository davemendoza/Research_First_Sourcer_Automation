from contracts.canonical_people_schema import enforce_canonical
# Phase 4 Master Talent Intelligence Engine
# Unified Script with High-End Stretch Scoring

import pandas as pd
from rich.console import Console
from rich.table import Table

console = Console()

INPUT_CSV = "ai_talent_leads.csv"
OUTPUT_CSV = "phase4_ranked_signals.csv"

# ===============================
# ROLE DEFINITIONS (10 families, expanded)
# ===============================
ROLE_BUCKETS = {
    # 1. Foundational AI / Frontier Research
    "foundational": [
        "research scientist", "foundational model", "foundation model",
        "scaling law", "scaling laws", "mixture of experts", "moe",
        "switch transformer", "transformer", "attention is all you need",
        "neurips", "iclr", "icml", "deepmind", "google brain",
        "openai research", "meta ai", "fair", "anthropic research"
    ],
    # 2. Applied LLM / GenAI Engineer
    "applied_llm": [
        "llm", "large language model", "gpt-4", "gpt-3", "gpt3", "gpt4",
        "llama", "llama 2", "llama2", "llama 3", "mistral", "mixtral",
        "dbrx", "claude", "gemini", "qwen", "phi",
        "finetune", "fine-tune", "fine tuning", "instruction tuning",
        "inference", "token streaming", "serving", "llmops", "prompt engineering",
        "embedding model", "embeddings", "chatbot", "assistant model"
    ],
    # 3. RLHF / Alignment
    "rlhf": [
        "rlhf", "reinforcement learning from human feedback",
        "reward model", "reward modeling", "preference model",
        "preference learning", "ppo", "dpo",
        "alignment", "safety tuning", "constitutional ai"
    ],
    # 4. RAG / Retrieval
    "rag": [
        "rag", "retrieval augmented generation", "retrieval-augmented generation",
        "retrieval pipeline", "retrieval system", "retrieval workflow",
        "knowledge retrieval", "knowledge base", "kb retrieval",
        "semantic search", "semantic retrieval", "hybrid retrieval",
        "langchain", "llamaindex", "llama index"
    ],
    # 5. Vector DB / Retrieval Infra
    "vector": [
        "pinecone", "weaviate", "qdrant", "milvus", "faiss",
        "lancedb", "vespa", "pgvector", "redis vector", "elastic vector",
        "opensearch vector", "vector db", "vector database"
    ],
    # 6. AI / ML Infrastructure & Distributed Systems
    "infra": [
        "cuda", "nvidia", "tensorrt", "tensorrt-llm", "triton",
        "deepspeed", "fsdp", "zero-1", "zero-2", "zero-3", "zero3",
        "distributed training", "data parallel", "tensor parallel",
        "pipeline parallel", "multi-node", "multi node",
        "gpu cluster", "gpu orchestration", "gpu scheduling",
        "kubernetes", "k8s", "ray serve", "ray", "slurm",
        "inference serving", "latency", "throughput"
    ],
    # 7. Machine Learning Engineer (general ML)
    "ml": [
        "machine learning engineer", "ml engineer", "ml system",
        "classification", "regression", "supervised learning",
        "unsupervised learning", "time series", "recommendation system",
        "recommender", "sklearn", "xgboost", "random forest"
    ],
    # 8. Forward Deployed / Solutions Engineer
    "fde": [
        "forward deployed", "fde", "solutions engineer",
        "customer engineer", "implementation engineer"
    ],
    # 9. Developer Evangelist / DevRel
    "devrel": [
        "developer advocate", "devrel", "developer evangelist",
        "community engineer", "community building", "technical content",
        "tutorials", "documentation", "workshops", "talks", "conference speaker"
    ],
    # 10. Product-Focused AI / Applied ML
    "product_ai": [
        "product", "product manager", "applied ml", "applied ai",
        "ai features", "ai product", "user-facing ai", "ux for ai"
    ],
    # Fallback
    "general": []
}

ROLE_WEIGHTS = {
    "foundational": 180,
    "applied_llm": 130,
    "rlhf": 140,
    "rag": 90,
    "vector": 70,
    "infra": 150,
    "ml": 70,
    "fde": 40,
    "devrel": 40,
    "product_ai": 55,
    "general": 10,
}

ROLE_LABELS = {
    "foundational": "Foundational AI / Frontier Research Scientist",
    "applied_llm": "Applied LLM / GenAI Engineer",
    "rlhf": "RLHF / Alignment Engineer",
    "rag": "RAG / Retrieval Engineer",
    "vector": "Vector DB / Retrieval Infra Engineer",
    "infra": "AI / ML Infrastructure & Distributed Systems",
    "ml": "Machine Learning Engineer",
    "fde": "Forward Deployed / Solutions Engineer",
    "devrel": "Developer Evangelist / DevRel",
    "product_ai": "Product-Focused AI / Applied ML",
    "general": "General Tech / Contributor",
}

# ===============================
# LOAD DATA
# ===============================
def load_data(path=INPUT_CSV):
    try:
        df = pd.read_csv(path)
        return df
    except Exception as e:
        console.print(f"[red]Error loading CSV: {e}[/red]")
        return pd.DataFrame()

# ===============================
# DETECT PRIMARY & SECONDARY ROLES
# ===============================
def detect_roles(text):
    t = str(text).lower()
    scores = {}

    for role, keywords in ROLE_BUCKETS.items():
        if not keywords:
            scores[role] = 0
        else:
            scores[role] = sum(1 for kw in keywords if kw in t)

    # sort by match count
    sorted_roles = sorted(scores.items(), key=lambda x: x[1], reverse=True)

    primary_key = sorted_roles[0][0]
    # if only one role had nonzero and others zero, second may be general
    secondary_key = sorted_roles[1][0] if len(sorted_roles) > 1 else "general"

    primary = ROLE_LABELS.get(primary_key, "General Tech / Contributor")
    secondary = ROLE_LABELS.get(secondary_key, "General Tech / Contributor")

    return primary, secondary, scores

# ===============================
# HIGH-END STRETCH SCORING
# ===============================
def compute_score(stars, role_score_dict):
    total = 0.0

    # add weighted role signals
    for role_key, count in role_score_dict.items():
        if count > 0:
            total += ROLE_WEIGHTS.get(role_key, 0)

    # stretch stars effect
    try:
        s = float(stars) if stars is not None else 0.0
    except ValueError:
        s = 0.0

    total += s * 0.9
    return total

# ===============================
# TIER ASSIGNMENT (High-End Stretch)
# ===============================
def assign_tier(score):
    if score >= 450:
        return "🧠 Foundational AI"
    elif score >= 250:
        return "⚡ Advanced AI"
    elif score >= 130:
        return "🔧 Applied AI"
    elif score >= 50:
        return "💡 Emerging ML"
    else:
        return "👤 General Contributor"

# ===============================
# MAIN PROCESSOR
# ===============================
def process(df: pd.DataFrame) -> pd.DataFrame:
    if "description" not in df.columns:
        raise ValueError("Input CSV must have a 'description' column")
    if "name" not in df.columns:
        df["name"] = ""

    if "stars" not in df.columns:
        df["stars"] = 0

    primary_roles = []
    secondary_roles = []
    scores = []

    for _, row in df.iterrows():
        desc = row.get("description", "")
        primary, secondary, role_score_dict = detect_roles(desc)
        score = compute_score(row.get("stars", 0), role_score_dict)

        primary_roles.append(primary)
        secondary_roles.append(secondary)
        scores.append(score)

    df["primary_role"] = primary_roles
    df["secondary_role"] = secondary_roles
    df["signal_strength"] = scores
    df["tier"] = df["signal_strength"].apply(assign_tier)

    df = df.sort_values("signal_strength", ascending=False).reset_index(drop=True)
    df["rank"] = df.index + 1
    return df

# ===============================
# DISPLAY TOP ROWS
# ===============================
def display(df: pd.DataFrame, top_n: int = 10):
    table = Table(title="Phase 4: AI Talent Intelligence Output", show_lines=True)
    for col in ["rank", "name", "primary_role", "secondary_role", "tier", "signal_strength"]:
        table.add_column(col, style="cyan")

    for _, r in df.head(top_n).iterrows():
        table.add_row(
            str(r["rank"]),
            str(r["name"]),
            str(r["primary_role"]),
            str(r["secondary_role"]),
            str(r["tier"]),
            str(round(r["signal_strength"], 1)),
        )

    console.print(table)

# ===============================
# MAIN
# ===============================
if __name__ == "__main__":
    console.print("[bold blue]Running AI Talent Engine – Phase 4 Master Engine[/bold blue]")
    df = load_data()
    if not df.empty:
        result = process(df)
result = enforce_canonical(result)
        result.to_csv(OUTPUT_CSV, index=False)
        display(result)
        console.print(f"[green]Saved: {OUTPUT_CSV}[/green]")
    else:
        console.print("[red]No data to process.[/red]")
