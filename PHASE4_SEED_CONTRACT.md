# ============================================================
# RESEARCH FIRST SOURCER AUTOMATION
# © 2026 L. David Mendoza. All Rights Reserved.
# ============================================================

# Phase 4 — Scenario Seed Contract (Authoritative)

## Output (Required)
Phase 4 produces the scenario seed CSV:

OUTPUTS/scenario/<role_slug>/<stem>_04_seed.csv

Where:
- role_slug is the scenario role identifier (e.g., frontier_ai_research_scientist)
- stem == role_slug (scenario contract)

Example:
OUTPUTS/scenario/frontier_ai_research_scientist/frontier_ai_research_scientist_04_seed.csv

## Rules (Non-Negotiable)
- No deletion, ever.
- No fabrication, ever.
- Preserve all input columns.
- Ensure Person_ID exists and is deterministic.
- Fail-closed if input CSV has 0 rows or invalid header.

## Person_ID
- If Person_ID exists and is non-empty, it is preserved.
- Else if person_id or id exists, it is mapped into Person_ID (original column remains).
- Else Person_ID is deterministically generated from strongest available identity surface:
  LinkedIn/GitHub/Email/Name, else row-position fallback.

## Relationship to Scenario Mode
Scenario mode remains strict:
- Scenario runs MUST NOT auto-generate seeds.
- Scenario starts Phase 5 only if this file exists at the required path.

## Operator Flow
1) Build the seed explicitly via phase4_seed_builder.py
2) Then run scenario:
   python3 -m EXECUTION_CORE.run_safe scenario <role_slug>
