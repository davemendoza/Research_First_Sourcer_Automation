# ============================================================
#  AI Talent Schema Rules – Phase 9 Reference
#  Created by L. David Mendoza © 2025
# ============================================================

schema_reference: AI_Talent_Schema_Rules.md
schema_version: 3.5.0
phase_scope: Phase 9
maintainer: L. David Mendoza © 2025
last_validated: 2025-12-11
validation_status: Active

------------------------------------------------------------
Schema Purpose
------------------------------------------------------------
Defines extended predictive fields for trajectory modeling and future-role
fit estimation. Compatible with automation_build.py and Phase 8 validators.

------------------------------------------------------------
Schema Core Specification
------------------------------------------------------------
Field Name              | Type      | Description
------------------------|-----------|---------------------------------------------
schema_reference        | string    | Linked schema definition file
schema_version          | string    | Semantic version of schema
phase_scope             | string    | Current operational phase
maintainer              | string    | Maintainer / author
last_validated          | date      | Last validation date
validation_status       | string    | Current status
governance_agents       | list      | Required #21–#24
predictive_metrics      | list      | Predictive Hiring Intelligence fields
output_format           | string    | markdown / json

------------------------------------------------------------
Predictive Metrics
------------------------------------------------------------
•  signal_density_index  
•  trajectory_confidence  
•  influence_rank_percentile  
•  future_role_fit_estimate  

------------------------------------------------------------
Governance & Validation Agents
------------------------------------------------------------
#21 Schema Validator Agent – schema consistency  
#22 Audit & Provenance Agent – provenance / timestamps  
#23 Analytics Integrator – unified analytic datasets  
#24 Governance Compliance Agent – fairness / privacy  
------------------------------------------------------------

Proprietary Rights Notice
------------------------
All code, scripts, GitHub repositories, documentation, data, and GPT-integrated components of the AI Talent Engine – Signal Intelligence and Research_First_Sourcer_Automation Python Automation Sourcing Framework are strictly proprietary. All intellectual property rights, copyrights, trademarks, and related rights are exclusively owned by Dave Mendoza, DBA AI Craft, Inc.
No individual or entity may copy, reproduce, distribute, modify, create derivative works, reverse engineer, decompile, or otherwise use any part of this system, software, or associated materials for personal or commercial purposes without explicit written authorization from Dave Mendoza.
All rights reserved. Unauthorized use may result in legal action.
This statement is governed by the laws of the State of Colorado, USA.
