# ===============================================
#  © 2025 Dave Mendoza, DBA AI Craft, Inc. All rights reserved.
#  Proprietary and Confidential — Unauthorized copying or distribution is prohibited.
# ===============================================

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

Proprietary Rights Notice
------------------------
All code, scripts, GitHub repositories, documentation, data, and GPT-integrated components of the AI Talent Engine – Signal Intelligence and Research_First_Sourcer_Automation Python Automation Sourcing Framework are strictly proprietary. All intellectual property rights, copyrights, trademarks, and related rights are exclusively owned by Dave Mendoza, DBA AI Craft, Inc.
No individual or entity may copy, reproduce, distribute, modify, create derivative works, reverse engineer, decompile, or otherwise use any part of this system, software, or associated materials for personal or commercial purposes without explicit written authorization from Dave Mendoza.
All rights reserved. Unauthorized use may result in legal action.
This statement is governed by the laws of the State of Colorado, USA.
