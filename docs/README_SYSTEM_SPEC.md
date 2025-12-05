---
file_type: documentation_index
project: Research-First Sourcer Automation
version: 1.0
description: Cross-reference and functional summary of all system specification (.md) files used in GPT Knowledge and local execution.
updated: 2025-12-04
---

# 🧭 AI Talent Engine — System Specification Index
**Repository:** Research_First_Sourcer_Automation  
**GPT Instance:** AI TALENT ENGINE Search Agent Intel Library  
**Phases Covered:** 6–7  
**Schema Backbone:** AI_Talent_Schema_Rules.md

---

## 🧩 1. AI_Talent_Engine_Phase6_Master.md
**Agent:** Corporate Research X-Ray + Research Agent Network  
**Pipeline Role:** Phase 6 — Active Intelligence Extraction  

| Component | Description |
|------------|-------------|
| **Purpose** | Orchestrates 25 AI domain-specific agents to unify academic, corporate, and open-source research intelligence. |
| **Core Output** | Generates structured CSVs (one researcher per row) following the canonical AI_Talent_Schema_Rules schema. |
| **Agents** | Public Portfolio, Academic Lab, Conference, Citation, RLHF/Post-Training, MLSys, Multimodal, and Corporate X-Ray modules. |
| **Integration Stage** | Activated after Phase 5 data collection; feeds Phase 7 Citation Intelligence. |
| **Key Rules** | Prioritize RLHF & citation signals; merge GitHub + Scholar + Portfolio for identity validation; maintain provenance URLs. |

**Pipeline Role:**  
Acts as the research-grade enrichment core, transforming raw entity data into standardized talent intelligence outputs.

---

## 🔬 2. AI_Talent_Engine_Phase7_Citation_Intelligence.md
**Agent:** Citation Network Mapping  
**Pipeline Role:** Phase 7 — Citation Velocity & Influence Analytics  

| Component | Description |
|------------|-------------|
| **Purpose** | Extends Phase 6 outputs by ranking researchers via citation velocity, co-author influence, and collaboration graphs. |
| **Functions** | ① Compute citation velocity (24-month acceleration) ② Detect cross-lab clusters ③ Rank citation tiers (50K → 2.5K) ④ Build influence networks. |
| **Output Columns** | Fills `Citation_Trajectory`, `Research_Areas`, and `Strengths` / `Weaknesses` fields. |
| **Sources** | Google Scholar and Semantic Scholar APIs. |
| **Integration Stage** | Runs post-enrichment to generate ranking and collaboration metrics for analytic dashboards. |

**Pipeline Role:**  
Serves as the analytical layer quantifying research impact, feeding into hiring velocity and collaboration analytics.

---

## 🧬 3. AI_Talent_Schema_Rules.md
**Agent:** Schema Validator  
**Pipeline Role:** Cross-Phase — Canonical Schema Enforcement  

| Component | Description |
|------------|-------------|
| **Purpose** | Defines canonical column order, normalization logic, and enumerations for all agent outputs (Phases 5–8). |
| **Coverage** | 35 standardized fields — from `AI_Classification` to `Last_Updated`. |
| **Validation Logic** | Ensures consistent data types, normalized roles (Frontier / RLHF / Infra / Multimodal / Safety / Evaluation). |
| **Key Calculations** | Includes formula for `Citation_Trajectory` = `citations_last_24mo / total_citations`. |
| **Integration Stage** | Enforces schema during merging, deduplication, and ingestion to analytics systems. |

**Pipeline Role:**  
Acts as the data contract and validator, ensuring that outputs from Phase 6 (intelligence) and Phase 7 (analytics) remain interoperable.

---

## 🔗 Pipeline Connectivity Overview

| Phase | Module | Input | Output | Dependency |
|-------|---------|--------|---------|-------------|
| **Phase 6** | Agent Network (17–25) | Raw data (GitHub, Scholar, corporate) | Enriched researcher profiles | Validated by AI_Talent_Schema_Rules |
| **Phase 7** | Citation Intelligence | Phase 6 output CSVs | Ranked influence metrics, velocity tiers | Schema field: `Citation_Trajectory` |
| **Global** | Schema Rules | All Agent Outputs | Schema-compliant analytics dataset | Enforced continuously |

---

## 🧠 Summary Connection
- **Phase 6 = Intelligence Extraction**  
- **Phase 7 = Citation & Influence Analytics**  
- **AI_Talent_Schema_Rules = Normalization Backbone**

Together, they form a **research-to-insight pipeline:**
> *Raw profiles → Enriched Intelligence → Ranked Influence → Analytics Dashboards*

---

## 🧮 Version Control & Revision History
**File:** README_SYSTEM_SPEC.md  
**Project:** Research_First_Sourcer_Automation  
**Maintainer:** Dave [Core Architect, AI Talent Engine]  
**Tracking Scope:** Phases 5–8 (System Documentation)

| Version | Date | Updated By | Change Summary | Related Files |
|----------|------|-------------|----------------|----------------|
| **v1.0** | 2025-12-04 | Dave / ChatGPT-5 | Initial system specification summary and schema alignment across Phases 6–7. | AI_Talent_Schema_Rules.md, AI_Talent_Engine_Phase6_Master.md, AI_Talent_Engine_Phase7_Citation_Intelligence.md |
| **v1.1 (planned)** | 2026-01 | Dave | Add Phase 8 module (“Talent Radar Intelligence Agent”) and associated integration logic. | AI_Talent_Engine_Phase8_Talent_Radar.md |
| **v1.2 (planned)** | TBD | Dave | Add Phase 9 (“Predictive Hiring Intelligence”) and update schema for career trajectory fields. | AI_Talent_Schema_Rules.md, Phase9 module |
| **v2.0 (future)** | TBD | Dave / Engineering | Merge all phase outputs into unified GraphQL endpoint for analytics dashboard integration. | system_spec, phase9, dashboard |
| **v2.1 (future)** | TBD | Dave / AI Ops | Incorporate pipeline automation and self-healing enrichment jobs. | orchestrator_config.yaml, CI/CD scripts |

---

### 🧠 Notes
- Maintain semantic versioning (`major.minor`) for clarity and automation triggers.  
- Each phase document should include its own YAML front matter with `version:` and `updated:` fields.  
- Any schema or pipeline change affecting CSV output **must** increment the minor version and update `AI_Talent_Schema_Rules.md`.  
- When introducing a new phase (8+), append its `.md` file reference to this table and commit under `/docs/system_spec/`.  

---

**End of README_SYSTEM_SPEC.md**

