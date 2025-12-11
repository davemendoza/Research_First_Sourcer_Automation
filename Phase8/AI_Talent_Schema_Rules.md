# ============================================================
#  AI Talent Schema Rules – Phase 8 Reference
#  Created by L. David Mendoza © 2025
# ============================================================

schema_reference: AI_Talent_Schema_Rules.md
schema_version: 3.4.1
phase_scope: Phase 8
maintainer: L. David Mendoza © 2025
last_validated: 2025-12-11
validation_status: Active

------------------------------------------------------------
Schema Purpose
------------------------------------------------------------
The AI Talent Schema Rules file defines the canonical field structure,
metadata format, and governance mapping used by the AI Talent Engine Phase 8
framework. It guarantees schema consistency between master documentation,
review templates, and validation agents.

Every Phase 8 file validated under this schema must contain:
•  A metadata header (schema_reference, schema_version, phase_scope, maintainer)
•  Governance agent coverage (#21–#24)
•  Evidence field alignment consistent with the AI Talent Review Template
•  Public-data-only compliance per Governance Compliance Agent #24

------------------------------------------------------------
Schema Core Specification
------------------------------------------------------------
Field Name              | Type      | Description
------------------------|-----------|---------------------------------------------
schema_reference        | string    | Linked schema definition file name
schema_version          | string    | Semantic version for schema alignment
phase_scope             | string    | Current operational phase identifier
maintainer              | string    | Responsible author / maintainer
last_validated          | date      | Date of last schema validation
validation_status       | string    | Current validation status
governance_agents       | list      | Required validation agents (#21–#24)
evidence_fields         | list      | Evidence attributes required by review template
output_format           | string    | Preferred output type (markdown/json)

------------------------------------------------------------
Evidence Fields
------------------------------------------------------------
•  candidate_header
•  evidence_tier_ledger
•  evaluation_sections
•  hiring_manager_submittal_decision
•  reviewer_provenance
•  governance_footer

------------------------------------------------------------
Governance & Validation Agents
------------------------------------------------------------
#21 Schema Validator Agent – schema consistency
#22 Audit & Provenance Agent – provenance / timestamps
#23 Analytics Integrator – unified analytic datasets
#24 Governance Compliance Agent – fairness / privacy
------------------------------------------------------------

------------------------------------------------------------
Compliance Rules
------------------------------------------------------------
1.  Master and schema files must declare identical schema_version and phase_scope.
2.  All four governance agents (#21–#24) must be present exactly once.
3.  Evidence fields must match the current AI Talent Review Template definition.
4.  Validation outputs should conform to markdown summary format unless json is requested.
5.  Public contact information must comply with Governance Agent #24 privacy rules.
------------------------------------------------------------

------------------------------------------------------------
Operational Notes
------------------------------------------------------------
This schema supersedes Phase 7 schema v3.3 and introduces:
• Expanded metadata header structure for predictive analytics compatibility  
• Standardized governance agent declarations  
• Phase-to-phase schema version tracking  
• Explicit evidence field alignment with the AI Talent Review Template v3.3  
• Cross-phase validation support for predictive hiring intelligence
------------------------------------------------------------

------------------------------------------------------------
Governance Summary
------------------------------------------------------------
Maintainer: L. David Mendoza © 2025  
Schema Version: 3.4.1  
Phase Scope: Phase 8  
Validation Status: Active  
Last Validated: 2025-12-11  
------------------------------------------------------------
