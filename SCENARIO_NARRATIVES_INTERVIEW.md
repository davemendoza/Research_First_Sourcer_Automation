# Scenario Narratives — Interview-Safe Execution Guide  
Version: Day4-v1.0  
Date: 2025-12-30  
Author: L. David Mendoza  
© 2025 L. David Mendoza. All Rights Reserved.

---

## How to Use This Under Interview Pressure (Child-Proof)

1. Pick a scenario name **verbatim** from this document.
2. Decide execution envelope:
   - Prefix with **`demo:`** for a short, bounded, interview-safe run.
   - Use the name **without prefix** for exhaustive, production-grade runs.
3. Read or paste the prompt exactly.
4. Change **only declared variables** (Top N, Tier scope, repo family).
5. Execute only through `run_safe.py`.

Nothing else exists. Nothing else runs.

---

## Critical Design Principle (Say This Out Loud)

> “Each scenario has two declared envelopes.  
> A `demo:` envelope optimized for speed and clarity,  
> and an exhaustive envelope optimized for completeness.  
> The logic never changes — only the execution envelope does.”

This is intentional governance, not a shortcut.

---

## Execution Envelope Rules (Non-Negotiable)

| Envelope | Purpose | Runtime Expectation | When to Use |
|--------|--------|--------------------|-------------|
| `demo:` | Demonstrate logic | Seconds–low minutes | Interviews, live reviews |
| (no prefix) | Achieve completeness | Minutes–hours | Production, async runs |

Prefixes **never** change logic, pipelines, or safety gates.  
They only declare intent and default variable bounds.

---

# CORE SCENARIOS (HIGH-CONFIDENCE, INTERVIEW-READY)

---

## 1. demo: Frontier OSS Radar (Top Contributors)

**Use when asked:**  
“How do you identify frontier-level contributors?”

**What it demonstrates:**  
Evidence-based ranking across foundational LLM and inference repos.

**What it intentionally ignores:**  
Private work, non-OSS contributions, location.

**Demo envelope defaults:**  
- Top 25–50 contributors  
- Tier 1 repos only  

**Exhaustive envelope:**  
- All tiers  
- Full contributor population  

**Why this is safe live:**  
Bounded input, deterministic ranking, fast return.

---

## 2. demo: Multi-Repo Frontier Builders

**Use when asked:**  
“How do you distinguish depth from surface activity?”

**What it demonstrates:**  
Cross-repo contribution as a proxy for sustained impact.

**Anti-gaming property:**  
Single-repo keyword stuffing cannot dominate.

**Demo envelope defaults:**  
- ≥2 frontier repos  
- Top 25 ranked  

**Exhaustive envelope:**  
- All qualifying contributors across all repos  

---

## 3. demo: Inference / Kernel Performance Radar

**Use when asked:**  
“How do you find performance-critical engineers?”

**What it demonstrates:**  
Signal extraction from Triton, FlashAttention, TensorRT-LLM, vLLM.

**What it does NOT do:**  
Claim runtime benchmarks or private infra access.

**Demo envelope defaults:**  
- Top 25 contributors  
- One repo family  

**Exhaustive envelope:**  
- All inference-related repos  
- Full contributor set  

---

## 4. demo: Distributed Training & Scaling Infra

**Use when asked:**  
“How do you surface training-scale infrastructure talent?”

**What it demonstrates:**  
OSS evidence across DeepSpeed, Megatron-LM, Ray.

**Boundary condition:**  
Not suitable for evaluating applied ML engineers.

**Demo envelope defaults:**  
- Top 25 contributors  
- One framework family  

**Exhaustive envelope:**  
- All infra repos  
- Cross-framework contributors  

---

## 5. demo: Applied LLM Tooling Builders

**Use when asked:**  
“How do you find applied engineers, not researchers?”

**What it demonstrates:**  
Product-minded OSS activity in Transformers, TGI, SGLang, llama.cpp.

**Why it matters:**  
Shows differentiation between frontier and applied roles.

**Demo envelope defaults:**  
- Top 25 contributors  

**Exhaustive envelope:**  
- All applied tooling repos  
- Tier 1–2 orgs  

---

# HIGH-YIELD SAFETY-NET SCENARIOS (ANTI-EMBARRASSMENT)

These exist so you **never** get a low-result run live.

---

## 6. demo: High-Density Frontier Ecosystem (Narrative)

**Use when asked:**  
“Show me scale.”

**What it demonstrates:**  
Volume + narrative without filtering or ranking bias.

**Critical rule:**  
Location is descriptive only, never a scoring factor.

**Demo envelope defaults:**  
- One large GitHub org repo family  
- Top 100 contributors  

**Exhaustive envelope:**  
- All frontier org repos  
- Thousands+ contributors  

---

## 7. demo: Company-Tier Competitive Landscape (Tier 1)

**Use when asked:**  
“How does this compare across competitors?”

**What it demonstrates:**  
Competitive OSS impact mapping.

**Why this is powerful:**  
Instant OpenAI/Anthropic/DeepMind context.

**Demo envelope defaults:**  
- Tier 1 only  
- Top 100 contributors  

**Exhaustive envelope:**  
- Tier 1–3  
- Full landscape  

---

# ELITE SCENARIOS (OPENAI-LEVEL SIGNALING)

These are not always run live — they exist to show depth.

---

## 8. Conference Authors → OSS Bridge

**Use when asked:**  
“How do you connect research to real engineering output?”

**What it demonstrates:**  
Research-to-code translation.

**Why this is elite:**  
Very few systems link publications to OSS impact.

**Demo envelope defaults:**  
- Top 25 authors with OSS overlap  

**Exhaustive envelope:**  
- All qualifying authors across years  

---

## 9. Patent Inventors → OSS Bridge

**Use when asked:**  
“How do you uncover non-obvious talent?”

**What it demonstrates:**  
Cross-signal intelligence beyond resumes.

**Boundary condition:**  
Lower yield; used for depth, not speed.

**Demo envelope defaults:**  
- Top 10–15 results  

**Exhaustive envelope:**  
- All qualifying inventors  

---

# GOVERNANCE & FAILURE MODE STATEMENTS (MEMORIZE)

Use these verbatim if challenged:

- “I never run exhaustive searches live unless explicitly asked.”
- “Bounded runs demonstrate correctness; exhaustive runs deliver completeness.”
- “No single signal is determinative in any scenario.”
- “If the data is weak, the system downgrades confidence — it never hallucinates strength.”
- “Disagreement doesn’t require re-execution; evidence is inspectable post-hoc.”

---

## Final Reminder

This document exists so you **never improvise** under pressure.

If it’s not written here:
- it doesn’t run
- it doesn’t get explained
- it doesn’t exist

That is intentional.

