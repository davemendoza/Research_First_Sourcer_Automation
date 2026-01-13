#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$REPO_ROOT"

echo "Repo Root: $REPO_ROOT"

# ------------------------------------------------------------------------------
# Backup (best practice): snapshot any existing phase_next folder
# ------------------------------------------------------------------------------
TS="$(date +"%Y%m%d_%H%M%S")"
BK_DIR="$REPO_ROOT/.autogen_backups/phase_next_cde_${TS}"
mkdir -p "$BK_DIR"

if [ -d "$REPO_ROOT/core/phase_next" ]; then
  mkdir -p "$BK_DIR/core"
  cp -R "$REPO_ROOT/core/phase_next" "$BK_DIR/core/phase_next"
  echo "Backed up: core/phase_next -> $BK_DIR/core/phase_next"
fi

# ------------------------------------------------------------------------------
# Ensure folders
# ------------------------------------------------------------------------------
mkdir -p core/phase_next

# ------------------------------------------------------------------------------
# core/phase_next/control_plane.py
# - Centralized flags; defaults are SAFE and READ-ONLY
# ------------------------------------------------------------------------------
cat <<'PY' > core/phase_next/control_plane.py
"""
Phase-Next Control Plane (READ-ONLY default)

This module intentionally defaults to READ-ONLY operation.
No Excel writes and no GPT writeback are performed unless explicitly enabled.

Flags can be overridden via environment variables:
  PHASE_NEXT_READ_ONLY=1|0
  PHASE_NEXT_EXCEL_WRITE_ENABLED=1|0
  PHASE_NEXT_WATCHLIST_RULES_ENABLED=1|0
  PHASE_NEXT_GPT_WRITEBACK_ENABLED=1|0
  PHASE_NEXT_ADAPTIVE_CADENCE_ENABLED=1|0
"""

from __future__ import annotations

import os
from dataclasses import dataclass


def _env_bool(name: str, default: bool) -> bool:
    v = os.getenv(name)
    if v is None:
        return default
    v = v.strip().lower()
    if v in {"1", "true", "yes", "y", "on"}:
        return True
    if v in {"0", "false", "no", "n", "off"}:
        return False
    return default


@dataclass(frozen=True)
class ControlFlags:
    read_only: bool
    excel_write_enabled: bool
    watchlist_rules_enabled: bool
    gpt_writeback_enabled: bool
    adaptive_cadence_enabled: bool


def status() -> ControlFlags:
    # Safe defaults:
    # - read_only True
    # - excel_write_enabled False
    # - watchlist_rules_enabled True (evaluation only; no writes)
    # - gpt_writeback_enabled False (payload generation only)
    # - adaptive_cadence_enabled True (planning only; no writes)
    flags = ControlFlags(
        read_only=_env_bool("PHASE_NEXT_READ_ONLY", True),
        excel_write_enabled=_env_bool("PHASE_NEXT_EXCEL_WRITE_ENABLED", False),
        watchlist_rules_enabled=_env_bool("PHASE_NEXT_WATCHLIST_RULES_ENABLED", True),
        gpt_writeback_enabled=_env_bool("PHASE_NEXT_GPT_WRITEBACK_ENABLED", False),
        adaptive_cadence_enabled=_env_bool("PHASE_NEXT_ADAPTIVE_CADENCE_ENABLED", True),
    )

    # Guardrails: if read_only, force-disable writes
    if flags.read_only:
        return ControlFlags(
            read_only=True,
            excel_write_enabled=False,
            watchlist_rules_enabled=flags.watchlist_rules_enabled,
            gpt_writeback_enabled=flags.gpt_writeback_enabled,
            adaptive_cadence_enabled=flags.adaptive_cadence_enabled,
        )

    return flags


# Convenience booleans (common import pattern)
FLAGS = status()
READ_ONLY = FLAGS.read_only
EXCEL_WRITE_ENABLED = FLAGS.excel_write_enabled
WATCHLIST_RULES_ENABLED = FLAGS.watchlist_rules_enabled
GPT_WRITEBACK_ENABLED = FLAGS.gpt_writeback_enabled
ADAPTIVE_CADENCE_ENABLED = FLAGS.adaptive_cadence_enabled
PY

