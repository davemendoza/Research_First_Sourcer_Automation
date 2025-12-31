# Day 4 — Auditability

## What Auditability Means Here

Auditability is the ability to **explain a run after it finishes**
without re-running anything and without reading code.

This system treats every execution as:
- Intentional
- Bounded
- Inspectable
- Explainable

---

## Core Artifacts

### Execution Manifest (existing)
Generated automatically at run completion.

It records:
- run identity
- timestamps
- steps executed
- outputs produced
- final status

### Audit Explainer (new)
`audit_explain_run.py` reads a manifest and explains it in plain English.

No execution.
No mutation.
No side effects.

---

## Interview-Safe Explanation

> “Every run emits a manifest.
> I can explain exactly what happened, why it happened,
> and where the evidence lives — without rerunning anything.”

This avoids:
- hand-waving
- code spelunking
- opaque automation concerns

---

## Usage

```bash
./audit_explain_run.py outputs/<path_to_manifest>.json

