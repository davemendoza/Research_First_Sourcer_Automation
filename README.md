# Research_First_Sourcer_Automation  
## Research-Operations-Grade AI Talent Intelligence Platform

**Author:** Dave Mendoza  
**Audience:** OpenAI Research Ops, Research Leadership, Engineering  
**Focus:** Evidence-based research hiring enablement under expert scrutiny

---

## Overview

This repository contains the Python automation layer of the **AI Talent Engine**, a research-operations-grade system designed to support AI research hiring where correctness matters more than convenience.

The system operates beyond traditional recruiting tools that rely on keyword frequency, titles, or inferred expertise. Instead, it evaluates **primary technical evidence** produced in research and engineering environments.

Signals analyzed include:

- Open-source code and repositories  
- Research publications and citations  
- Model artifacts and training configurations  
- Infrastructure and inference contributions  
- Conference participation and research networks  

The objective is **validity under skepticism**.

---

## Research Operations vs Recruiting Operations

Recruiting operations optimize for throughput.

Research operations optimize for **truth under review**.

This system is built with research-operations constraints: determinism, schema enforcement, explicit handling of uncertainty, and false-positive suppression. Outputs are not treated as conclusions, but as structured hypotheses grounded in inspectable evidence.

---

## Design Principles

- **Determinism:** identical inputs yield identical outputs  
- **Evidence-first reasoning:** no inferred signals without artifacts  
- **Uncertainty awareness:** absence of evidence is not over-interpreted  
- **Human judgment preserved:** the system supports, not replaces, expert decision-making  
- **Contestability:** all outputs are designed to be challenged and revised  

The goal is not prediction.  
The goal is reduction of epistemic uncertainty.

---

## System Architecture

The system operates as a dual-core architecture:

- A GPT multi-agent intelligence layer performs domain-specific signal extraction  
- A Python automation layer enforces validation, normalization, and schema alignment  

This repository contains the automation layer.

---

## Core Capabilities

- Deterministic enrichment of research and engineering profiles  
- Multi-source artifact analysis across GitHub, arXiv, Semantic Scholar, and model repositories  
- Schema-driven role classification across research, applied, and infrastructure domains  
- Explicit rejection of keyword-only scoring  
- Review-ready outputs traceable to underlying technical evidence  

---

## Why This Exists

Research organizations generate technical evidence continuously.

This system exists to translate that evidence into structured context that respects research epistemology while reducing evaluative burden on human reviewers.

---

## Author

Dave Mendoza

Designer and operator of research-operations-grade intelligence systems emphasizing evaluability, rigor, and technical truth over recruiting heuristics.