# ------------------------------------------------------------------------------
# core/phase_next/analysis_envelope.py
# - Standard container for Phase-Next intelligence output (READ-ONLY)
# ------------------------------------------------------------------------------
cat <<'PY' > core/phase_next/analysis_envelope.py
"""
Analysis Envelope

A stable, import-safe container for Phase-Next output artifacts.
This does NOT call any network services and does NOT write to Excel.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class SeedHubMetadata:
    watchlist_flag: Optional[str] = None
    monitoring_tier: Optional[str] = None
    domain_type: Optional[str] = None
    source_category: Optional[str] = None
    language_code: Optional[str] = None


@dataclass
class CadencePlan:
    tier: str
    period_days: int
    rationale: str


@dataclass
class WatchlistDecision:
    decision: str
    reason: str
    signals: List[str] = field(default_factory=list)


@dataclass
class IntelligenceEnvelope:
    # Identity / provenance
    seed_hub_row_id: Optional[str] = None
    seed_hub_type: Optional[str] = None
    seed_hub_value: Optional[str] = None
    metadata: SeedHubMetadata = field(default_factory=SeedHubMetadata)

    # C/D outputs
    cadence_plan: Optional[CadencePlan] = None
    watchlist: Optional[WatchlistDecision] = None

    # E outputs (read-only scaffolds)
    strengths: List[str] = field(default_factory=list)
    weaknesses: List[str] = field(default_factory=list)
    notes: List[str] = field(default_factory=list)
    confidence: str = "Unknown"

    # GPT writeback payload (generated only; never posted)
    gpt_payload: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "seed_hub_row_id": self.seed_hub_row_id,
            "seed_hub_type": self.seed_hub_type,
            "seed_hub_value": self.seed_hub_value,
            "metadata": {
                "watchlist_flag": self.metadata.watchlist_flag,
                "monitoring_tier": self.metadata.monitoring_tier,
                "domain_type": self.metadata.domain_type,
                "source_category": self.metadata.source_category,
                "language_code": self.metadata.language_code,
            },
            "cadence_plan": None if not self.cadence_plan else {
                "tier": self.cadence_plan.tier,
                "period_days": self.cadence_plan.period_days,
                "rationale": self.cadence_plan.rationale,
            },
            "watchlist": None if not self.watchlist else {
                "decision": self.watchlist.decision,
                "reason": self.watchlist.reason,
                "signals": list(self.watchlist.signals),
            },
            "strengths": list(self.strengths),
            "weaknesses": list(self.weaknesses),
            "notes": list(self.notes),
            "confidence": self.confidence,
            "gpt_payload": self.gpt_payload,
        }
PY

# ------------------------------------------------------------------------------
# core/phase_next/adaptive_cadence.py
# - Cadence planning (READ-ONLY)
# ------------------------------------------------------------------------------
cat <<'PY' > core/phase_next/adaptive_cadence.py
"""
Adaptive Cadence (READ-ONLY)

Maps Monitoring_Tier values to sampling cadence plans.
No scheduling side effects; this only returns a plan object.
"""

from __future__ import annotations

from dataclasses import dataclass

from .analysis_envelope import CadencePlan


def _normalize_tier(tier: str | None) -> str:
    if not tier:
        return "T3"
    t = str(tier).strip().upper()
    if t in {"T0", "T1", "T2", "T3", "T4"}:
        return t
    # Common variants
    if t in {"HIGH", "HOT", "URGENT"}:
        return "T1"
    if t in {"MED", "MEDIUM"}:
        return "T2"
    if t in {"LOW", "COLD"}:
        return "T3"
    return "T3"


def plan_from_tier(tier: str | None) -> CadencePlan:
    t = _normalize_tier(tier)

    # Conservative defaults in days (can be tuned later)
    if t == "T0":
        return CadencePlan(tier=t, period_days=7, rationale="T0: highest urgency monitoring tier.")
    if t == "T1":
        return CadencePlan(tier=t, period_days=30, rationale="T1: active targets, monthly sampling.")
    if t == "T2":
        return CadencePlan(tier=t, period_days=60, rationale="T2: warm targets, bi-monthly sampling.")
    if t == "T3":
        return CadencePlan(tier=t, period_days=90, rationale="T3: baseline targets, quarterly sampling.")
    return CadencePlan(tier=t, period_days=180, rationale="T4: low priority, semiannual sampling.")
PY

# ------------------------------------------------------------------------------
# core/phase_next/watchlist_rules.py
# - Watchlist evaluation (READ-ONLY; no writes)
# ------------------------------------------------------------------------------
cat <<'PY' > core/phase_next/watchlist_rules.py
"""
Watchlist Promotion Rules (READ-ONLY)

