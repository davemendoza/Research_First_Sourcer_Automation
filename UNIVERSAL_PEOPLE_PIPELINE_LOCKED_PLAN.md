# AI Talent Engine – Universal People Pipeline (LOCKED Plan)
© 2026 L. David Mendoza. All rights reserved.

Version: v1.0.0-universal-locked
Status: LOCKED EXECUTION CONTRACT
Last Updated: 2026-01-01
Owner: L. David Mendoza
Scope: Universal People Identity + Harvest + Enrichment + Validation + Evaluation + Audit + CLI

-------------------------------------------------------------------------------

## 0) Why this exists
This file is the single source of truth for how the People pipeline is designed, executed, and validated.
It exists to prevent:
- identity-less rows
- schema drift
- demo-only hacks
- bypass paths under pressure
- silent empties
- “we assumed the module existed” failures

This plan is UNIVERSAL. It is not framed for any one company, meeting, or customer.

-------------------------------------------------------------------------------

## 1) Canonical truth rule (snapshots first)
We do NOT design or patch based on assumptions. We only act on verified repo state.

### Canonical snapshot files (must exist and be current)
- SNAPSHOT_SCHEMAS.json
- SNAPSHOT_HARVESTERS.json
- SNAPSHOT_ORCHESTRATION.json

### Snapshot integrity rule (hard stop)
If any snapshot indicates a critical file is placeholder/truncated/redacted (examples: "<PASTE FULL...>", "…", partial bodies),
THEN:
- STOP implementation decisions that depend on that file
- Re-snapshot the repo immediately
- Re-run inventory and update the snapshot set
No exceptions.

-------------------------------------------------------------------------------

## 2) Non-negotiable principle: Identity spine first
No person → no row → no enrichment → no CSV output.

### Identity Spine must exist BEFORE any enrichment and BEFORE any row write
Core identity fields (must all be present for a row to be written):
- Person_ID (deterministic stable hash)
- Canonical_Full_Name
- First_Name
- Last_Name
- Name_Source (github | github_io | hf | openalex | scholar | resume | linkedin)
- Identity_Status (unresolved | probable | confirmed)
- Identity_Confidence_Score (0.0–1.0)
- Identity_Sources (pipe-delimited list OR JSON array)
- Primary_Role_Family
- All_Role_Types (pipe-delimited, supports multi-fit)

Authority anchors (must be attempted in order; capture what exists):
- GitHub_Username
- GitHub_URL
- GitHub_IO_URL
- HuggingFace_Username
- HuggingFace_Profile_URL
- ORCID
- OpenAlex_Author_ID
- SemanticScholar_Author_ID

### Reject rules (stop-the-line)
If any core identity field is missing, the row is rejected and MUST NOT be written.
Rejected rows must include:
- Row_Validity_Status = rejected
- Rejection_Reason (explicit)
- Missing_Critical_Fields (pipe-delimited)
- Manual_Review_Flag (true/false)

-------------------------------------------------------------------------------

## 3) Authority order (fixed escalation, no bypass)
Authority escalation order is locked and may not be bypassed:

1) GitHub
2) GitHub.io
3) HuggingFace
4) OpenAlex / Semantic Scholar
5) Resume
6) LinkedIn

Rules:
- GitHub is an anchor, not a person.
- GitHub.io is mandatory to attempt and must be captured when present.
- For research-heavy roles, OpenAlex/Semantic Scholar attempts are mandatory (capture IDs or “attempted-not-found” provenance).
- Resume and LinkedIn are “discover if public,” never invented, always sourced.

-------------------------------------------------------------------------------

## 4) Locked schema contract (Word doc is canonical)
The canonical People schema is locked in:
- AI_Talent_Engine_People_Schema_LOCKED.docx

The pipeline must conform to that schema exactly.
The schema validator rejects incomplete identities; it does not fill or infer.

-------------------------------------------------------------------------------

## 5) Provenance and “no silent empties”
Every populated field must have provenance.
Every attempted-but-missing critical field must have explicit provenance.

### Required governance fields
- Field_Level_Provenance (JSON map OR pipe-map)
- Last_Verified_Timestamp
- Data_Freshness_Days
- Row_Validity_Status (valid | rejected | partial)
- Rejection_Reason
- Missing_Critical_Fields
- Manual_Review_Flag

“No silent empties” rule:
- If a field is blank, either it is truly not applicable OR it must be marked as attempted/not-found in provenance.

-------------------------------------------------------------------------------

## 6) Demo vs Daily (architecture identical, scale bounded only)
Demo and Daily runs must be identical in architecture.
The only difference is scale (bounded rows) and/or throttles.

Forbidden:
- separate codepaths
- alternate logic branches
- bypassing validation
- skipping authority escalation
- skipping provenance

-------------------------------------------------------------------------------

## 7) Plain-English CLI (mandatory, interview-safe)
No raw Python invocation required in demos or interviews.

The CLI must support:
- run frontier
- run daily
- run scenario <name>
- confirm last run
- email status

CLI parity rule:
Shell commands must map 1:1 to supported arguments.
No phantom flags.

