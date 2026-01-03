# ===============================================
#  © 2025 Dave Mendoza, DBA AI Craft, Inc. All rights reserved.
#  Proprietary and Confidential — Unauthorized copying or distribution is prohibited.
# ===============================================

# AI Talent Engine – Phase 6 Master Specification
Version 6.0 · December 2025  

The AI Talent Engine is a 26-agent research-grade sourcing and enrichment system aligned to the **Research-First Sourcer Automation** project.

---

## 1 · Purpose
Unifies academic, corporate, and portfolio intelligence to identify, classify, and enrich AI/ML researchers and engineers across Frontier, RLHF, Infra, and Multimodal domains.

---

## 2 · Core Schema
**Column 1:** AI_Classification  
Followed by Full_Name · Company · Team_or_Lab · Title · Seniority · Contact · Tech Signals · Research Evidence · Qualitative · Provenance.  
Validated by *Parasail Schema Rules*.

---

## 3 · Phase 6 Agents
17 · Public Portfolio & Contact Intelligence  
18 · Academic Lab Intelligence  
19 · Global Conference Intelligence (Frontier + Infra + RLHF)  
20 · Citation Network Mapping  
21 · Competitive Movement Tracking  
22 · RLHF & Post-Training Intelligence  
23 · MLSys / Distributed Systems & GPU Infra  
24 · Multimodal & Reasoning Models  
25 · AI Luminary & Awards Intelligence  
26 · Corporate AI Research X-Ray  

Each agent extracts domain-specific signals and outputs standardized CSV rows.

---

## 4 · Integration Pipeline
Phase 0–5 → Data collection  
Phase 6 → Research agent activation  
Phase 7 → Citation analytics  
Phase 8 → Visualization & reporting  

Output directory: `/output/intelligence/*.csv`

---

## 5 · Key Behavior
* Rank citations & RLHF signals highest.  
* Merge GitHub + Scholar + Portfolio for identity confidence.  
* Include only public contact data.  
* Auto-assign AI_Classification by stack context.  
* Keep source URLs for audit.

---

## 6 · References
See also `AI_Talent_Engine_Phase7_Citation_Intelligence.md` and `Parasail_Schema_Rules.md`

Proprietary Rights Notice
------------------------
All code, scripts, GitHub repositories, documentation, data, and GPT-integrated components of the AI Talent Engine – Signal Intelligence and Research_First_Sourcer_Automation Python Automation Sourcing Framework are strictly proprietary. All intellectual property rights, copyrights, trademarks, and related rights are exclusively owned by Dave Mendoza, DBA AI Craft, Inc.
No individual or entity may copy, reproduce, distribute, modify, create derivative works, reverse engineer, decompile, or otherwise use any part of this system, software, or associated materials for personal or commercial purposes without explicit written authorization from Dave Mendoza.
All rights reserved. Unauthorized use may result in legal action.
This statement is governed by the laws of the State of Colorado, USA.
