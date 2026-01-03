# Interview Demo Script — Read-Aloud Version
Version: Day4-v1.0
Author: L. David Mendoza
© 2025 L. David Mendoza. All Rights Reserved.

---

## Opening (Always Say This First)

“Before I run anything, I’ll explain what question this scenario answers and why this execution envelope is appropriate.”

---

## Scenario Declaration (Exact Wording)

“I’m running the scenario:

demo: <SCENARIO NAME>

The demo envelope is intentionally bounded for clarity and speed.
The exhaustive version uses the same logic and runs asynchronously for completeness.”

---

## Intent Statement (Mandatory)

“This scenario exists to answer **<PRIMARY QUESTION>**.
It intentionally does **not** attempt to answer **<EXCLUDED QUESTION>**.”

---

## Boundary Condition (Anti-Stump)

“If we tried to use this scenario to evaluate **<WRONG USE CASE>**, the results would be misleading — and that’s by design.”

---

## Execution Envelope Explanation

“The only difference between demo and exhaustive runs is variable bounds, not logic.”

Defaults I’m using:
- Top N: <VALUE>
- Tier scope: <VALUE>
- Repo family: <VALUE>

---

## Governance Statement (Power Move)

“Nothing in this system runs unless it’s explicitly allowed, declared, and auditable.
This scenario is allow-listed, safety-gated, and explainable post-hoc.”

---

## Execution (Only After All Above)

```bash
./run_safe.py "<SCENARIO NAME>"

