# ROLE MENU — CANONICAL (HUMAN-FACING UX CONTRACT)

Maintainer: L. David Mendoza © 2026  
Status: LOCKED — DOCUMENTATION ONLY  
Authoritative Enforcement: EXECUTION_CORE/run_safe.py → _scenario_childproof()

---

## PURPOSE

This document defines the complete, approved set of AI role types that a human may invoke when running the AI Talent Engine.

It exists for:
• demos  
• interviews  
• daily operational reference  
• onboarding future maintainers  

This file is NOT read by code.  
The executable source of truth is the _scenario_childproof() function in run_safe.py.

---

## EXECUTION MODES (CHILD-PROOF)

Every role below must work with all three prefixes:

demo <role>  
scenario <role>  
run <role>  

Examples:

demo frontier ai scientist  
scenario rlhf engineer  
run ai infrastructure engineer  

Rules:
• No role outside this list may run  
• Unknown phrases must fail loudly  
• No internal identifiers are ever shown to the user  

---

## APPROVED ROLE LIST (27 TOTAL)

### CORE RESEARCH & FRONTIER

1. Frontier AI Scientist  
2. Foundational AI Scientist  
3. AI Research Scientist  
4. Machine Learning Researcher  

---

### MODELING, TRAINING & REINFORCEMENT LEARNING

5. Machine Learning Engineer  
6. Applied Machine Learning Engineer  
7. RLHF Engineer  
8. Reinforcement Learning Engineer  
9. Model Training Engineer  

---

### LLM, GENAI & APPLICATION

10. AI Engineer  
11. Generative AI Engineer  
12. LLM Engineer  
13. Prompt Engineer  

Prompt Engineer is valid only when downstream technical signals exist  
(e.g., Python, LangChain, RAG, RLHF).

---

### INFERENCE, PERFORMANCE & OPTIMIZATION

14. AI Performance Engineer  
15. Inference Engineer  
16. Model Optimization Engineer  

---

### INFRASTRUCTURE, SYSTEMS & PLATFORM

17. AI Infrastructure Engineer  
18. Machine Learning Infrastructure Engineer  
19. Distributed Systems Engineer  
20. Site Reliability Engineer for AI  
21. GPU Systems Engineer  

---

### DEPLOYMENT, CUSTOMER & FORWARD ROLES

22. AI Solutions Architect  
23. Forward Deployed Engineer  
24. AI Platform Engineer  

---

### ECOSYSTEM, EVALUATION & SAFETY

25. AI Safety Engineer  
26. Model Evaluation Engineer  
27. AI Alignment Engineer  

---

## IMPORTANT GUARANTEES

• This list is exhaustive  
• This list is closed  
• Adding a role requires a code change, not a doc edit  
• If a role is not listed here, the system must stop and say so  

---

## RELATIONSHIP TO CODE

Executable enforcement lives in:

EXECUTION_CORE/run_safe.py  
  └── _scenario_childproof()

This document exists to:
• explain behavior  
• document intent  
• support demos and interviews  
• prevent accidental scope creep  

---

## CHANGE POLICY

• Do NOT add roles casually  
• Do NOT treat this as a config file  
• Do NOT import or parse this file from code  
• Any change requires:
  – UX agreement  
  – code update  
  – re-lock of this document  

---

## FINAL NOTE

This role menu is intentionally human-centric.

It is designed so a non-technical user can say:

demo frontier  
run infra  
scenario rlhf  

…and the system behaves deterministically, safely, and transparently.

