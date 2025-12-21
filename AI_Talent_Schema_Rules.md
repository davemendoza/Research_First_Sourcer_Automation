---
file_type: schema_specification
project: Research-First Sourcer Automation
version: 3.3
phase: global
description: Canonical AI Talent Engine schema reference aligned to the 37-agent system (Phases 6–8).
updated: 2025-12-21
author: L. David Mendoza (Creator)
license: © 2025 L. David Mendoza – All Rights Reserved
---

> **Created by L. David Mendoza © 2025**  
> AI Talent Engine — Canonical Schema Specification (37 Agents · 37 Fields)

# 🧬 AI Talent Schema Rules v3.3

Defines the unified field hierarchy and enumerations for all outputs within the AI Talent Engine (v3.3).  
This release expands schema coverage from 32 → 37 fields to incorporate the Phase 8 Predictive & Governance layer.

---

## 1 · Schema Overview
Every dataset produced by the AI Talent Engine must conform to this canonical schema.  
It governs: field order, normalization logic, allowed enumerations, cross-phase compatibility, and provenance consistency.

---

## 2 · Canonical Agent Distribution (1–37)

| Phase | Agent Range | Role | Description |
|-------|--------------|------|--------------|
| 6 | 1–26 | Intelligence Extraction | Portfolio and research signal collection |
| 7 | 27–32 | Citation & Influence Analytics | Velocity and network analysis |
| 8 | 33–37 | Predictive & Governance Analytics | Career forecasting and integrity checks |

---

## 3 · Canonical Field Order (37 Columns)

| # | Field Name | Description |
|---|-------------|-------------|
| 1 | AI_Classification | Primary domain category: Frontier / RLHF / Applied / Infra / Multimodal / Safety / Evaluation |
| 2 | Full_Name | Researcher or Engineer full name |
| 3 | Company | Institution or corporate affiliation |
| 4 | Team_or_Lab | Division or group (e.g., FAIR, DeepMind Safety) |
| 5 | Title | Professional title as written |
| 6 | Seniority_Level | Principal / Staff / Senior / Director / VP |
| 7 | Corporate_Email | Public lab or company email |
| 8 | Personal_Email | Publicly listed email |
| 9 | LinkedIn_URL | LinkedIn profile |
| 10 | Portfolio_URL | Personal website / GitHub.io |
| 11 | Google_Scholar_URL | Scholar reference link |
| 12 | Semantic_Scholar_URL | Alternate scholarly record |
| 13 | GitHub_URL | Code repository reference |
| 14 | Primary_Specialties | Core technical skills (LLMs, CUDA, alignment etc.) |
| 15 | LLM_Names | Model names (GPT-4, Claude, LLaMA, etc.) |
| 16 | VectorDB_Tech | Vector DB used (Weaviate, FAISS, Pinecone, etc.) |
| 17 | RAG_Details | RAG framework details |
| 18 | Inference_Stack | Inference runtimes (vLLM, TensorRT-LLM, ONNX, etc.) |
| 19 | GPU_Infra_Signals | CUDA / Triton / DeepSpeed usage |
| 20 | RLHF_Eval_Signals | Reward-model and PPO/DPO indicators |
| 21 | Multimodal_Signals | Vision-language or robotics fusion signals |
| 22 | Research_Areas | Primary academic focus |
| 23 | Top_Papers_or_Blogposts | Notable works or posts |
| 24 | Conference_Presentations | Talks / tutorials / workshops |
| 25 | Awards_Luminary_Signals | Recognition (Best Paper, Spotlight, etc.) |
| 26 | Panel_Talks_Workshops | Panels moderated or organized |
| 27 | Citation_Trajectory | 24-month citation velocity (High / Medium / Low) |
| 28 | Strengths | Qualitative impact summary |
| 29 | Weaknesses | Known skill or domain gaps |
| 30 | Corporate_Profile_URL | Company / lab research page |
| 31 | Publications_Page_URL | Institutional publication index |
| 32 | Blog_Post_URLs | Authored technical articles |
| 33 | Career_Velocity_Score | Career growth velocity computed by Phase 8 |
| 34 | Influence_Delta_12mo | Projected influence change over 12 months |
| 35 | Emerging_Talent_Flag | Binary indicator for early-career momentum |
| 36 | Governance_Compliance_Score | Compliance and audit integrity rating |
| 37 | Predictive_Hiring_Score | Composite career + influence forecast |

---

## 4 · Normalization Rules

### AI_Classification  
Valid values = [`Frontier`,`RLHF`,`Applied`,`Infra`,`Multimodal`,`Safety`,`Evaluation`]

### Citation Trajectory  
```python
velocity = citations_last_24mo / total_citations

