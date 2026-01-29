# ============================================================
# RESEARCH FIRST SOURCER AUTOMATION
# © 2026 L. David Mendoza. All Rights Reserved.
# ============================================================

# Phase 3 — Integration Verification / System Coherence (Authoritative)

## Scope (Non-Negotiable)
Phase 3 verifies that:
- Demo runs cleanly from entry to Phase 7.
- Scenario remains strict and fail-closed (requires Phase 4 seed).
- Phase contracts (consume/emit paths) are explicit and stable.
- OUTPUTS is stable: no loose partials; intermediates are archived (never deleted).

This phase does NOT redesign Phases 5–7 and does NOT rewrite audited files.

---

## Canonical Root (Hard Gate)
Run:
  pwd

PASS only if:
  /Users/davemendoza/Desktop/Research_First_Sourcer_Automation

STOP if not exact.

---

## Phase Contracts (Consume / Emit)

### Entry: EXECUTION_CORE/run_safe.py
Invocation styles:
- Mode-aware (recommended):
    python3 -m EXECUTION_CORE.run_safe demo <role>
    python3 -m EXECUTION_CORE.run_safe scenario <role>
- Legacy:
    python3 EXECUTION_CORE/run_safe.py <role>   (treated as scenario)

Output base:
- scenario: OUTPUTS/scenario/<role_slug>/
- demo:     OUTPUTS/scenario/demo/   (intentional so Phase 5 can detect demo context)

Canonical frontier stem:
- role aliases including "frontier" normalize to:
    frontier_ai_research_scientist

Expected filenames in the base:
- Phase 4 seed: <stem>_04_seed.csv
- Phase 5 out:  <stem>_05_phase5.csv
- Phase 6 out:  <stem>_06_phase6.csv
- Phase 7 out:  <stem>_07_phase7.csv

Archive behavior:
- After success, Phase 5/6 outputs are moved (never deleted) into:
  OUTPUTS/_ARCHIVE_partial_runs/scenario/<mode>/<stem>/<YYYYMMDD_HHMMSS>/

Only Phase 7 remains active in the base folder after a successful run.

---

## Demo vs Scenario Rules (Fail-Closed)

### Scenario
- REQUIRES existing Phase 4 seed:
    OUTPUTS/scenario/<role_slug>/<stem>_04_seed.csv
- If missing, run_safe must fail with an actionable error.
- Scenario MUST NOT use demo fallback.

### Demo
- Allowed to start without a Phase 4 seed in OUTPUTS/scenario/demo.
- Demo fallback is allowed ONLY inside Phase 5:
  If the expected demo seed is missing, Phase 5 resolves exactly ONE:
    OUTPUTS/demo/**/*.FULL.csv
  If none exist: fail.
  If more than one exist: fail (ambiguity).

---

## Verification Commands (Required)

### 1) Imports (repo coherence)
python3 -c "from EXECUTION_CORE.phase5_passthrough import process_csv as p5; from EXECUTION_CORE.phase6_ai_stack_signals import process_csv as p6; from EXECUTION_CORE.phase7_oss_contribution_intel import process_csv as p7; print('OK: imports')"

PASS: prints OK: imports

### 2) Scenario fail-closed (missing seed)
python3 -m EXECUTION_CORE.run_safe scenario frontier_ai_research_scientist

PASS: fails with RuntimeError explaining missing:
  OUTPUTS/scenario/frontier_ai_research_scientist/frontier_ai_research_scientist_04_seed.csv

### 3) Demo fallback prerequisites
find OUTPUTS/demo -type f -name "*.FULL.csv" -print

PASS: exactly one file printed

### 4) Demo end-to-end run
python3 -m EXECUTION_CORE.run_safe demo frontier

PASS: writes Phase 7 and archives Phase 5/6 intermediates.

### 5) Output stability check (no loose partials active)
ls -la OUTPUTS/scenario/demo

PASS:
- <stem>_07_phase7.csv exists
- <stem>_05_phase5.csv and <stem>_06_phase6.csv do NOT exist (archived)

### 6) Archive recoverability check
find OUTPUTS/_ARCHIVE_partial_runs -type f \\( -name "*_05_phase5.csv" -o -name "*_06_phase6.csv" \\) -print | tail -n 50

PASS: shows timestamped archive paths containing Phase 5/6 artifacts.

---

## Definition of Done (Phase 3)
Phase 3 is DONE only when all required commands above:
- PASS in the canonical root
- Produce expected outputs and expected failure modes
- Confirm archives are present and timestamped
- Confirm no loose partials remain active in OUTPUTS/scenario/demo or scenario role folders after success
