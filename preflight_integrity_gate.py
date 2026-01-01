#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI Talent Engine | Research-First Sourcer Automation
Preflight Integrity Gate (Execution-Blocking)

Version: v1.0.0
Author: L. David Mendoza
Copyright: © 2025 L. David Mendoza. All rights reserved.

Purpose
- Enforce absolute demo and production integrity before any pipeline run.
- Block execution on any placeholder data risk, schema contract violation,
  demo misconfiguration, synthetic identity sources, or network prerequisite mismatch.

Non-negotiable contract requirements (summary)
- ZERO fabricated people
- ZERO placeholders of any kind
- Truthful sparsity is mandatory (blank beats fake)
- Demo equals real pipeline rules, bounded scope only
- Contact fields: public-only, explicitly published, never inferred
- Enforcement must be mandatory (preflight + postrun QA)

This file is designed to be called by your canonical CLI entry point.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable, List, Optional, Sequence, Tuple, Dict, Any
import re
import sys
import time
import json


# -----------------------------
# Versioning and changelog
# -----------------------------
__version__ = "v1.0.0"

CHANGELOG = [
    {
        "version": "v1.0.0",
        "date": "2025-12-31",
        "changes": [
            "Initial execution-blocking preflight integrity gate with placeholder detection, schema order enforcement, demo caps enforcement, synthetic source blocking, and network prerequisite checks."
        ],
    }
]


# -----------------------------
# Hard schema contract
# -----------------------------
REQUIRED_PREFIX_COLUMNS: List[str] = [
    "Person_ID",
    "Full_Name",
    "Role_Type",
    "Email",
    "Phone",
    "LinkedIn_URL",
    "GitHub_URL",
    "GitHub_IO_URL",
    "Google_Scholar_URL",
    "Resume_or_CV_URL",
]


# -----------------------------
# Placeholder and fake-value detection
# -----------------------------
DEFAULT_FORBIDDEN_SUBSTRINGS: List[str] = [
    "example.com",
    "github.com/example",
    "email@example.com",
    "name@example",
    "555-555-5555",
    "cv available upon request",
    "resume available upon request",
    "lorem",
    "tbd",
]

DEFAULT_FORBIDDEN_REGEX: List[str] = [
    r"\b555[\s\-\.]555[\s\-\.]5555\b",
    r"\b(?:test|fake|dummy)\b",
    r"\bexample\b",
    r"\b(?:john|jane)\s+doe\b",
]

_DEFAULT_URL_REGEX = re.compile(r"https?://[^\s]+")


@dataclass(frozen=True)
class PreflightContext:
    """
    This context must be constructed by the canonical CLI after parsing arguments
    and after CLI parity has been validated, but before any pipeline execution begins.
    """
    mode: str  # "demo" or "real"
    scenario: str
    output_path: Path

    planned_columns: List[str]

    planned_min_rows: Optional[int] = None
    planned_target_rows: Optional[int] = None
    planned_max_rows: Optional[int] = None

    data_sources: List[str] = field(default_factory=list)

    allow_network: bool = True
    requires_network: bool = True

    # Optional seeds or configured URLs that must resolve (domains only checked here).
    configured_seed_urls: List[str] = field(default_factory=list)

    # Optional: If your system keeps a list of source IDs known to be synthetic.
    synthetic_source_ids: List[str] = field(default_factory=lambda: [
        "mock",
        "mocks",
        "mock_people",
        "mock_people_generator",
        "synthetic",
        "faker",
        "fake",
        "dummy",
        "test_fixtures",
        "fixtures",
        "generated_people",
    ])


class PreflightFailure(RuntimeError):
    pass


def _now_utc_iso() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def _normalize(s: str) -> str:
    return (s or "").strip().lower()


def _extract_domains(urls: Sequence[str]) -> List[str]:
    domains: List[str] = []
    for u in urls:
        uu = (u or "").strip()
        if not uu:
            continue
        m = re.match(r"^https?://([^/]+)", uu, flags=re.IGNORECASE)
        if m:
            domains.append(m.group(1).lower())
    return sorted(set(domains))


