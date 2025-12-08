# AI Talent Schema Rules (v3.7-F+)
**System Specification — AI Talent Engine | Phase-7+ Autonomous Schema**

---

## 📘 Overview
This document defines the **canonical and self-updating schema** for all validated AI Talent dossiers, intelligence summaries, and evidence maps used by the AI Talent Engine.

The `v3.7-F+` release introduces **automated schema synchronization** and **dynamic compliance self-healing** to reduce manual maintenance across phases.

---

## 🧩 Canonical Columns Definition
<!-- canonical:columns:start -->

| Field | Type | Description | Required | Constraints / Notes |
|-------|------|-------------|-----------|----------------------|
| `Candidate_Overview` | dict | Core metadata (name, title, affiliations, summary). | ✅ | must exist |
| `Role_Classification` | list | Primary + secondary research/engineering roles. | ✅ | ≥ 1 |
| `Organizational_Context` | text | Institutional, team, or lab-level context summary. | ✅ | non-empty |
| `Core_Technical_Signals` | list | Research or engineering artifacts (papers, code, models, patents). | ✅ | ≥ 3 items |
| `Career_Trajectory` | dict | Stage, progression, and velocity of influence. | ✅ | must include `stage` + `velocity` |
| `Strengths` | list | Evidence-based strengths tied to verifiable artifacts. | ✅ | ≥ 3 |
| `Weaknesses` | list | Evidence-based gaps or limitations. | ✅ | ≥ 3 |
| `False_Positive_Check` | bool | Indicates branding-only or misattributed profiles. | ✅ | true / false |
| `Hiring_Intelligence_Summary` | dict | Weighted quantitative metrics + summary text. | ✅ | must include weight map |
| `Evidence_Map_JSON` | json | Array of verifiable artifacts (papers, repos, models, patents). | ✅ | ≥ 3 items |
| `Hiring_Manager_Summary_Text` | text | Executive summary for decision brief. | ✅ | non-empty |
| `Citation_Velocity_Score` | float | Derived quantitative metric (0–1 normalized). | ✅ | auto-generated |
| `Influence_Tier` | enum | Tier (Frontier / Applied / Growth / Emerging). | ✅ | must match allowed list |
| `Collaboration_Count` | int | Number of unique collaborators. | ✅ | ≥ 0 |
| `Last_Validated` | datetime | UTC timestamp of validation. | ✅ | auto-set |
| `Schema_Version` | text | Reference to canonical schema version. | ✅ | must match current release |
| `Schema_Checksum` | text | Auto-generated integrity hash. | ✅ | auto-set |
<!-- canonical:columns:end -->

---

## 🧠 Canonical Section Order
1. Candidate_Overview  
2. Role_Classification  
3. Organizational_Context  
4. Core_Technical_Signals  
5. Career_Trajectory  
6. Strengths  
7. Weaknesses  
8. False_Positive_Check  
9. Hiring_Intelligence_Summary  
10. Evidence_Map_JSON  
11. Hiring_Manager_Summary_Text  

> **Rule:** Field order is binding and validated through positional hashing during Phase-7+ processing.

---

## ⚖️ Competency Weights (Normalized)
```yaml
competency_weights:
  Research_Impact: 0.30
  Engineering_Implementation: 0.25
  Collaboration_Scope: 0.15
  Publication_Quality: 0.10
  Model_or_Code_Release: 0.10
  Translational_Impact: 0.10

validation:
  enforce_weight_sum: true
  tolerance: 0.001
  failure_mode: "hard"
