# ===============================================
#  © 2025 Dave Mendoza, DBA AI Craft, Inc. All rights reserved.
#  Proprietary and Confidential — Unauthorized copying or distribution is prohibited.
# ===============================================

# 🧠 AI Talent Engine – Phase 6 Master Specification
**Version 6.1 · December 2025**  
**Validated by:** AI_Talent_Schema_Rules v3.0  

---

## 1 · Purpose
The AI Talent Engine is a 26-agent research-grade sourcing and enrichment system aligned with the **Research-First Sourcer Automation** project.  

Phase 6 unifies **academic**, **corporate**, and **open-source portfolio intelligence** to identify, classify, and enrich AI/ML researchers and engineers across **Frontier**, **RLHF**, **Infra**, and **Multimodal** domains.  

It acts as the **active enrichment layer** connecting upstream raw data ingestion (Phases 0–5) to downstream analytics (Phases 7–8).

---

## 2 · Core Schema
**Column 1:** `AI_Classification`  
Followed by:  
`Full_Name · Company · Team_or_Lab · Title · Seniority · Contact · Tech Signals · Research Evidence · Qualitative · Provenance`.  

All Phase 6 outputs are validated using **AI_Talent_Schema_Rules v3.0**, which defines canonical column order, normalization logic, and enumerations for all AI Talent Engine phases (5–8).  

This schema ensures data interoperability across:
- Research enrichment (Phase 6)  
- Citation analytics (Phase 7)  
- Visualization (Phase 8)

---

## 3 · Phase 6 Agents

| # | Agent Name | Description |
|---|-------------|-------------|
| **17** | Public Portfolio & Contact Intelligence | Aggregates public portfolio, GitHub, and contact metadata. |
| **18** | Academic Lab Intelligence | Extracts lab affiliations, publications, and co-author data. |
| **19** | Global Conference Intelligence | Identifies participation in Frontier, Infra, and RLHF conferences. |
| **20** | Citation Network Mapping | Pre-computes citation links for Phase 7 analytics. |
| **21** | Competitive Movement Tracking | Maps inter-company and cross-lab researcher mobility. |
| **22** | RLHF & Post-Training Intelligence | Detects reward model, preference optimization, and alignment work. |
| **23** | MLSys / Distributed Systems & GPU Infra | Captures systems, CUDA, and distributed infrastructure signals. |
| **24** | Multimodal & Reasoning Models | Identifies vision-language, diffusion, and reasoning model efforts. |
| **25** | AI Luminary & Awards Intelligence | Collects recognition data: Best Paper, Spotlight, or Test-of-Time. |
| **26** | Corporate AI Research X-Ray | Analyzes internal AI research groups and publication pipelines. |

Each agent outputs structured CSV data following `AI_Talent_Schema_Rules v3.0`.

---

## 4 · Integration Pipeline
| Phase | Role | Description |
|-------|------|-------------|
| **0–5** | Data Collection | Ingest raw entity data from Scholar, GitHub, and corporate datasets. |
| **6** | Research Agent Activation | Apply 17–26 agents to enrich and classify profiles. |
| **7** | Citation Intelligence | Compute velocity, collaboration networks, and influence tiers. |
| **8** | Visualization & Reporting | Aggregate dashboards and export analytics datasets. |

**Output directory:** `/output/intelligence/*.csv`

---

## 5 · Key Behavior
- Prioritize **RLHF**, **citation velocity**, and **GPU infra** signals.  
- Merge **GitHub + Scholar + Portfolio** data for identity verification.  
- Capture **only public contact information** (no private data).  
- Auto-assign `AI_Classification` based on technical stack context.  
- Preserve **source URLs** for audit and provenance tracking.  
- Enforce schema compliance through AI_Talent_Schema_Rules v3.0 normalization.

---

## 6 · Cross-Phase References
- [`AI_Talent_Engine_Phase7_Citation_Intelligence.md`] — Citation velocity and influence graph layer.  
- [`AI_Talent_Schema_Rules.md`] — Canonical schema validation and normalization standard.  
- [`README_SYSTEM_SPEC.md`] — System-wide phase index and version history.

---

## 7 · Version Control
| Version | Date | Summary | Author |
|----------|------|----------|---------|
| **6.0** | 2025-12 | Initial release (Parasail validation reference). | Dave / Core Architect |
| **6.1** | 2025-12-06 | Replaced Parasail validation with AI_Talent_Schema_Rules v3.0; schema and phase alignment update. | System Spec Refactor Agent |

---

**End of Document**

Proprietary Rights Notice
------------------------
All code, scripts, GitHub repositories, documentation, data, and GPT-integrated components of the AI Talent Engine – Signal Intelligence and Research_First_Sourcer_Automation Python Automation Sourcing Framework are strictly proprietary. All intellectual property rights, copyrights, trademarks, and related rights are exclusively owned by Dave Mendoza, DBA AI Craft, Inc.
No individual or entity may copy, reproduce, distribute, modify, create derivative works, reverse engineer, decompile, or otherwise use any part of this system, software, or associated materials for personal or commercial purposes without explicit written authorization from Dave Mendoza.
All rights reserved. Unauthorized use may result in legal action.
This statement is governed by the laws of the State of Colorado, USA.
