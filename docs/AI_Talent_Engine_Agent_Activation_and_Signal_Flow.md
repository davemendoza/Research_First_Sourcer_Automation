# AI Talent Engine — Agent Activation & Signal Flow

This document explains how the AI Talent Engine activates agents, validates evidence, and produces research-grade talent intelligence.  
It is designed to be readable by both technical and non-technical stakeholders.

The system follows three hard rules:

- Evidence must be publicly verifiable
- No agent may invent or mutate evidence
- Governance has veto authority across all layers

---

## How to Read the Diagram

- Evidence flows **upward** from public artifacts
- Validation always precedes scoring
- Predictive intelligence is advisory, never authoritative
- Governance monitors, constrains, and can halt execution

---

## Agent Activation & Signal Flow Diagram

```mermaid
flowchart TB

subgraph L1["Layer 1 — Evidence Acquisition (First-Order)"]
A1["Public Artifacts<br/>Papers · Repos · Models · Patents · Talks"]
A2["Portfolio · Lab · Model · Community Agents<br/>(Agents 1–15, 38–49)"]
A1 --> A2
end

subgraph L2["Layer 2 — Systems & Domain Validation"]
B1["Alignment · Systems · Linguistic Validation<br/>(Agents 6–10, 43–45)"]
A2 --> B1
end

subgraph L3["Layer 3 — Network & Influence Modeling"]
C1["Collaboration · Influence Graphs<br/>(Agents 11–16, 32)"]
B1 --> C1
end

subgraph L4["Layer 4 — Impact & Velocity Analytics"]
D1["Baselines · Citation Velocity · Impact Scores · Influence Tiers<br/>(Agents 17–20)"]
C1 --> D1
end

subgraph L5["Layer 5 — Second-Order Fusion Intelligence"]
E1["Multi-Agent Fusion & Optimization<br/>(Agents 28–32)"]
D1 --> E1
end

subgraph L6["Layer 6 — Predictive Intelligence (Non-Authoritative)"]
F1["Trajectory & Forecasting Models<br/>(Agents 25–27, 33–35, 37)"]
E1 --> F1
end

subgraph GOV["Governance & Integrity Control Plane"]
G1["Schema Validation · Audit & Provenance · Responsible AI<br/>(Agents 21–24, 36, 46–47)"]
end

G1 -. monitors .-> A2
G1 -. validates .-> D1
G1 -. vetoes .-> E1
G1 -. constrains .-> F1

F1 --> OUT["Research-Grade Talent Intelligence Output<br/>Evidence-Backed · Auditable · Governed"]
