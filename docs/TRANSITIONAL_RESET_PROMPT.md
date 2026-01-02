# Universal Lead Enrichment Pipeline  
## Exhaustive First-Run Standard — Demo-Ready or Stop

NEW CHAT RESET PROMPT (PASTE THIS AS THE FIRST MESSAGE)

---

## 0) Absolute Objective (Non-Negotiable)

The system must produce finished, demo-ready, world-class lead files on the **first successful run**, meeting **all** of the following simultaneously:

- **25–50 real leads minimum per demo run**
- **Column count may NEVER be reduced**
  - The **minimum column count is defined by the canonical People schema**
  - No scenario, demo, fallback, or partial mode may emit fewer columns
- **40–70+ columns per lead**, fully materialized where public data exists
- **Real enrichment evidence only**, never placeholders, prioritizing:
  - GitHub.io (first-class root)
  - Resume / CV links
  - Public contact info (email, phone only when actually published)
  - Social media (LinkedIn, X, Medium, Substack, YouTube, etc.)
  - Publications, patents, academic profiles when present

The pipeline **must generate a LEADS_MASTER CSV** that:

- Pops open automatically on completion
- Emails automatically on completion
- Fails hard if incomplete or invalid

Anything else is secondary until this is achieved.

---

## 1) Hard Constraints and Dev Rules (Must Obey)

You must follow these rules without exception:

- **Inventory-first, always**
  - Enumerate actual repo files and entry points before proposing changes
- **Full-file replacement only**
  - No snippets, no diffs, no partial edits
- **No interactive editors**
  - No nano, no vim, no open-and-edit
  - Only bash heredoc overwrite using `cat <<'EOF' > file`
- **Explicit paste boundaries**
  - Every file must be delivered as a complete paste-ready block
- **Path contracts are sacred**
  - Never invent paths or rename modules
- **Legacy must soft-skip**
  - INFO logs only, never hard-fail
- **No synthetic data ever**
  - Truthful sparsity is mandatory
- **CLI flag parity**
  - No phantom flags in wrappers
- **Enforcement must be in code**
  - Preflight + QA gates, never “remembered”

---

## 2) Canonical Output Schema Contract (Identity-First)

The **canonical People schema is the physical output spine**.

- The schema **must be materialized on disk**
- Every emitted CSV row must include **all schema columns**, even if blank
- Column order is enforced **before CSV write**
- Column presence is enforced **before CSV write**
- The schema may **never** exist only “on paper”

Schema families (non-exhaustive, must include all):

- Identity spine
- Contact and professional presence
- Research / publications / patents / x-ray
- Technical capability signals
- Governance / provenance / quality control
- Operational metadata
- GPT-Slim contract fields

---

## 3) What Is Already Fixed (Do Not Rework)

These are DONE and must not be revisited:

- Person_ID and Role_Type canonical prefix enforced
- Demo bounds logic exists (25–50 intended)
- Normalization phase is wired
- `run_safe.py` is the authoritative entrypoint
- Manifest creation exists
- Popup and email hooks exist
- Duplicate autogen scripts quarantined
- One execution path intended
- SSH Git workflow works
- CAT-based file generation pattern established

---

## 4) Critical Failures and Root Causes (Blockers)

These must be fixed before doing anything else.

### Failure A: Demo Count Violation

- Runs hard-failed below 25 leads

Root cause:
- Filtering or gating occurs **after** enrichment begins

Required fix:
- **Row-count enforcement must occur BEFORE enrichment**
- No enrichment step may reduce rows below 25
- If sources are thin, widen candidate pull **before** enrichment

---

### Failure B: Schema Collapse (Missing Columns)

- Output has fewer than required columns
- GitHub.io, resumes, social, publications, patents missing

Required fix:
- **Exhaustive-first enrichment**
- All columns emitted for all rows
- Column presence + order enforced before CSV write

---

### Failure C: GitHub.io Treated as Fatal

Incorrect behavior:
- HTTP 404 collapses the run

