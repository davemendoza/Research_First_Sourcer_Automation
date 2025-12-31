import pandas as pd
from datetime import datetime

rows = [
    # Frontier / Foundational
    ("Frontier_LLM_Researchers", "github_search", "LLM researcher language model", "T1", "Foundational"),
    ("Pretraining_Scientists", "github_search", "pretraining transformer", "T1", "Foundational"),
    ("AI_Alignment_RLHF", "github_search", "RLHF reward model", "T1", "Foundational"),

    # Applied AI
    ("Applied_GenAI_Engineers", "github_search", "generative ai engineer", "T2", "Applied"),
    ("RAG_Engineers", "github_search", "RAG langchain llamaindex", "T2", "Applied"),
    ("Healthcare_AI", "github_search", "healthcare AI machine learning", "T2", "Applied"),

    # Infra / Performance
    ("GPU_Inference_Engineers", "github_search", "CUDA inference optimization", "T1", "Infra"),
    ("ML_Systems_Engineers", "github_search", "ML systems distributed training", "T1", "Infra"),
    ("Platform_AI", "github_search", "AI platform engineering", "T2", "Infra"),

    # Breadth / volume
    ("AI_Engineers_Broad", "github_search", "AI engineer machine learning", "T3", "Broad"),
    ("ML_Engineers", "github_search", "machine learning engineer", "T3", "Broad"),
]

df = pd.DataFrame(rows, columns=[
    "scenario",
    "seed_type",
    "seed_value",
    "tier",
    "category"
])

out = "scenario_control_matrix.xlsx"
df.to_excel(out, index=False)

print("✅ scenario_control_matrix.xlsx regenerated")
print(f"Rows: {len(df)}")
print(f"Timestamp: {datetime.utcnow().isoformat()}Z")