-------------------------------------------------------------------------------

## 8) Completion email notification (mandatory)
A completion email must be sent on successful run completion.
It must be recorded in operational metadata:
- Completion_Email_Sent
- Completion_Email_Recipient
- Completion_Email_Timestamp
- Output_File_Path

If email cannot send (env/credentials), the run must still record:
- Completion_Email_Sent = false
- Rejection_Reason or Notification_Error in provenance/notes

-------------------------------------------------------------------------------

## 9) GPT-Slim contract (mandatory, deterministic)
GPT-Slim is an evaluator, not a generator.
It must operate only on eligible rows.

Required fields:
- GPT_Slim_Input_Eligible (true/false)
- GPT_Slim_Reason_Excluded
- GPT_Slim_Evaluation_Status
- GPT_Slim_Confidence_Score
- GPT_Slim_Rationale

Eligibility gating (minimum):
- Identity Spine passes
- Required evidence pack exists for the role family OR explicit attempt proof exists

No hallucination rule:
- GPT-Slim must never invent identity, publications, contact info, affiliations, or links.

-------------------------------------------------------------------------------

## 10) Universal “Morning Start” execution plan (one-day, world-class)
This is the exact order of operations for the morning.

### Hour 0–1: Snapshot integrity + architecture lock (NO CODE)
Deliverables:
1) Snapshot Integrity Report
   - list: complete vs placeholder/truncated modules
   - identify critical path breakpoints
2) Architecture Map (from snapshots only)
   - enumerators/harvesters
   - resolver
   - enrichment stages
   - schema validation and write stage
3) Explicit failure mode list (where identity was bypassed)

Hard stop condition:
- any critical module placeholder/truncated → re-snapshot immediately

### Hour 1–3: Identity spine design + resolver contract (NO CODE)
Deliverables:
1) PERSON object contract
   - required fields
   - provenance format
   - Identity_Status definitions
2) Identity confidence rubric (deterministic)
3) Rejection rules (stop-the-line), plus “manual review” rules
4) Dedupe keys and merge precedence rules

### Hour 3–5: Harvester sequencing + escalation (NO CODE)
Deliverables:
1) Authority escalation spec (locked order)
2) Required attempts per role family
3) “No-loss candidates” policy (probable vs confirmed)
4) Evidence pack definition per role family (what must exist or be proved attempted)

### Hour 5–6: CSV enforcement contract (NO CODE)
Deliverables:
1) Final schema list in exact order
2) Validator semantics (reject vs fill)
3) Output row statuses: valid/rejected/partial with explicit reasons

### Hour 6–7: CLI + completion email contract (NO CODE)
Deliverables:
1) Plain-English CLI command mapping
2) Completion email contract + audit fields
3) Confirm-last-run output contract

### Hour 7–8: GPT-Slim instruction contract (NO CODE)
Deliverables:
1) Required input columns
2) Eligibility gating
3) Output rubric fields and definitions
4) “No hallucinations” enforcement language

### Hour 8–9: Final universal demo run spec (NO CODE)
Deliverables:
1) Definition of DONE (acceptance checklist)
2) 25–40 person run constraints
3) Manual spot-check protocol
4) Freeze outputs and commit state

-------------------------------------------------------------------------------

## 11) Acceptance checklist (definition of DONE)
A run is DONE only if:
- 100% written rows have complete Identity Spine
- 0 anonymous rows
- GitHub_Username + GitHub_URL always present
- GitHub_IO_URL captured when present OR attempt recorded
- At least one of HF/OpenAlex/S2/Scholar present OR attempt proof recorded
- Publications logged OR “none found” with attempt proof
- Contact fields only when public, always with source
- Row_Validity_Status accurate (no silent “valid”)
- Output file path + run metadata fully recorded
- Completion email sent OR explicitly recorded as failed

-------------------------------------------------------------------------------

## 12) Change control (how we prevent disasters)
This file is LOCKED. Changes require:
- version bump
- changelog entry
- explicit rationale
- validation steps updated
- git commit with message referencing the version bump

-------------------------------------------------------------------------------

## CHANGELOG
- v1.0.0-universal-locked (2026-01-01): Initial locked universal execution contract for People pipeline.

-------------------------------------------------------------------------------

## Validation steps (required every morning start)
1) Confirm snapshots exist and are current:
   ls -la SNAPSHOT_SCHEMAS.json SNAPSHOT_HARVESTERS.json SNAPSHOT_ORCHESTRATION.json

2) Confirm locked schema doc exists:
   ls -la AI_Talent_Engine_People_Schema_LOCKED.docx

3) Confirm no placeholder/truncated critical modules per snapshots:
   (Manual review based on Snapshot Integrity Report; hard stop if found)

4) Confirm CLI contract exists (when implemented):
   - run frontier
   - run daily
   - run scenario <name>
   - confirm last run
   - email status

-------------------------------------------------------------------------------

## Git commands (after creating/updating this file)
git status
git add UNIVERSAL_PEOPLE_PIPELINE_LOCKED_PLAN.md
git commit -m "docs(people): lock universal people pipeline plan v1.0.0"
git push
