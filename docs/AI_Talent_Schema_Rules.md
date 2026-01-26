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
# AI TALENT SCHEMA RULES — v3.3
# ENFORCED · PERFORMANCE-BOUNDED · REGRESSION-SAFE
# =============================================================================
#
# Maintainer: L. David Mendoza © 2025
# DBA: AI Craft, Inc.
# Proprietary & Confidential
#
# =============================================================================

schema_version: 3.3
status: active
deterministic: true
public_data_only: true

# -----------------------------------------------------------------------------
# GOVERNANCE
# -----------------------------------------------------------------------------
governance:
  agents_required:
    - 21
    - 22
    - 24
    - 36
  governance_ok_required: true
  audit_log_internal_only: true

# -----------------------------------------------------------------------------
# DATA SOURCE CLASSIFICATION (AUTHORITATIVE)
# -----------------------------------------------------------------------------
data_sources:

  allowed:
    - Publish or Perish (PoP)
    - ORCID
    - OpenAlex
    - Public Academic CV Websites

  academic_cv_domains:
    - "*.github.io"
    - "*.academia.edu"
    - "*.researchgate.net"
    - "*.university.*"
    - "*.edu"

  handling_rules:
    academic_cv_domains:
      treat_as: authoritative_academic_cv
      require_ocr: true
      allow_contact_extraction: true
      allow_affiliation_extraction: true
      disallow_not_publicly_available_if_visible: true

  forbidden:
    - Direct Google Scholar scraping
    - Private datasets
    - Inferred private contact data

# -----------------------------------------------------------------------------
# EXECUTION RULES
# -----------------------------------------------------------------------------
execution:
  allow_preamble: false
  allow_metadata_display: false
  allow_validation_text: false
  allow_execution_banners: false
  start_at_section: 1

# -----------------------------------------------------------------------------
# PERFORMANCE BUDGET — ENFORCED
# -----------------------------------------------------------------------------
performance_budget:
  ocr:
    max_passes_per_artifact: 1
    max_time_ms: 1000
    allow_cached_reuse: true
  identity_resolution:
    max_time_ms: 300
  rendering:
    max_time_ms: 500
  retries:
    scope: field_level_only
    forbid_full_regeneration_on_single_field_failure: true
  parallelism:
    allowed: true
    must_reconcile_before_section_1: true

# -----------------------------------------------------------------------------
# REGRESSION & CI ENFORCEMENT (MANDATORY)
# -----------------------------------------------------------------------------
regression_rules:
  forbidden_outputs:
    - visible_field_marked_not_publicly_available
    - skipped_ocr_when_screenshots_present
    - multiple_ocr_runs_same_artifact
    - full_regeneration_on_single_field_failure

  hard_fail_on_violation: true

# -----------------------------------------------------------------------------
# OUTPUT RULES
# -----------------------------------------------------------------------------
output:
  sections_required: 10
  partial_output: forbidden
  regeneration_on_failure: mandatory
  formatting: markdown
  tone: professional
  verbosity: executive

# -----------------------------------------------------------------------------
# DETERMINANT TABLE REQUIREMENTS
# -----------------------------------------------------------------------------
determinant_tables:
  table_a:
    skills: 10
    scale: 1-10
    required: true
  table_b:
    dimensions: 5
    weighted: true
    required: true

# -----------------------------------------------------------------------------
# DECISION RULE
# -----------------------------------------------------------------------------
decision:
  required: true
  allowed_values:
    - Submit
    - Monitor
    - Do Not Submit
  justification_required: true

# =============================================================================
# END OF FILE
# =============================================================================