def _looks_like_placeholder(value: str, forbidden_substrings: Sequence[str], forbidden_regex: Sequence[str]) -> Optional[str]:
    v = (value or "").strip()
    if not v:
        return None

    lv = v.lower()

    for sub in forbidden_substrings:
        if sub and sub.lower() in lv:
            return f"forbidden substring '{sub}'"

    for rx in forbidden_regex:
        try:
            if re.search(rx, v, flags=re.IGNORECASE):
                return f"forbidden regex '{rx}'"
        except re.error:
            # If regex is invalid, treat as configuration failure
            return f"invalid forbidden regex configuration '{rx}'"

    return None


def _validate_column_prefix(planned_columns: Sequence[str]) -> Optional[str]:
    cols = list(planned_columns or [])
    if len(cols) < len(REQUIRED_PREFIX_COLUMNS):
        return f"planned_columns has only {len(cols)} columns, requires at least {len(REQUIRED_PREFIX_COLUMNS)}"

    prefix = cols[: len(REQUIRED_PREFIX_COLUMNS)]
    if prefix != REQUIRED_PREFIX_COLUMNS:
        diffs = []
        for i, (exp, got) in enumerate(zip(REQUIRED_PREFIX_COLUMNS, prefix), start=1):
            if exp != got:
                diffs.append(f"col {i}: expected '{exp}' got '{got}'")
        return "column order violation: " + "; ".join(diffs)

    return None


def _validate_mode_and_demo_caps(ctx: PreflightContext) -> List[str]:
    failures: List[str] = []

    mode = _normalize(ctx.mode)
    if mode not in {"demo", "real"}:
        failures.append(f"invalid mode '{ctx.mode}' (must be 'demo' or 'real')")
        return failures

    if mode == "demo":
        # Hard demo caps
        min_rows = ctx.planned_min_rows
        max_rows = ctx.planned_max_rows
        target_rows = ctx.planned_target_rows

        if min_rows is None:
            failures.append("demo requires planned_min_rows to be set (must be >= 25)")
        elif min_rows < 25:
            failures.append(f"demo planned_min_rows is {min_rows}, must be >= 25")

        if max_rows is None:
            failures.append("demo requires planned_max_rows to be set (must be <= 50)")
        elif max_rows > 50:
            failures.append(f"demo planned_max_rows is {max_rows}, must be <= 50")

        if target_rows is not None and (target_rows < 25 or target_rows > 50):
            failures.append(f"demo planned_target_rows is {target_rows}, must be within 25..50")

    return failures


def _validate_no_synthetic_sources(ctx: PreflightContext) -> List[str]:
    failures: List[str] = []
    source_ids = [_normalize(s) for s in (ctx.data_sources or []) if (s or "").strip()]
    synthetic_ids = set(_normalize(s) for s in (ctx.synthetic_source_ids or []) if (s or "").strip())

    for sid in source_ids:
        for bad in synthetic_ids:
            if bad and (sid == bad or bad in sid):
                failures.append(f"synthetic identity source detected: '{sid}' matched blocked token '{bad}'")
                break

    return failures


def _validate_network_prereqs(ctx: PreflightContext) -> List[str]:
    failures: List[str] = []
    if ctx.requires_network and not ctx.allow_network:
        failures.append("network access required but allow_network is false")
    return failures


def _validate_configured_seeds(ctx: PreflightContext, forbidden_substrings: Sequence[str], forbidden_regex: Sequence[str]) -> List[str]:
    """
    Preflight can only validate configured seed URLs and domains.
    Full URL resolution is handled by the postrun QA gate once URLs exist.
    """
    failures: List[str] = []
    for u in (ctx.configured_seed_urls or []):
        u = (u or "").strip()
        if not u:
            continue

        why = _looks_like_placeholder(u, forbidden_substrings, forbidden_regex)
        if why:
            failures.append(f"configured_seed_url placeholder detected: '{u}' ({why})")

        if not _DEFAULT_URL_REGEX.match(u):
            failures.append(f"configured_seed_url is not a valid URL: '{u}'")

    return failures


