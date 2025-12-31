#!/usr/bin/env python3
"""
Scenario Matrix Builder (Ultra Expansion)
- Takes your scenario_control_matrix.xlsx (11 rows)
- Expands to 100+ high-recall variants
- Outputs: data/scenarios/scenario_control_matrix_EXPANDED.xlsx
© 2025 L. David Mendoza
"""
import pandas as pd
from pathlib import Path
import yaml

EXPAND_MAP = {
    # Foundational / frontier expansions
    "LLM researcher language model": [
        "large language model researcher",
        "language model research engineer",
        "foundation model researcher",
        "transformer researcher",
        "pretraining language model",
        "LLM training",
        "scaling laws transformer",
        "mixture of experts transformer",
        "instruction tuning",
        "tokenizer language model",
    ],
    "pretraining transformer": [
        "transformer pretraining",
        "masked language model",
        "causal language model training",
        "distributed pretraining",
        "data pipeline pretraining",
        "FSDP pretraining",
        "DeepSpeed pretraining",
        "Megatron pretraining",
    ],
    "RLHF reward model": [
        "reinforcement learning from human feedback",
        "reward modeling",
        "preference optimization",
        "DPO alignment",
        "PPO RLHF",
        "SFT RLHF",
        "alignment engineer",
        "policy optimization LLM",
    ],

    # Applied
    "generative ai engineer": [
        "genai engineer",
        "LLM engineer",
        "LLMOps",
        "prompt + LangChain",
        "agentic workflows",
        "tool calling",
        "structured generation",
    ],
    "RAG langchain llamaindex": [
        "retrieval augmented generation",
        "RAG pipeline",
        "LangChain RAG",
        "LlamaIndex RAG",
        "vector database RAG",
        "FAISS retrieval",
        "embedding pipeline",
        "reranking RAG",
        "hybrid search RAG",
    ],
    "healthcare AI machine learning": [
        "medical imaging deep learning",
        "clinical NLP",
        "biomedical machine learning",
        "health ML engineer",
        "healthcare LLM",
        "radiology deep learning",
    ],

    # Infra / performance
    "CUDA inference optimization": [
        "TensorRT LLM",
        "Triton inference",
        "vLLM inference",
        "GPU kernel optimization",
        "FlashAttention",
        "quantization inference",
        "PagedAttention",
        "ONNX runtime GPU",
    ],
    "ML systems distributed training": [
        "distributed training",
        "DeepSpeed ZeRO",
        "FSDP PyTorch",
        "NCCL collective",
        "parameter server",
        "Ray distributed training",
        "Kubernetes ML platform",
        "MLOps platform",
    ],
    "AI platform engineering": [
        "ML platform",
        "LLM platform",
        "inference platform",
        "model serving platform",
        "feature store platform",
        "observability ML",
    ],

    # Broad control expansions
    "AI engineer machine learning": [
        "machine learning engineer",
        "applied machine learning",
        "deep learning engineer",
        "ML engineer PyTorch",
        "ML engineer TensorFlow",
    ],
    "machine learning engineer": [
        "applied ML engineer",
        "production ML engineer",
        "MLOps engineer",
        "model serving engineer",
    ],
}

def main():
    cfg = yaml.safe_load(open("volume_expansion.yaml"))
    inp = cfg["scenario_matrix_input"]
    out = cfg["scenario_matrix_output"]

    base = pd.read_excel(inp)

    required = {"scenario", "seed_type", "seed_value", "tier", "category"}
    missing = required - set(base.columns)
    if missing:
        raise SystemExit(f"❌ Scenario matrix missing columns: {missing}")

    rows = []
    for _, r in base.iterrows():
        seed = str(r["seed_value"]).strip()
        rows.append(r.to_dict())

        # Expand if we have a mapping. If not, still add a few generic expansions.
        variants = EXPAND_MAP.get(seed, [])
        if not variants:
            variants = [
                seed,
                f"{seed} engineer",
                f"{seed} research",
                f"{seed} open source",
            ]

        for i, v in enumerate(variants, start=1):
            rr = r.to_dict()
            rr["scenario"] = f"{r['scenario']}_EXP_{i:02d}"
            rr["seed_type"] = "github_search"
            rr["seed_value"] = v
            rows.append(rr)

    expanded = pd.DataFrame(rows).drop_duplicates(subset=["seed_value", "tier", "category"]).reset_index(drop=True)

    Path(out).parent.mkdir(parents=True, exist_ok=True)
    expanded.to_excel(out, index=False)

    # Also overwrite the root scenario_control_matrix.xlsx so the rest of your tooling stays aligned
    expanded.to_excel("scenario_control_matrix.xlsx", index=False)

    print("✅ Scenario expansion complete")
    print(f"Base rows: {len(base)}")
    print(f"Expanded rows: {len(expanded)}")
    print(f"Wrote: {out}")
    print("Synced: scenario_control_matrix.xlsx (root)")
if __name__ == "__main__":
    main()