This module evaluates whether a row should be escalated/promoted to a watchlist.
It NEVER writes to Excel; it only returns a decision object.

Signals are placeholders for now (no biasing population of Seed Hub columns).
Later phases can replace these with real evidence from open sources.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from .analysis_envelope import WatchlistDecision
from .control_plane import WATCHLIST_RULES_ENABLED


def _truthy(v: Any) -> bool:
    if v is None:
        return False
    s = str(v).strip().lower()
    return s in {"1", "true", "yes", "y", "on"}


def evaluate_watchlist(row: Dict[str, Any]) -> WatchlistDecision:
    """
    READ-ONLY evaluator.
    Returns WatchlistDecision regardless of enabled state, but if disabled,
    returns "NOOP" to keep the pipeline stable.
    """
    if not WATCHLIST_RULES_ENABLED:
        return WatchlistDecision(decision="NOOP", reason="Watchlist rules disabled.", signals=[])

    signals: List[str] = []

    # These are intentionally generic and non-invasive.
    # Later, real evidence signals (citations velocity, repo burst, conference movement) can be wired in.
    if _truthy(row.get("Watchlist_Flag")):
        signals.append("seed_hub_watchlist_flag_true")

    # Example: treat Tier T0/T1 as an escalation factor (planning only)
    tier = (row.get("Monitoring_Tier") or "").strip().upper()
    if tier in {"T0", "T1"}:
        signals.append(f"monitoring_tier_{tier.lower()}")

    # Domain/type provenance signals (planning only)
    domain_type = (row.get("Domain_Type") or "").strip()
    if domain_type:
        signals.append("domain_type_present")

    source_category = (row.get("Source_Category") or "").strip()
    if source_category:
        signals.append("source_category_present")

    # Decision logic (simple, deterministic)
    if len(signals) >= 3:
        return WatchlistDecision(
            decision="PROMOTE",
            reason="3 escalation signals detected",
            signals=signals,
        )

    if len(signals) == 2:
        return WatchlistDecision(
            decision="HOLD",
            reason="2 escalation signals detected",
            signals=signals,
        )

    return WatchlistDecision(
        decision="IGNORE",
        reason="Insufficient escalation signals",
        signals=signals,
    )


# Compatibility alias (future-proof)
evaluate_watchlist_candidate = evaluate_watchlist
PY

# ------------------------------------------------------------------------------
# core/phase_next/intelligence_formatter.py
# - Builds a READ-ONLY intelligence envelope + optional GPT payload
# ------------------------------------------------------------------------------
cat <<'PY' > core/phase_next/intelligence_formatter.py
"""
Intelligence Formatter (READ-ONLY)

Builds a deterministic IntelligenceEnvelope from:
- Seed hub row fields
- Cadence plan (Phase C)
- Watchlist decision (Phase D)
- GPT writeback payload generation scaffold (Phase E)

No GPT calls. No Excel writes.
"""

from __future__ import annotations

from typing import Any, Dict, Optional

from .analysis_envelope import IntelligenceEnvelope, SeedHubMetadata
from .adaptive_cadence import plan_from_tier
from .watchlist_rules import evaluate_watchlist
from .gpt_writeback import prepare_gpt_writeback_payload


def _safe_str(v: Any) -> Optional[str]:
    if v is None:
        return None
    s = str(v).strip()
    return s if s else None


def build_envelope(row: Dict[str, Any]) -> IntelligenceEnvelope:
    meta = SeedHubMetadata(
        watchlist_flag=_safe_str(row.get("Watchlist_Flag")),
        monitoring_tier=_safe_str(row.get("Monitoring_Tier")),
        domain_type=_safe_str(row.get("Domain_Type")),
        source_category=_safe_str(row.get("Source_Category")),
        language_code=_safe_str(row.get("Language_Code")),
    )

    env = IntelligenceEnvelope(
        seed_hub_row_id=_safe_str(row.get("Seed_Hub_Row_ID") or row.get("Row_ID") or row.get("Person ID")),
        seed_hub_type=_safe_str(row.get("Seed_Hub_Type")),
        seed_hub_value=_safe_str(row.get("Seed_Hub_Value") or row.get("Value") or row.get("URL")),
        metadata=meta,
    )

    env.cadence_plan = plan_from_tier(meta.monitoring_tier)
    env.watchlist = evaluate_watchlist(row)

    # Phase E scaffolds: deterministic, conservative
    env.strengths = [
        "Read-only scaffolds active: cadence planning and watchlist evaluation are operational.",
        "Seed Hub metadata fields are wired as targets (not populated) for future monitoring.",
    ]

    env.weaknesses = [
        "No live evidence ingestion in this phase (by design).",
        "No GPT writeback enabled; payload generation only.",
    ]

    env.notes = [
        "This run is read-only. No writes performed.",
        "To enable writes later, set PHASE_NEXT_READ_ONLY=0 and PHASE_NEXT_EXCEL_WRITE_ENABLED=1 explicitly.",
        "GPT writeback remains disabled unless PHASE_NEXT_GPT_WRITEBACK_ENABLED=1 is explicitly set.",
    ]

    env.confidence = "Medium"

    # Generate payload (but do not send anywhere)
    env.gpt_payload = prepare_gpt_writeback_payload(env)

    return env
