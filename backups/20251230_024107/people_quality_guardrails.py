#!/usr/bin/env python3
"""
AI Talent Engine – People Quality Guardrails
Version: v1.0.0-ultra
Date: 2025-12-30
© 2025 L. David Mendoza. All Rights Reserved.

MANDATE
This project is maximalist by default.
No "optional hardening". No silent successes. No empty runs.

This module enforces:
- Per-scenario minimum yield
- Global minimum yield
- Evidence URL requirements
- Fail-fast behavior on unacceptable outputs
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional

@dataclass
class GuardrailConfig:
    min_people_per_scenario: int = 120
    min_people_total: int = 600
    require_evidence_urls: bool = True

class GuardrailViolation(RuntimeError):
    pass

def validate_scenario_yields(yields: Dict[str, int], cfg: GuardrailConfig) -> None:
    bad = {k: v for k, v in yields.items() if v < cfg.min_people_per_scenario}
    if bad:
        msg = "Guardrail violation: scenarios below minimum yield:\n"
        for k, v in sorted(bad.items(), key=lambda x: x[0]):
            msg += f"  - {k}: {v} (min {cfg.min_people_per_scenario})\n"
        raise GuardrailViolation(msg)

def validate_total_people(total: int, cfg: GuardrailConfig) -> None:
    if total < cfg.min_people_total:
        raise GuardrailViolation(
            f"Guardrail violation: total people {total} is below minimum {cfg.min_people_total}"
        )

def validate_evidence_urls(people_rows: List[dict], cfg: GuardrailConfig) -> None:
    if not cfg.require_evidence_urls:
        return
    missing = 0
    for r in people_rows:
        urls = str(r.get("evidence_urls", "") or "").strip()
        if not urls:
            missing += 1
    if missing:
        raise GuardrailViolation(
            f"Guardrail violation: {missing} people rows missing evidence_urls"
        )