def run_preflight_integrity_gate(
    ctx: PreflightContext,
    *,
    forbidden_substrings: Optional[Sequence[str]] = None,
    forbidden_regex: Optional[Sequence[str]] = None,
    log_path: Optional[Path] = None,
) -> None:
    """
    Execute all preflight checks. On any failure, raise PreflightFailure.

    Integration contract:
    - Caller must treat any PreflightFailure as execution-blocking and exit non-zero.
    - Caller must not write output files prior to a passing gate.
    """
    forbidden_substrings = list(forbidden_substrings or DEFAULT_FORBIDDEN_SUBSTRINGS)
    forbidden_regex = list(forbidden_regex or DEFAULT_FORBIDDEN_REGEX)

    failures: List[str] = []

    # 1) Schema prefix contract
    col_err = _validate_column_prefix(ctx.planned_columns)
    if col_err:
        failures.append(col_err)

    # 2) Mode and demo caps
    failures.extend(_validate_mode_and_demo_caps(ctx))

    # 3) Synthetic sources
    failures.extend(_validate_no_synthetic_sources(ctx))

    # 4) Network prerequisites
    failures.extend(_validate_network_prereqs(ctx))

    # 5) Configured seed validation (placeholders, format)
    failures.extend(_validate_configured_seeds(ctx, forbidden_substrings, forbidden_regex))

    # 6) Output path sanity
    try:
        outp = Path(ctx.output_path)
        if not outp.name:
            failures.append("output_path has no filename")
    except Exception as e:
        failures.append(f"invalid output_path: {e}")

    # 7) Scenario sanity
    if not (ctx.scenario or "").strip():
        failures.append("scenario is empty")

    # Logging
    record: Dict[str, Any] = {
        "timestamp_utc": _now_utc_iso(),
        "module": "preflight_integrity_gate",
        "version": __version__,
        "mode": ctx.mode,
        "scenario": ctx.scenario,
        "output_path": str(ctx.output_path),
        "planned_columns_prefix": list(ctx.planned_columns[: len(REQUIRED_PREFIX_COLUMNS)]),
        "planned_min_rows": ctx.planned_min_rows,
        "planned_target_rows": ctx.planned_target_rows,
        "planned_max_rows": ctx.planned_max_rows,
        "data_sources": list(ctx.data_sources),
        "allow_network": bool(ctx.allow_network),
        "requires_network": bool(ctx.requires_network),
        "configured_seed_domains": _extract_domains(ctx.configured_seed_urls),
        "status": "PASS" if not failures else "FAIL",
        "failures": failures,
    }

    if log_path is None:
        log_path = Path.cwd() / "logs" / "preflight_gate.jsonl"

    try:
        log_path.parent.mkdir(parents=True, exist_ok=True)
        with log_path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")
    except Exception:
        # Logging failure must never cause a false PASS, but also should not mask a hard FAIL.
        pass

    if failures:
        msg_lines = []
        msg_lines.append("❌ PREFLIGHT FAILURE — INTEGRITY GATE BLOCKED EXECUTION")
        msg_lines.append(f"Mode: {ctx.mode}")
        msg_lines.append(f"Scenario: {ctx.scenario}")
        msg_lines.append("Failures:")
        for i, r in enumerate(failures, start=1):
            msg_lines.append(f"  {i}. {r}")
        msg_lines.append("")
        msg_lines.append("No output was generated. Fix the failures above, then rerun.")
        raise PreflightFailure("\n".join(msg_lines))

    print("✅ Preflight integrity gate passed. Proceeding with pipeline execution.")


def _selftest() -> int:
    """
    Minimal local selftest.
    Not a demo. Not a pipeline run.
    """
    ctx = PreflightContext(
        mode="demo",
        scenario="frontier",
        output_path=Path("outputs/demo_frontier.csv"),
        planned_columns=list(REQUIRED_PREFIX_COLUMNS) + ["Extra_Column_1"],
        planned_min_rows=25,
        planned_target_rows=50,
        planned_max_rows=50,
        data_sources=["public_github", "public_scholar"],
        allow_network=True,
        requires_network=True,
        configured_seed_urls=[],
    )

    try:
        run_preflight_integrity_gate(ctx)
        return 0
    except PreflightFailure as e:
        print(str(e), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(_selftest())


"""
VALIDATION STEPS (must be run after adding this file)
1) From repo root:
   python3 preflight_integrity_gate.py
   Expected: ✅ Preflight integrity gate passed.

2) Confirm log created:
   ls -la logs/preflight_gate.jsonl

GIT COMMANDS
git status
git add preflight_integrity_gate.py logs/.gitkeep 2>/dev/null || true
git commit -m "Add execution-blocking preflight integrity gate (no placeholders, schema order, demo caps)"
git push

Notes
- This module intentionally does NOT attempt full URL resolution. That belongs in the postrun QA gate after URLs exist.
- This module blocks execution on any configuration that risks fake completeness.
"""
