---
phase: 7
version: "7.0"
label: "Citation & Influence Analytics"
schema_ref: "../AI_Talent_Schema_Rules.md"
changelog_ref: "../CHANGELOG.md"
audit_status: "PASS"
---

---
phase: 7
version: "7.0"
label: "Citation & Influence Analytics"
schema_ref: "../AI_Talent_Schema_Rules.md"
changelog_ref: "../CHANGELOG.md"
audit_status: "PASS"
---

---
file_type: system_specification
project: Research-First Sourcer Automation
version: 7.0
phase: 7
description: Citation-based intelligence and velocity mapping layer for AI Talent Engine. Detects, ranks, and classifies researchers by citation velocity, co-author networks, and influence clusters.
updated: 2025-12-04
---

# 🔬 AI Talent Engine — Phase 7: Citation Intelligence Module
**Version:** v7.0  
**Project:** Research-First Sourcer Automation  
**Owner:** AI Talent Engine Development Team  

---

## 1 · Purpose
Phase 7 introduces **Citation Intelligence**, an analytical layer that measures *research influence trajectories* and *collaboration networks* using citation data from Google Scholar and Semantic Scholar.  
It extends Phase 6 outputs to identify:
- High-velocity citation growth (“breakout” researchers)  
- Cross-lab collaboration clusters  
- Citation-based ranking tiers (50 K → 30 K → 10 K → 2.5 K)  
- Co-authorship influence graphs  

---

## 2 · Core Functions

### A · Citation Velocity Layer
Computes relative citation acceleration over the past 24 months.

```python
velocity = citations_last_24mo / total_citations


