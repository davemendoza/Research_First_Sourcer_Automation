# GPT-Slim Integration Contract (Universal, Design-Only, LOCKED)
Version: v1.0.0-gptslim-design-locked
Owner: L. David Mendoza
Date: 2026-01-02
Project: Research_First_Sourcer_Automation

© 2026 L. David Mendoza – AI Talent Engine

## 0. Status
LOCKED DESIGN CONTRACT (NO EXECUTION, NO WIRING)

This document specifies how GPT-Slim will be integrated as an evaluation layer without changing:
- People Pipeline identity logic
- People Pipeline scoring logic
- Scenario row bounds or discard rules
- Canonical schema definitions
- Any primary scenario CSV artifacts

GPT-Slim is an evaluator only. It must never become a generator of identities or contacts.

## 1. Non-Negotiable Principles

### 1.1 Evaluator, Not Generator
GPT-Slim may:
- Read a validated People scenario CSV
- Produce a separate evaluation artifact keyed by Person_ID

GPT-Slim must never:
- Create people, names, GitHub accounts, URLs, emails, phones, resumes
- Fill blank contact fields
- Modify the primary People CSV
- Alter row counts or discard lists
- Alter schema logic

### 1.2 Truthful Sparsity
If evidence is not present in public sources or in the validated inputs, GPT-Slim outputs must reflect:
- "Insufficient evidence"
- A reason code
- A bounded confidence score that does not imply certainty

### 1.3 Fail-Safe Separation
If GPT-Slim fails for any reason:
- The People Pipeline output remains valid and authoritative
- The evaluation artifacts are not produced, or are produced as a single atomic write
- No partial or corrupt evaluation files are left behind

### 1.4 No Phantom CLI Flags
No wrapper may pass flags to a Python entry point that does not accept them.
Any future wiring must preserve 1:1 CLI parity with --help.

## 2. Invocation Boundary (When GPT-Slim Runs)

GPT-Slim evaluation is permitted only after:
1. A People scenario run completes successfully
2. The primary scenario CSV exists on disk
3. Post-generation validation passes:
   - Column order contract is satisfied
   - URL sanity checks are satisfied
   - Placeholder checks are satisfied
   - Demo bounds are satisfied when in demo mode

GPT-Slim is never invoked implicitly. It must be invoked as an explicit, gated step.

## 3. Inputs GPT-Slim Receives (Minimal, Safe Set)

### 3.1 Required input
- Primary People scenario CSV (validated)

### 3.2 Allowed input fields
GPT-Slim may consume only the fields needed for evaluation and auditability:
- Person_ID
- Canonical_Full_Name (or the live name column)
- Role_Type
- Identity_Status
- Identity_Confidence_Score
- Proof URLs and IDs (when present):
  - GitHub_URL, GitHub_IO_URL
  - HuggingFace_Profile_URL
  - ORCID
  - OpenAlex_Author_ID
  - SemanticScholar_Author_ID
  - GoogleScholar_Profile_URL
- Technical signal fields (when present):
  - LLM_Model_Names
  - RLHF_Methods
  - Inference_Stacks
  - Optimization_Techniques
  - Vector_DBs
  - RAG_Frameworks
  - GPU_Stack
  - Distributed_Systems
  - Serving_Frameworks
- Research summaries (when present):
  - Publication_Count
  - Citation_Count
  - Citation_Velocity
- Contact fields (read-only):
  - Public_Email
  - Public_Phone
  - LinkedIn_URL

GPT-Slim must not infer or invent missing proof sources.

## 4. Outputs GPT-Slim May Write (Separate Artifacts Only)

GPT-Slim writes only to a dedicated evaluation directory:
- outputs/gpt_slim/

GPT-Slim must never overwrite existing evaluation artifacts. Write-once per run.

### 4.1 Required evaluation artifact
A CSV keyed by Person_ID:
- outputs/gpt_slim/<scenario>_gpt_slim_eval_<run_id>.csv

### 4.2 Required fields in the evaluation CSV
- Person_ID
- GPT_Slim_Input_Eligible (true/false)
- GPT_Slim_Reason_Excluded (blank unless excluded)
- GPT_Slim_Evaluation_Status (pass / review / insufficient_evidence / error)
- GPT_Slim_Confidence_Score (0-100, bounded)
- GPT_Slim_Rationale (concise, evidence-referenced, no invented claims)
- GPT_Slim_Risk_Flags (optional; comma-separated enumerated flags)
- GPT_Slim_Model_Version (string)
- GPT_Slim_Timestamp (ISO-8601)

### 4.3 Optional evaluation metadata
- outputs/gpt_slim/<scenario>_gpt_slim_eval_<run_id>.json
Containing run-level metadata and summary counts.

## 5. Eligibility Gating Rules (Hard)

A row is eligible only if:
- Identity_Status is not unresolved
- At least one proof source exists (GitHub_URL, GitHub_IO_URL, HF URL, OpenAlex, S2, ORCID, personal site)
- Placeholder checks pass
- Required column order contract already passed validation

If ineligible:
- Mark GPT_Slim_Input_Eligible = false
- Provide a reason code in GPT_Slim_Reason_Excluded
- Do not block evaluation of other eligible rows

## 6. Failure Handling (Hard)

If GPT-Slim evaluation fails:
- Produce no output file, or produce a single file where all rows are GPT_Slim_Evaluation_Status = error
- Include a deterministic error summary in the JSON metadata
- Exit with non-zero status for the evaluation step only

The People Pipeline is not considered failed.

## 7. Change Control

This contract is LOCKED.
Any change requires:
- Version bump
- Rationale
- Updated validator semantics
- A green transcript of the evaluation step on a bounded dataset

## 8. Changelog

### v1.0.0-gptslim-design-locked (2026-01-02)
- Initial locked design-only GPT-Slim integration contract
- Strict separation of evaluator from pipeline outputs
- Deterministic artifact plan and gating rules
