# EXECUTION CONTRACT — Research_First_Sourcer_Automation

## Canonical Entry
The ONLY executable Python entrypoint in this repository is:

EXECUTION_CORE/run_safe.py

No other Python file may be executed directly.

---

## Import-Only Modules (NON-EXECUTABLE)
The following files are import-only and MUST NEVER be executed directly:

- canonical_people_writer.py
- talent_intel_preview.py
- phase6_ai_stack_signals.py
- phase7_oss_contribution_intel.py
- name_resolution_pass.py
- people_scenario_resolver.py
- people_source_github.py

Any direct execution attempt is a contract violation.

---

## Writer of Record
File: canonical_people_writer.py

Responsibilities:
- Write canonical People CSVs
- Accept in-memory structures only

Prohibitions:
- No CLI
- No subprocess
- No phase execution
- No filesystem discovery

---

## Preview Rules
Preview code is OBSERVATIONAL ONLY.

Preview MUST:
- Never write files
- Never invoke writers
- Never invoke phases
- Never call subprocesses

Preview code is NOT part of execution.

---

## Subprocess Rule
Subprocess execution is FORBIDDEN.

Exception:
- Must be explicitly documented
- Must be justified in writing
- Must be approved before use

Silence is NOT permission.

---

## Enforcement
- Any new executable requires explicit review
- Any new writer requires explicit designation
- Any file without a declared role is NON-EXECUTABLE by default
- Negative guarantees are mandatory

