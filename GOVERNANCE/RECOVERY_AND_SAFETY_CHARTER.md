# RECOVERY & SAFETY CHARTER
## Research_First_Sourcer_Automation

**Status:** Authoritative  
**Scope:** Entire repository  
**Applies To:** All demos, interviews, recovery operations, and production runs  
**Enforcement Model:** Fail-closed, code-enforced, audit-first  

---

## 1. Purpose & Authority

This charter defines the **non-negotiable safety, recovery, and integrity rules** governing the
Research_First_Sourcer_Automation system.

These rules exist to:

- Prevent catastrophic data loss
- Eliminate ambiguous execution behavior
- Preserve auditability and evidence integrity
- Protect momentum during high-stress contexts (interviews, live demos, recovery)

**This charter overrides:**
- Convenience
- Speed
- Assumptions
- Defaults
- Tool “best practices”

If a conflict exists, **this charter wins**.

---

## 2. Absolute Prohibitions (Zero Tolerance)

The following actions are **forbidden under all circumstances**:

### 2.1 Deletion & Reset
- No file or directory deletion
- No `rm`, `rm -rf`
- No `git reset`, `git clean`, `git checkout --force`
- No “reinitialization” or “cleanup” of directories

### 2.2 Synthetic or Fabricated Data
- No fake people
- No fabricated GitHub profiles or repositories
- No placeholder emails, phones, CVs, URLs, or identities
- No duplicated filler identities

If real data is unavailable:
- Leave fields empty
- Clearly annotate source-of-record

Truthful sparsity is mandatory.

### 2.3 Silent Overwrites
- Canonical CSVs may not be overwritten
- Metadata JSONs may not be overwritten
- Inventory artifacts may not be overwritten without explicit approval

### 2.4 Phantom Interfaces
- No assumed CLI flags
- No undocumented shell aliases
- No imports of unverified functions
- No “reasonable guesses” about signatures or behavior

---

## 3. Execution Contract (Hard-Locked)

### 3.1 Single Authoritative Entrypoint
- `EXECUTION_CORE/run_safe.py` is the **only executable entrypoint**
- All other Python files are import-only unless explicitly declared otherwise

### 3.2 Mandatory Human Confirmation
- Every execution requires explicit YES confirmation
- Mode, role, input CSV, and output path must be printed before execution
- No bypass flags exist

### 3.3 Deterministic Outputs
- Each run produces a unique, timestamped output directory
- Outputs are append-only
- `LATEST.csv` is a pointer, never a source of truth

---

## 4. Inventory & Provenance Protection

### 4.1 Inventory Separation
Two inventory locations exist by design:

- `INVENTORY_FINAL/`  
  Canonical, locked, interview-grade  
  Never auto-overwritten

- `INVENTORY_AUDIT/`  
  Temporary, diagnostic, regeneratable  

No script may write to `INVENTORY_FINAL/` without explicit human approval.

### 4.2 Run Snapshots
Every execution must snapshot inventory artifacts into the run output directory to preserve:
- Schema context
- Repo state
- Provenance traceability

---

## 5. Recovery Mode Protocol (SEV-0)

Any of the following automatically triggers **SEV-0 DATA INCIDENT** status:

- Missing files
- Empty directories
- Disappearing outputs
- Inventory mismatches
- Unexpected artifact paths

**Required response:**
1. Stop all execution immediately
2. Preserve current state
3. Snapshot repository
4. Diagnose before touching anything

Recovery mode is **reduction-only**:
- Allowed: deletions, assertions, contract enforcement
- Forbidden: refactors, rewrites, new abstractions, new flags

---

## 6. Stress Lockdown Clause

During interviews, demos, or visible stress conditions:

- No refactors
- No architectural changes
- No scope expansion
- Minimal, contract-preserving fixes only

Speed without validation is forbidden.

---

## 7. Writers, Validators, and Previews (Strict Roles)

### 7.1 One Artifact, One Authority
Every artifact must have:
- Exactly one writer
- Exactly one declared output path
- Exactly one validator

### 7.2 Writers
- Are pure functions
- May not parse CLI args
- May not spawn subprocesses
- Must prove artifact existence

### 7.3 Validators
- May only validate artifacts actually produced
- May not assume filenames or paths

### 7.4 Preview Code
- Is observational only
- Must never mutate state
- Must never call pipeline phases or writers

---

## 8. Enforcement Mandate

Rules must be enforced by workflow, not memory.

Required enforcement includes:
- Preflight checks
- CLI flag parity validation
- Duplicate module detection
- Illegal token detection (EOF, heredoc artifacts)
- Role registry enforcement

If enforcement fails:
- Stop
- Fix enforcement first
- Do not proceed

---

## 9. Definition of “Done”

No workflow is considered:
- Ready
- Safe
- Fixed
- Interview-grade

Unless accompanied by:
- Exact command run
- Artifact paths produced
- Row and column counts
- Validation pass confirmation
- Green execution transcript

Claims without evidence are invalid.

---

## 10. Assistant Accountability

If an instruction causes:
- File corruption
- Execution breakage
- Lost time during live contexts

The response must be:
1. Halt further instructions
2. Produce a written post-mortem
3. Add permanent rules to prevent recurrence

Continuing without repair is forbidden.

---

## 11. Closing Statement (Binding)

This system is not a toy, demo, or experiment.

From this point forward:

- Nothing is deleted casually
- Nothing is reset
- Nothing is assumed expendable
- Stability, recoverability, and evidence preservation override speed

**Safety is enforced by structure, not discipline.**

