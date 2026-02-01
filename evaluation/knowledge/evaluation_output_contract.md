# ==============================================================================
# AI TALENT ENGINE – SIGNAL INTELLIGENCE
# Proprietary and Confidential
# © 2025–2026 L. David Mendoza. All Rights Reserved.
# ==============================================================================
#
# This file contains proprietary intellectual property and trade secrets of
# L. David Mendoza and is part of the AI Talent Engine – Signal Intelligence system.
#
# Unauthorized access, use, copying, modification, distribution, disclosure,
# reverse engineering, or derivative use, in whole or in part, is strictly
# prohibited without prior written authorization.
#
# ==============================================================================

# Evaluation Output Contract (v1.0.0) — Deterministic, Table-First, Fail-Closed

## A) Hard-Gated Sequence (MUST follow exactly)
1) Canonical role selection (canonical_role_registry.json)
2) Evidence ingestion (artifacts, links, provided text only)
3) Terminology normalization (terminology_normalization_map.json; Agent #51 governance only)
4) Determinant mapping (role_determinants_allowlists.json allow-lists only)
5) Tier gating (Tier 1 requires explicit Tier 1 hits; else Tier 2 if Tier 2 hits; else Indeterminate)
6) Benchmarks section (role-gated; benchmarks_registry.json)
7) Research impact metrics (role-gated; optional; never penalize absence)
8) Confidence band (High/Medium/Limited) based on evidence richness and clarity
9) Cohort segmentation (required when N >= 2; no cross-role ranking)
10) Ranking tables (required when N >= 2)
11) Role-lens reprojection (when requested; evidence unchanged)
12) Business impact (conditional; evidence-only)

## B) Single Candidate Output (Always Required)
- Canonical Role
- Tier
- Confidence Band
- Tier 1 hits (explicit list)
- Tier 2 hits (explicit list)
- Conditional hits (list + resolution status)

## C) Multi-Candidate Output (Required when N >= 2)
### C1) Cohort Segmentation
Group candidates by Canonical Role. No cross-role ranking.

### C2) Primary Ranking Table (per cohort)
Columns:
- Rank
- Candidate
- Tier
- Composite Score (numeric where defensible)
- Tier 1 hit count
- Tier 2 hit count
- Confidence Band

### C3) Benchmark Comparison Table (role-gated)
Columns:
- Candidate
- Benchmarks Worked On
- Model Context
- Production vs Research
- Adoption Signal

### C4) Research Metrics Table (research roles only; optional)
Columns:
- Candidate
- Citation Count
- h-index
- Citation Velocity (if available)

## D) Role-Lens Reprojection (Key Demo Feature)
Re-evaluate same evidence under multiple roles and show:
- Tier deltas
- Determinant deltas
- Ranking deltas (within each role cohort)
