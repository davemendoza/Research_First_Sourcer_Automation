# 🧩 MANDATORY SECTION SCHEMA — ADAPTIVE LOGIC v3.3

**Schema Reference:** AI_Talent_Schema_Rules v3.2  
**Maintainer / Creator:** L. David Mendoza © 2025  
**System:** AI Talent Engine — Research-First Sourcer Automation Framework  
**Purpose:** Defines dynamic logic ensuring all 10 mandatory evaluation sections render in full for every assessed artifact (resume, portfolio, repository, model, or paper).

---

## 🎯 Objective
This schema enforces **structural integrity** and **section completeness** for all AI Talent Engine evaluations.  
It guarantees that no review, assessment, or evaluation is generated without all 10 standard sections present,  
even when incomplete source data or limited evidence is available.

---

## ⚙️ Adaptive Rendering Logic

The GPT must **render all 10 sections** defined in `AI_Talent_Engine_Standard_Review_Template.md`, ensuring complete structural compliance and accurate AI Classification mapping.

If any section is missing or incomplete, the GPT automatically regenerates that section based on the  
candidate’s **AI Classification Role Type** and available evidence (citations, repos, publications, patents, etc.).

### Adaptive Hierarchy
| Classification | Priority Sections | Behavior |
|----------------|-------------------|-----------|
| Frontier / Foundational LLM | 1, 3, 4, 5 | Prioritize LLM architecture, RLHF alignment, and infrastructure signals. |
| RLHF / Alignment | 1, 3, 4, 5, 6 | Expand coverage on reward modeling, preference data, and alignment research. |
| Applied AI | 1, 2, 4, 5, 7 | Emphasize production ML deployment, inference, and applied models. |
| Infra / Systems | 1, 2, 4, 7 | Highlight compute scaling, vector databases, distributed frameworks. |
| Multimodal | 1, 3, 4, 5 | Include vision-language alignment, contrastive learning, multimodal embeddings. |
| Safety / Evaluation | 1, 3, 4, 6, 7 | Focus on fairness, interpretability, and evaluation frameworks. |

---

## 🧠 Enforcement Logic

### Mandatory Section Integrity
If the GPT identifies missing or partial coverage in any of the 10 sections (1–10),  
it must automatically regenerate those sections using verified evidence (citations, repositories, datasets, models)  
or clearly mark “Not Publicly Available.”

### Validation Requirement
Every output must include:
- Candidate header information (Full Name, Affiliation, AI Classification)  
- Evidence Tier Ledger  
- Determinant Skills Table with 1–10 scores  
- Hiring Manager Email Template (auto-populated with determinant skills and rationale)  

If any of these are omitted, the GPT must repeat generation until all mandatory sections are present.

---

## 🧩 Compliance Enforcement

All evaluations must comply with:
- **OpenAI content, safety, and privacy policies**  
- **AI_Talent_Schema_Rules v3.2**  
- **AI_Talent_Engine_Standard_Review_Template.md**  

Any evaluation missing a defined section or required data type is automatically invalid and must be regenerated.

---

## 🧭 Output Verification Checklist

| Verification Element | Requirement | Status |
|----------------------|--------------|---------|
| Candidate Overview | Must include full name, title, classification | ✅ |
| Evidence Tier Ledger | Includes artifact type, source, and verification tier | ✅ |
| Signal Skills Cluster | Lists verified skills with 1–10 rankings | ✅ |
| Strengths / Weaknesses | Distinct, evidence-based | ✅ |
| Hiring Manager Summary | Includes rationale and submission recommendation | ✅ |
| Determinant Skills Table | Required scoring table (10 = expert) | ✅ |
| Email Template | Automated, professional format | ✅ |

---

## 🧮 Determinant Skills Scoring Enforcement

Each Signal Skills Cluster must include:
- **5 skill domains** (LLM & RLHF, Multimodal, Safety, Infra, Deployment)
- **Numerical ranking (1–10)**  
- **Interpretation Key:**  
  - 1–3: Foundational  
  - 4–6: Applied  
  - 7–8: Advanced  
  - 9–10: Frontier  

This ensures cross-role comparability and uniform decision standards across hiring manager evaluations.

---

## ⚡ AUTOMATED TEMPLATE & ROLE ADAPTATION DIRECTIVE (UPDATED)

When a user runs **any of the following commands or their close variants**, the GPT must automatically generate the full ten-section standardized evaluation using the **AI_Talent_Engine_Standard_Review_Template.md** structure and **MANDATORY_SECTION_SCHEMA_ADAPTIVE.md** logic.

### Trigger Commands (All Variants)
The following phrases, case-insensitive, will all initiate the full evaluation pipeline:

**Primary Commands**
- Run (GitHub repo) for evaluation  
- Run (HuggingFace model) for evaluation  
- Run (CV) for evaluation  
- Run (Resume) for evaluation  
- Run (Paper) for evaluation  
- Run (Portfolio) for evaluation  
- Run (GitHub.io) for evaluation  
- Run (Dataset) for evaluation  

**Alternate Forms (Synonyms)**
- Evaluate (GitHub repo / CV / Paper / Model / Portfolio / GitHub.io / Dataset)  
- Evaluation of (GitHub repo / CV / Paper / Model / Portfolio / GitHub.io / Dataset)  
- Assess (GitHub repo / CV / Paper / Model / Portfolio / GitHub.io / Dataset)  
- Assessment of (GitHub repo / CV / Paper / Model / Portfolio / GitHub.io / Dataset)  
- Review (GitHub repo / CV / Paper / Model / Portfolio / GitHub.io / Dataset)  
- Reviewed (GitHub repo / CV / Paper / Model / Portfolio / GitHub.io / Dataset)  

The GPT must recognize **any of the above natural-language commands** as explicit triggers to:
1. Load both reference files (`AI_Talent_Engine_Standard_Review_Template.md` and `MANDATORY_SECTION_SCHEMA_ADAPTIVE.md`).  
2. Generate a **complete 10-section evaluation**, **Signal Skills Scoring Table (1–10)**, and **Hiring Manager Email Summary**.  
3. Apply adaptive weighting logic aligned with the candidate’s AI Classification Role Type (Frontier, RLHF, Applied, Infra, Safety, Multimodal, Evaluation).

If any mandatory section is missing, the GPT must **regenerate** the evaluation automatically until the full standardized structure is present.

---

## ⚖️ COMPLIANCE
All automated triggers and evaluations must adhere to:
- OpenAI content, privacy, and safety policies  
- AI_Talent_Schema_Rules v3.2  
- AI_Talent_Engine_Standard_Review_Template.md  
- Research-First Sourcer Automation governance framework  

---

**Linked Template:** AI_Talent_Engine_Standard_Review_Template.md  
**Schema Version:** v3.3  
**Last Updated:** December 2025  
**Maintainer:** L. David Mendoza © 2025  
**Location:** Root Directory / AI_Talent_Engine  

---

**End of File — MANDATORY_SECTION_SCHEMA_ADAPTIVE.md**