PY

# ------------------------------------------------------------------------------
# core/phase_next/gpt_writeback.py
# - Generates a payload ONLY when enabled; safe to import always
# ------------------------------------------------------------------------------
cat <<'PY' > core/phase_next/gpt_writeback.py
"""
GPT Writeback Scaffold (READ-ONLY)

This module generates a structured payload intended for a future GPT writeback step.
It does NOT call any GPT APIs and does NOT write to Excel.

If GPT_WRITEBACK_ENABLED is False, prepare_gpt_writeback_payload returns None.
"""

from __future__ import annotations

from typing import Any, Dict, Optional

from .control_plane import GPT_WRITEBACK_ENABLED
from .analysis_envelope import IntelligenceEnvelope


def prepare_gpt_writeback_payload(env: IntelligenceEnvelope) -> Optional[Dict[str, Any]]:
    if not GPT_WRITEBACK_ENABLED:
        return None

    # This is a deterministic, schema-aligned envelope for a future GPT step.
    return {
        "row_identity": {
            "seed_hub_row_id": env.seed_hub_row_id,
            "seed_hub_type": env.seed_hub_type,
            "seed_hub_value": env.seed_hub_value,
        },
        "metadata": {
            "watchlist_flag": env.metadata.watchlist_flag,
            "monitoring_tier": env.metadata.monitoring_tier,
            "domain_type": env.metadata.domain_type,
            "source_category": env.metadata.source_category,
            "language_code": env.metadata.language_code,
        },
        "phase_next": {
            "cadence_plan": None if not env.cadence_plan else {
                "tier": env.cadence_plan.tier,
                "period_days": env.cadence_plan.period_days,
                "rationale": env.cadence_plan.rationale,
            },
            "watchlist": None if not env.watchlist else {
                "decision": env.watchlist.decision,
                "reason": env.watchlist.reason,
                "signals": env.watchlist.signals,
            },
        },
        "narrative_scaffolds": {
            "strengths": env.strengths,
            "weaknesses": env.weaknesses,
            "notes": env.notes,
            "confidence": env.confidence,
        },
        "writeback_targets": {
            # Wired targets only; do not populate during read-only.
            "Watchlist_Flag": "target_only",
            "Monitoring_Tier": "target_only",
            "Domain_Type": "target_only",
            "Source_Category": "target_only",
            "Language_Code": "target_only",
        },
    }


def writeback(env: IntelligenceEnvelope) -> Optional[Dict[str, Any]]:
    # Alias for integration convenience
    return prepare_gpt_writeback_payload(env)
PY

