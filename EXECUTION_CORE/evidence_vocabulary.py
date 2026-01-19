#!/usr/bin/env python3
"""
EXECUTION_CORE/evidence_vocabulary.py
============================================================
CANONICAL EVIDENCE VOCABULARY (FROZEN)

This file defines the single canonical mapping between:
- Raw artifact text
- Canonical evidence categories

These labels are consumed by:
- Day 9 (Evidence Summarization)
- Day 8 (Determinant Tiering)

This file must remain stable unless the ontology itself changes.
"""

from typing import Dict, List

CANONICAL_EVIDENCE: Dict[str, List[str]] = {
    "base model training": ["base model", "pretraining", "training from scratch"],
    "architecture research": ["architecture research", "model architecture"],
    "scaling laws": ["scaling laws"],
    "rlhf training": ["rlhf", "reinforcement learning from human feedback"],
    "reward modeling": ["reward modeling"],

    "gpu orchestration": ["gpu orchestration", "multi-gpu"],
    "distributed training": ["distributed training"],
    "cuda": ["cuda"],
    "deepspeed": ["deepspeed"],
    "fsdp": ["fsdp"],
    "nccl": ["nccl"],

    "rag system design": ["rag", "retrieval augmented generation"],
    "vector database integration": ["vector database", "faiss", "pinecone", "weaviate"],
    "production llm deployment": ["production llm deployment"],
    "langchain pipelines": ["langchain"],
    "llamaindex pipelines": ["llamaindex"],

    "end-to-end deployment ownership": ["end-to-end deployment"],
    "integration architecture": ["integration architecture"],

    "authoritative technical content": ["whitepaper", "technical article"],
    "open-source leadership": ["open-source maintainer", "project maintainer"],
    "conference talks": ["conference talk", "speaker"],

    "technical deal ownership": ["technical deal ownership"],
    "ai infrastructure sales": ["ai infrastructure sales"],
}

__all__ = ["CANONICAL_EVIDENCE"]