Correct contract:
- Probe execution must occur
- 404 is a valid outcome
- Only true execution failures are fatal
  - Exceptions
  - Corrupted response handling
  - DNS failures indicating code breakage

---

### Failure D: Evidence Depth Too Shallow

Missing mandatory value surfaces:

- Resume / CV scraping
- Portfolio discovery
- Academic links
- Patent discovery
- Company research personnel x-ray
- Social graph enrichment

These are **core value**, not optional.

---

## 5) Locked Priority Order (No Drift)

### Priority 1: Single Authoritative Exhaustive Enrichment Script

Create **one** authoritative script that:

- Runs only after demo row bounds are satisfied
- Guarantees the **full canonical People schema**
- Emits all columns per row, even if blank
- Treats GitHub.io as first-class root
- Never collapses demo runs

It must crawl, in order:

1. GitHub profile and repositories
2. GitHub.io (primary portfolio root when present)
3. Links discovered on GitHub and GitHub.io

Then extract:

- Public emails and phones (only if published)
- Resume / CV links
- Social links
- Academic profile links
- Patent signals
- Publications and citation signals
- Field-level provenance and timestamps

---

### Priority 2: Company Research Personnel X-Ray

Add a secondary enrichment surface:

- Crawl public research/team/blog author pages
- Extract names, roles, social links, public contact info
- Emit x-ray notes + provenance fields

---

### Priority 3: GitHub.io Elevation (Non-Optional)

GitHub.io is:

- Primary resume / portfolio root
- Academic and publication discovery hub
- Social link aggregation hub

Failure rules:

- Probe execution failure → FAIL
- HTTP 404 → CONTINUE

---

### Priority 4: GPT-Slim Instruction Update

GPT Slim must evaluate:

- Column completeness
- Evidence richness
- Schema adherence

Flag:

- Thin rows
- Placeholder data
- Missing enrichment surfaces

Emit a human-readable quality verdict.

---

### Priority 5: Plain-English, Child-Proof Commands

Create wrapper scripts such as:

- `run_frontier_demo.py`
- `run_applied_ai_demo.py`
- `run_infra_demo.py`

Each must:

- Explain behavior in plain English
- Enforce 25–50 bounds BEFORE enrichment
- Be impossible to misuse
- Print progress without spam
- Produce LEADS_MASTER
- Pop open CSV
- Email completion
- Fail closed if QA fails

---

## 6) LEADS_MASTER Writer-of-Record (PHANTOM PATH FIX)

This is locked and non-negotiable.

- **Scenario runners DO NOT write LEADS_MASTER**
- Scenario runners may write scenario-scoped CSVs only
- **Exactly one script is the writer-of-record**

Writer-of-record responsibilities:

- Materialize LEADS_MASTER **after** scenario CSVs complete
- Merge scenario outputs deterministically
- Enforce:
  - Canonical schema
  - Column order
  - Column presence
  - Demo row bounds
- Run final QA validation
- Write LEADS_MASTER to a single, explicit file path
- Open LEADS_MASTER automatically
- Email LEADS_MASTER automatically

Validation rules:

- LEADS_MASTER path must be written by the writer-of-record
- Validators may only validate artifacts explicitly promised by the scenario registry
- No script may assume a CSV exists without verifying the writer-of-record

This design **eliminates phantom output paths permanently**.

---

## 7) Explicit Non-Goals (Do Not Drift)

You must not:

- Re-debate schema philosophy
- Re-invent orchestration
- Add new flags casually
- Optimize prematurely
- Touch already-fixed normalization logic

---

## 8) Definition of Done (Only This Counts)

We are done only when **one demo run** produces:

- 25–50 real leads
- Full canonical People schema (no column reduction)
- Visible public evidence per lead when available

And the output:

- Pops open automatically
- Emails automatically
- Passes all QA gates

I must be able to open the file and show it immediately with no explanation.

---

## 9) Operating Instruction

You are not allowed to move on until the first demo run meets this standard.

Enrichment depth is the primary objective.

GitHub.io, resumes, contact info, social media, publications, and patents are **first-class citizens**, not optional extras.

