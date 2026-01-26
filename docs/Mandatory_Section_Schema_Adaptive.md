execution_mode: silent_auto
preamble_output: false
introductory_text: false
validator_visible: false
governance_output_visible: false
show_phase_banner: false
require_user_confirmation: false
schema_validation_display: false
logging_mode: internal_only

# =============================================================================
# 🧩 MANDATORY SECTION SCHEMA — ADAPTIVE LOGIC v3.3
# EXECUTION-ENFORCED · OCR-HARD-LOCK · PERFORMANCE & VALIDATOR SAFE
# =============================================================================
#
# Maintainer: L. David Mendoza © 2025
# System: AI Talent Engine — Signal Intelligence
# Schema Reference: AI_Talent_Schema_Rules v3.3
# Phase Scope: 6 → 9
#
# This schema is the FINAL execution authority.
# Best practices are ASSUMED and MUST be enforced.
#
# =============================================================================

schema_reference: AI_Talent_Schema_Rules.md
schema_version: 3.3
validation_lock: true
deterministic_execution: true

governance_agents:
  - 21
  - 22
  - 24
  - 36

# -----------------------------------------------------------------------------
# OCR ENFORCEMENT — VISUAL & HTML-RENDERED CVS (HARD REQUIREMENT)
# -----------------------------------------------------------------------------
ocr:
  always_enabled: true

  force_on_domains:
    - "*.github.io"
    - "*.pages.dev"
    - "*.vercel.app"
    - "*.netlify.app"
    - "*.university.*"
    - "*.edu"

  force_on_conditions:
    - visual_profile_card_present
    - sidebar_identity_block_present
    - icon_labeled_contact_fields_present
    - screenshots_provided_by_user
    - academic_cv_layout_detected

  extraction_targets:
    - full_name
    - current_title
    - employer_affiliation
    - department
    - lab_or_group
    - city
    - state_or_region
    - country
    - corporate_email
    - personal_email
    - phone_number
    - google_scholar_url
    - github_url
    - linkedin_url
    - publications_link
    - cv_link

  forbidden_outputs_if_visible:
    - "Not Publicly Available"

  # ---------------------------------------------------------------------------
  # PERFORMANCE OPTIMIZATION — ENFORCED
  # ---------------------------------------------------------------------------
  caching:
    enabled: true
    cache_key: artifact_hash
    reuse_on_retry: true

  retry_strategy:
    mode: field_level
    max_retries_per_field: 2
    regenerate_full_evaluation: false

  execution_model:
    parallelize:
      - ocr_extraction
      - link_resolution
    reconcile_after_parallel: true

  failure_policy:
    if_ocr_not_executed: hard_fail
    if_visible_field_left_empty: hard_fail
    retry_until_extracted: true

# -----------------------------------------------------------------------------
# VALIDATOR SYMMETRY (PHASE-7 SAFE)
# -----------------------------------------------------------------------------
validator_symmetry:
  validators_must_respect:
    - ocr_cache_reuse
    - field_level_retry_only
    - no_full_regeneration_on_single_field_failure
  forbid_validator_side_effects:
    - re_running_ocr
    - serializing_parallel_steps
    - reclassifying_visible_fields_as_missing

# -----------------------------------------------------------------------------
# SECTION ORDER — IMMUTABLE
# -----------------------------------------------------------------------------
sections:
  - id: 1
    name: Candidate Overview
    required: true
  - id: 2
    name: Evidence Tier Ledger
    required: true
  - id: 3
    name: AI Classification / Role Type
    required: true
  - id: 4
    name: Career Trajectory
    required: true
  - id: 5
    name: Infrastructure & Systems Signals
    required: true
  - id: 6
    name: Strengths
    required: true
    min_items: 3
  - id: 7
    name: Weaknesses
    required: true
    min_items: 2
  - id: 8
    name: Citation & Influence
    required: true
  - id: 9
    name: Decision & Determinant Skills Tables
    required: true
  - id: 10
    name: Automated Hiring Manager Email
    required: true

# -----------------------------------------------------------------------------
# FAILSAFE & COMPLETION GUARANTEE
# -----------------------------------------------------------------------------
failsafe:
  suppress_all_logs: true
  suppress_all_preamble: true
  suppress_validation_output: true
  block_partial_outputs: true
  auto_regenerate_on_missing: true
  retry_until_valid: true

completion_requirements:
  determinant_table_required: true
  summary_table_required: true
  decision_required: true
  email_required: true
  audit_ready: true

# =============================================================================
# END OF FILE
# =============================================================================
