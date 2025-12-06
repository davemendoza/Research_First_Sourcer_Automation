---
file_type: schema_specification
project: Research-First Sourcer Automation
version: 3.0
phase: global
description: Canonical AI Talent Engine schema reference for all phases.
updated: 2025-12-04
---

# 🧬 AI Talent Schema Rules
**Version:** v3.0  
**Author:** Research-First Sourcer Automation Project  
**Purpose:**  
Defines the unified data schema, normalization rules, and field hierarchy for all agent outputs within the AI Talent Engine.  
This schema ensures that every CSV, JSON, or enrichment output remains consistent, standardized, and ingestion-ready across Phases 5–8.

---

## 1. Schema Overview

All outputs (from corporate, academic, RLHF, multimodal, GPU, or citation-based agents) must conform to the **AI Talent Schema**.  
This schema underpins your Phase 6 and Phase 7 pipelines and enables seamless merging of intelligence outputs into analytics dashboards or hiring intelligence layers.

It governs:
- Field naming conventions  
- Column order  
- Normalization logic  
- Accepted enumerations  
- Cross-phase compatibility  

---

## 2. Canonical Column Order

| # | Column Name | Description |
|---|--------------|-------------|
| **1** | **AI_Classification** | Primary research or role category. Valid values: `Frontier`, `RLHF`, `Applied`, `Infra`, `Multimodal`, `Safety`, `Evaluation`. |
| **2** | Full_Name | Full researcher or engineer name. |
| **3** | Company | Current company or institutional affiliation. |
| **4** | Team_or_Lab | Lab, division, or internal group (e.g., Applied AI, FAIR, DeepMind Safety). |
| **5** | Title | Job title as written (Principal Scientist, Distinguished Engineer, etc.). |
| **6** | Seniority_Level | Normalized tier: `Principal`, `Staff`, `Senior`, `Director`, `VP`. |
| **7** | Corporate_Email | Public corporate or lab email (e.g., mailto links). |
| **8** | Personal_Email | Extracted from Scholar, CV, or portfolio when public. |
| **9** | Mobile_Phone | Publicly visible phone numbers (rare; captured via CVs or academic contact pages). |
| **10** | LinkedIn_URL | Profile link, if provided. |
| **11** | Portfolio_URL | Personal site, GitHub.io, or lab homepage. |
| **12** | Google_Scholar_URL | Scholar reference. |
| **13** | Semantic_Scholar_URL | Alternate scholarly record. |
| **14** | GitHub_URL | GitHub or code contribution reference. |
| **15** | Primary_Specialties | Core expertise (LLMs, RLHF, CUDA, alignment, reasoning, etc.). |
| **16** | LLM_Names | Explicitly mentioned model names (GPT-4, Claude, LLaMA, DeepSeek, Gemini, etc.). |
| **17** | VectorDB_Tech | Vector databases (Weaviate, Pinecone, FAISS, Milvus, Chroma, Vespa). |
| **18** | RAG_Details | Frameworks and architecture: LangChain, LlamaIndex, LangGraph, retriever logic. |
| **19** | Inference_Stack | Runtime or inference frameworks: vLLM, TensorRT-LLM, SGLang, ONNX, llama.cpp. |
| **20** | GPU_Infra_Signals | Hardware and system-level tech: CUDA, Triton, NCCL, DeepSpeed, FSDP. |
| **21** | RLHF_Eval_Signals | Reward modeling, DPO/PPO, evaluator networks, alignment pipelines. |
| **22** | Multimodal_Signals | Vision-language, diffusion, speech, robotics, or sensor fusion indicators. |
| **23** | Research_Areas | General domain or academic focus (alignment, interpretability, scaling laws). |
| **24** | Top_Papers_or_Blogposts | Highlighted authored works or technical posts. |
| **25** | Conference_Presentations | Talks, tutorials, or workshops presented. |
| **26** | Awards_Luminary_Signals | Recognition such as Best Paper, Test-of-Time, spotlight, or keynote roles. |
| **27** | Panel_Talks_Workshops | Moderator or organizer evidence from events. |
| **28** | Citation_Trajectory | Computed 24-month citation velocity: `High`, `Medium`, `Low`. |
| **29** | Strengths | Short qualitative summary of technical depth and impact. |
| **30** | Weaknesses | Known skill or domain gaps. |
| **31** | Corporate_Profile_URL | Primary company or research page URL. |
| **32** | Publications_Page_URL | Institutional publication list or research index. |
| **33** | Blog_Post_URLs | Authored or contributor blog links. |
| **34** | Source_Notes | Extraction context or metadata provenance. |
| **35** | Last_Updated | ISO-8601 date timestamp (YYYY-MM-DD). |

---

## 3. Normalization Rules

**AI_Classification**  
Must always belong to one of:  
`["Frontier", "RLHF", "Applied", "Infra", "Multimodal", "Safety", "Evaluation"]`

**Citation_Trajectory Formula**
```python
velocity = (citations_last_24mo / total_citations)