# ------------------------------------------------------------------------------
# core/phase_next/phase_next_activation.py
# - Consolidated C/D/E read-only runner that reads the Seed Hub and prints outputs
# ------------------------------------------------------------------------------
cat <<'PY' > core/phase_next/phase_next_activation.py
"""
Phase-Next Activation (C/D/E) - READ-ONLY

Reads Seed Hub rows, generates:
- Cadence plan (Phase C)
- Watchlist decision (Phase D)
- GPT writeback payload scaffold (Phase E; payload only, no calls)

No writes performed.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

from openpyxl import load_workbook

from .control_plane import status
from .intelligence_formatter import build_envelope


SEED_HUB_PATH = Path("data/AI_Talent_Landscape_Seed_Hubs.xlsx")


def _load_seed_hub_rows(max_rows: int = 250) -> List[Dict[str, Any]]:
    if not SEED_HUB_PATH.exists():
        raise FileNotFoundError(f"Seed Hub not found at: {SEED_HUB_PATH}")

    wb = load_workbook(SEED_HUB_PATH, data_only=True)
    ws = wb.active

    headers = []
    for c in ws[1]:
        headers.append(str(c.value).strip() if c.value is not None else "")

    rows: List[Dict[str, Any]] = []
    for i, r in enumerate(ws.iter_rows(min_row=2, values_only=True), start=2):
        if len(rows) >= max_rows:
            break
        row = {}
        for h, v in zip(headers, r):
            if h:
                row[h] = v
        rows.append(row)

    return rows


def main() -> Dict[str, Any]:
    flags = status()

    print("Phase-Next running in READ-ONLY cadence mode")
    print(f"Watchlist enabled: {flags.watchlist_rules_enabled}")
    print(f"GPT writeback enabled: {flags.gpt_writeback_enabled}")
    print(f"Excel writes enabled: {flags.excel_write_enabled}")

    rows = _load_seed_hub_rows(max_rows=250)
    if not rows:
        print("No rows found in Seed Hub.")
        return {"read_only": flags.read_only, "rows_loaded": 0, "writes_performed": False}

    # Build a handful of envelopes as a sanity check
    sample_count = 5 if len(rows) >= 5 else len(rows)
    samples = rows[:sample_count]

    envelopes = [build_envelope(r).to_dict() for r in samples]

    result = {
        "read_only": flags.read_only,
        "excel_write_enabled": flags.excel_write_enabled,
        "watchlist_rules_enabled": flags.watchlist_rules_enabled,
        "gpt_writeback_enabled": flags.gpt_writeback_enabled,
        "seed_hub_path": str(SEED_HUB_PATH),
        "max_rows_total": len(rows),
        "samples_generated": sample_count,
        "writes_performed": False,
        "sample_envelopes": envelopes,
        "notes": "Phase-Next executed in read-only mode. No writes performed.",
    }

    print(json.dumps(result, indent=2))
    print(f"Rows loaded: {len(rows)}")
    print(f"Samples generated: {sample_count}")
    print("Writes performed: False")
    print("Notes: Phase-Next executed in read-only mode. No writes performed.")

    return result


if __name__ == "__main__":
    main()
PY

# ------------------------------------------------------------------------------
# core/phase_next/__init__.py
# - Import-safe exports (avoid accidental import errors)
# ------------------------------------------------------------------------------
cat <<'PY' > core/phase_next/__init__.py
"""
core.phase_next package

Import-safe by design. This package is used in read-only mode by default.
"""

from .control_plane import (
    status,
    FLAGS,
    READ_ONLY,
    EXCEL_WRITE_ENABLED,
    WATCHLIST_RULES_ENABLED,
    GPT_WRITEBACK_ENABLED,
    ADAPTIVE_CADENCE_ENABLED,
)

from .adaptive_cadence import plan_from_tier
from .watchlist_rules import evaluate_watchlist, evaluate_watchlist_candidate
from .gpt_writeback import prepare_gpt_writeback_payload, writeback
PY

# ------------------------------------------------------------------------------
# Runner script: phase_next_run.sh
# ------------------------------------------------------------------------------
cat <<'BASH2' > phase_next_run.sh
#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$REPO_ROOT"

echo "Repo Root: $REPO_ROOT"
echo "Using python3:"
command -v python3 >/dev/null 2>&1 || { echo "ERROR: python3 not found"; exit 1; }
python3 --version

echo ""
echo "Running Phase-Next activation (C/D/E) READ-ONLY, no writes"
python3 -c "from core.phase_next.phase_next_activation import main; main()"
BASH2

chmod +x phase_next_run.sh
chmod +x phase_next_cde_gpt_autogen.sh

# ------------------------------------------------------------------------------
# Validation (compile only; no execution side effects)
# ------------------------------------------------------------------------------
python3 -m py_compile \
  core/phase_next/control_plane.py \
  core/phase_next/analysis_envelope.py \
  core/phase_next/adaptive_cadence.py \
  core/phase_next/watchlist_rules.py \
  core/phase_next/intelligence_formatter.py \
  core/phase_next/gpt_writeback.py \
  core/phase_next/phase_next_activation.py \
  core/phase_next/__init__.py

echo ""
echo "AUTOGEN COMPLETE"
echo ""
echo "NEXT:"
echo "  ./phase_next_run.sh"
echo ""
echo "Then (SSH assumed):"
echo "  git status"
echo "  git add core/phase_next phase_next_cde_gpt_autogen.sh phase_next_run.sh"
echo "  git commit -m \"Phase-Next: add read-only GPT writeback scaffolds (C/D/E)\""
echo "  git push"
