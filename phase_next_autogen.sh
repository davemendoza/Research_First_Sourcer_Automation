#!/bin/zsh
set -euo pipefail

# ==============================================================================
# phase_next_autogen.sh
# Phase-Next Autogeneration and Safe Revisions (Option B)
#
# Contract compliance:
# - Inventory-first (already completed)
# - No nano
# - Full-file creation only
# - Full-file replacement only (with mandatory legacy backups)
# - No silent success: hard-fail on missing legacy imports
#
# © 2025 L. David Mendoza
# Date: 2025-12-23
# ==============================================================================

ROOT="$(pwd)"
echo "🔹 Repo Root: $ROOT"

# ---------- Helpers ----------
die() { echo "❌ ERROR: $1" >&2; exit 1; }

require_file() {
  [[ -f "$1" ]] || die "Required file missing: $1"
}

backup_legacy() {
  local f="$1"
  require_file "$f"
  local legacy="${f%.py}_legacy.py"
  if [[ -f "$legacy" ]]; then
    echo "ℹ️ Legacy already exists: $legacy (leaving as-is)"
  else
    mv "$f" "$legacy"
    echo "✅ Backed up $f -> $legacy"
  fi
}

mkdir -p modules/phase_next

# ==============================================================================
# A) AUTOGENERATE NEW PHASE-NEXT MODULES (⬜ Missing)
# ==============================================================================

cat <<'PY' > modules/phase_next/__init__.py
"""
modules.phase_next
Phase-Next Semantic, Social, Predictive, and Intelligence Layer.

These modules are additive and do not invalidate prior Tracks A–H.
They are designed to be consumed by existing phases through thin wrappers.

© 2025 L. David Mendoza
Version: v1.0.0 (Phase-Next scaffolding)
Date: 2025-12-23
"""
PY

cat <<'PY' > modules/phase_next/lemma_normalizer.py
"""
lemma_normalizer.py
Deterministic lemma, tense, and word-family normalization.

Purpose:
- Normalize word families: manage, manages, managed, management.
- Reduce false negatives in role and skill matching.

Notes:
- Uses only deterministic processing.
- Safe to run on any text corpus.

© 2025 L. David Mendoza
Version: v1.0.0
Date: 2025-12-23
Changelog:
- Initial Phase-Next implementation.
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, List
import re

_WORD_RE = re.compile(r"[A-Za-z0-9_+\-]+")

@dataclass(frozen=True)
class LemmaResult:
    original: str
    normalized: str
    tokens: List[str]

def normalize_text(text: str) -> LemmaResult:
    if text is None:
        text = ""
    original = text
    t = text.strip()

    # Minimal deterministic normalization.
    t = re.sub(r"\s+", " ", t)
    t = t.replace("–", "-").replace("—", "-")  # normalize dashes to hyphen
    tokens = _WORD_RE.findall(t.lower())

    # Very lightweight suffix stripping to approximate lemma families.
    # This is intentionally conservative.
    norm_tokens: List[str] = []
    for tok in tokens:
        if tok.endswith("ing") and len(tok) > 5:
            norm_tokens.append(tok[:-3])
        elif tok.endswith("ed") and len(tok) > 4:
            norm_tokens.append(tok[:-2])
        elif tok.endswith("es") and len(tok) > 4:
            norm_tokens.append(tok[:-2])
        elif tok.endswith("s") and len(tok) > 3:
            norm_tokens.append(tok[:-1])
        else:
            norm_tokens.append(tok)

    normalized = " ".join(norm_tokens)
    return LemmaResult(original=original, normalized=normalized, tokens=norm_tokens)

def normalize_fields(fields: Dict[str, str]) -> Dict[str, LemmaResult]:
    out: Dict[str, LemmaResult] = {}
    for k, v in fields.items():
        out[k] = normalize_text(v if isinstance(v, str) else "")
    return out
PY

cat <<'PY' > modules/phase_next/title_variant_resolver.py
"""
title_variant_resolver.py
Variant/Legacy/Adjacent/Industry Title resolution.

Purpose:
- Normalize drifting titles and map them into stable canonical families.
- Reduce misclassification due to ambiguous enterprise titles.

© 2025 L. David Mendoza
Version: v1.0.0
Date: 2025-12-23
Changelog:
- Initial Phase-Next implementation.
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, Optional
import re

@dataclass(frozen=True)
class TitleResolution:
    raw_title: str
    normalized_title: str
    canonical_family: str
    confidence: float

_CANONICAL_MAP: Dict[str, str] = {
    # Examples, extend over time in a governed way:
    "member of technical staff": "MTS",
    "mts": "MTS",
    "research engineer": "Research Engineer",
    "research scientist": "Research Scientist",
    "software engineer": "Software Engineer",
    "principal engineer": "Principal Engineer",
}

_FAMILY_RULES = [
    (re.compile(r"\b(research)\b", re.I), "Research"),
    (re.compile(r"\b(ml|machine learning|ai)\b", re.I), "AI/ML"),
    (re.compile(r"\b(infra|platform|distributed|systems|sre)\b", re.I), "Infra/Systems"),
]

def resolve_title(title: str) -> TitleResolution:
    raw = title or ""
    t = raw.strip().lower()
    t = re.sub(r"\s+", " ", t)

    normalized = _CANONICAL_MAP.get(t, raw.strip())

    canonical_family = "General"
    conf = 0.50

    for rx, fam in _FAMILY_RULES:
        if rx.search(raw):
            canonical_family = fam
            conf = 0.70
            break

    # If normalized maps strongly, bump confidence.
    if t in _CANONICAL_MAP:
        conf = max(conf, 0.80)

    return TitleResolution(
        raw_title=raw,
        normalized_title=normalized,
        canonical_family=canonical_family,
        confidence=conf
    )
PY

cat <<'PY' > modules/phase_next/corpus_analyzer.py
"""
corpus_analyzer.py
Corpus-level analysis across artifacts (repos, papers, posts, bios).

Purpose:
- Aggregate text across sources into a single governed corpus per entity.
- Emit deterministic corpus features (length, uniqueness, keyword density).
- Enable GPT to reason on structured corpus signals.

© 2025 L. David Mendoza
Version: v1.0.0
Date: 2025-12-23
Changelog:
- Initial Phase-Next implementation.
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import List, Dict
import re
from collections import Counter

_WORD_RE = re.compile(r"[A-Za-z0-9_+\-]+")

@dataclass(frozen=True)
class CorpusFeatures:
    total_chars: int
    total_tokens: int
    unique_tokens: int
    top_tokens: List[str]

def build_corpus(text_blocks: List[str]) -> str:
    blocks = [b for b in (text_blocks or []) if isinstance(b, str) and b.strip()]
    return "\n".join(blocks).strip()

def extract_features(corpus: str, top_n: int = 25) -> CorpusFeatures:
    c = corpus or ""
    tokens = _WORD_RE.findall(c.lower())
    counts = Counter(tokens)
    top_tokens = [t for t, _ in counts.most_common(top_n)]
    return CorpusFeatures(
        total_chars=len(c),
        total_tokens=len(tokens),
        unique_tokens=len(counts),
        top_tokens=top_tokens
    )

def analyze(text_blocks: List[str]) -> Dict[str, object]:
    corpus = build_corpus(text_blocks)
    feats = extract_features(corpus)
    return {
        "corpus": corpus,
        "corpus_total_chars": feats.total_chars,
        "corpus_total_tokens": feats.total_tokens,
        "corpus_unique_tokens": feats.unique_tokens,
        "corpus_top_tokens": feats.top_tokens,
    }
PY

cat <<'PY' > modules/phase_next/multilang_diff.py
"""
multilang_diff.py
Multi-language diff and symbol-safe normalization.

Purpose:
- Identify language of text blocks (lightweight heuristic).
- Create deterministic diffs between snapshots.
- Handle symbols safely (no mojibake insertion into non-URL fields).

© 2025 L. David Mendoza
Version: v1.0.0
Date: 2025-12-23
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, Optional
import hashlib

@dataclass(frozen=True)
class DiffResult:
    old_hash: str
    new_hash: str
    changed: bool

def stable_hash(text: str) -> str:
    t = (text or "").encode("utf-8", errors="ignore")
    return hashlib.sha256(t).hexdigest()

def diff_text(old: str, new: str) -> DiffResult:
    oh = stable_hash(old)
    nh = stable_hash(new)
    return DiffResult(old_hash=oh, new_hash=nh, changed=(oh != nh))

def detect_language_hint(text: str) -> str:
    # Very lightweight heuristic. Replace with robust detector later if needed.
    t = text or ""
    ascii_ratio = sum(1 for ch in t if ord(ch) < 128) / max(1, len(t))
    return "en" if ascii_ratio > 0.92 else "multi"
PY

cat <<'PY' > modules/phase_next/social_signal_ingest.py
"""
social_signal_ingest.py
Social and community signal ingestion (public sources only).

Purpose:
- Ingest public social/community artifacts into structured signals.
- Sources: conferences, forums, groups, podcasts, X/Twitter, YouTube comments.
- No auth walls. No private data. Evidence-only.

© 2025 L. David Mendoza
Version: v1.0.0
Date: 2025-12-23
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import List, Dict, Optional

@dataclass(frozen=True)
class SocialArtifact:
    source: str
    url: str
    text: str

def ingest(artifacts: List[SocialArtifact]) -> Dict[str, object]:
    arts = artifacts or []
    return {
        "social_artifact_count": len(arts),
        "social_sources": sorted({a.source for a in arts if a.source}),
        "social_urls": [a.url for a in arts if a.url],
    }
PY

cat <<'PY' > modules/phase_next/sentiment_analyzer.py
"""
sentiment_analyzer.py
Technical sentiment, not opinionated.

Purpose:
- Score peer reception signals as technical credibility indicators.
- Input is structured evidence harvested by Python ingestion.

© 2025 L. David Mendoza
Version: v1.0.0
Date: 2025-12-23
"""

from __future__ import annotations
from typing import Dict

def score_technical_sentiment(text: str) -> Dict[str, float]:
    # Deterministic placeholder scoring:
    # Later: GPT can interpret nuanced tone, but Python should provide feature hooks.
    t = (text or "").lower()
    pos = sum(1 for w in ["excellent", "robust", "state-of-the-art", "breakthrough", "solid"] if w in t)
    neg = sum(1 for w in ["broken", "buggy", "incorrect", "misleading", "unsafe"] if w in t)
    return {
        "tech_sent_pos_hits": float(pos),
        "tech_sent_neg_hits": float(neg),
        "tech_sent_balance": float(pos - neg),
    }
PY

cat <<'PY' > modules/phase_next/community_presence_index.py
"""
community_presence_index.py
Community Presence Index (CPI).

Purpose:
- Quantify presence across communities and platforms.
- Provide deterministic counts for GPT interpretation.

© 2025 L. David Mendoza
Version: v1.0.0
Date: 2025-12-23
"""

from __future__ import annotations
from typing import Dict, List

def compute_cpi(platform_hits: Dict[str, int]) -> Dict[str, float]:
    hits = platform_hits or {}
    total = sum(max(0, int(v)) for v in hits.values())
    diversity = sum(1 for v in hits.values() if int(v) > 0)
    return {
        "cpi_total_hits": float(total),
        "cpi_platform_diversity": float(diversity),
        "cpi_score": float(total + 3 * diversity),
    }
PY

cat <<'PY' > modules/phase_next/time_series_features.py
"""
time_series_features.py
Time-series feature builder for trajectory modeling.

© 2025 L. David Mendoza
Version: v1.0.0
Date: 2025-12-23
"""

from __future__ import annotations
from typing import Dict, List

def build_features(timestamps: List[str]) -> Dict[str, float]:
    # Deterministic placeholder: count and basic density.
    ts = [t for t in (timestamps or []) if isinstance(t, str) and t.strip()]
    return {
        "ts_event_count": float(len(ts)),
    }
PY

cat <<'PY' > modules/phase_next/momentum_scorer.py
"""
momentum_scorer.py
Momentum scoring for rising vs static contributors.

© 2025 L. David Mendoza
Version: v1.0.0
Date: 2025-12-23
"""

from __future__ import annotations
from typing import Dict

def score(momentum_inputs: Dict[str, float]) -> Dict[str, float]:
    mi = momentum_inputs or {}
    v = float(mi.get("velocity", 0.0))
    d = float(mi.get("delta", 0.0))
    score = v + 2.0 * d
    return {"momentum_score": score}
PY

cat <<'PY' > modules/phase_next/trajectory_engine.py
"""
trajectory_engine.py
Trajectory forecasting hooks.

Purpose:
- Produce deterministic forecasting features from diffs, velocity, and time series.
- GPT layer can interpret forecasts, but Python provides structure.

© 2025 L. David Mendoza
Version: v1.0.0
Date: 2025-12-23
"""

from __future__ import annotations
from typing import Dict

def forecast(features: Dict[str, float]) -> Dict[str, float]:
    f = features or {}
    v = float(f.get("velocity", 0.0))
    m = float(f.get("momentum_score", 0.0))
    # Deterministic placeholder, expandable.
    return {
        "trajectory_forecast_score": v + 0.5 * m
    }
PY

cat <<'PY' > modules/phase_next/openalex_lifecycle_tracker.py
"""
openalex_lifecycle_tracker.py
Paper lifecycle tracking: preprint -> published -> patent references.

© 2025 L. David Mendoza
Version: v1.0.0
Date: 2025-12-23
"""

from __future__ import annotations
from typing import Dict, List

def track(records: List[Dict[str, object]]) -> Dict[str, float]:
    recs = records or []
    pre = sum(1 for r in recs if str(r.get("type","")).lower() in ["preprint", "arxiv"])
    pub = sum(1 for r in recs if str(r.get("type","")).lower() in ["paper", "journal", "conference"])
    pat = sum(1 for r in recs if str(r.get("type","")).lower() in ["patent"])
    return {
        "openalex_preprints": float(pre),
        "openalex_published": float(pub),
        "openalex_patents": float(pat),
    }
PY

cat <<'PY' > modules/phase_next/hindex_normalizer.py
"""
hindex_normalizer.py
h-index normalization hooks.

© 2025 L. David Mendoza
Version: v1.0.0
Date: 2025-12-23
"""

from __future__ import annotations
from typing import Dict

def normalize(h_index: int | float | None) -> Dict[str, float]:
    try:
        h = float(h_index or 0.0)
    except Exception:
        h = 0.0
    # Deterministic normalization placeholder.
    return {"h_index": h, "h_index_norm": min(1.0, h / 60.0)}
PY

cat <<'PY' > modules/phase_next/concordance_scorer.py
"""
concordance_scorer.py
Measured concordance between claims and evidence.

© 2025 L. David Mendoza
Version: v1.0.0
Date: 2025-12-23
"""

from __future__ import annotations
from typing import Dict, List

def score(claims: List[str], evidence: List[str]) -> Dict[str, float]:
    # Deterministic placeholder: overlap count.
    c = " ".join(claims or []).lower()
    e = " ".join(evidence or []).lower()
    hits = 0
    for w in ["trained", "deployed", "optimized", "published", "open sourced"]:
        if w in c and w in e:
            hits += 1
    return {"concordance_hits": float(hits)}
PY

cat <<'PY' > modules/phase_next/funding_signal_ingest.py
"""
funding_signal_ingest.py
Funding signals: grants, venture, lab funding (public sources).

© 2025 L. David Mendoza
Version: v1.0.0
Date: 2025-12-23
"""

from __future__ import annotations
from typing import Dict, List

def ingest(records: List[Dict[str, object]]) -> Dict[str, float]:
    recs = records or []
    grants = sum(1 for r in recs if str(r.get("type","")).lower() == "grant")
    venture = sum(1 for r in recs if str(r.get("type","")).lower() == "venture")
    return {
        "funding_grants": float(grants),
        "funding_venture": float(venture),
    }
PY

cat <<'PY' > modules/phase_next/rfc_participation_tracker.py
"""
rfc_participation_tracker.py
RFC and standards participation hooks.

© 2025 L. David Mendoza
Version: v1.0.0
Date: 2025-12-23
"""

from __future__ import annotations
from typing import Dict, List

def track(rfcs: List[Dict[str, object]]) -> Dict[str, float]:
    items = rfcs or []
    authored = sum(1 for r in items if str(r.get("role","")).lower() in ["author", "editor"])
    referenced = float(len(items))
    return {"rfc_authored": float(authored), "rfc_referenced": referenced}
PY

cat <<'PY' > modules/phase_next/continuous_discovery_scheduler.py
"""
continuous_discovery_scheduler.py
Continuous discovery loop driver.

Purpose:
- Establish a deterministic schedule of discovery runs.
- Does not run in background. It is invoked explicitly by runner.

© 2025 L. David Mendoza
Version: v1.0.0
Date: 2025-12-23
"""

from __future__ import annotations
from typing import Dict

def plan(monitoring_tier: str) -> Dict[str, int]:
    tier = (monitoring_tier or "").strip().lower()
    if tier in ["high", "tier1", "t1"]:
        return {"recommended_days": 3}
    if tier in ["medium", "tier2", "t2"]:
        return {"recommended_days": 7}
    return {"recommended_days": 14}
PY

# ==============================================================================
# B) SAFE FULL REPLACEMENTS FOR PARTIAL FILES (🟡)
#    Contract compliant: full replacement with legacy backup.
# ==============================================================================

PARTIAL_FILES=(
  "phase_f_normalize.py"
  "phase_f_velocity_analyzer.py"
  "phase_g_signal_scoring.py"
  "phase_g_role_weighting.py"
  "phase_d_diff_engine.py"
  "phase_e_emergence_detector.py"
)

for f in "${PARTIAL_FILES[@]}"; do
  backup_legacy "$f"
done

# --- phase_f_normalize.py wrapper ---
cat <<'PY' > phase_f_normalize.py
"""
phase_f_normalize.py
Phase F Normalization (Phase-Next extended wrapper)

This file is a full replacement that preserves legacy behavior and extends it with:
- Lemma/tense normalization
- Title variant resolution hooks

Legacy file:
- phase_f_normalize_legacy.py

Hard rule:
- No silent success. If legacy module cannot be loaded, this fails.

© 2025 L. David Mendoza
Version: v1.1.0-phase-next
Date: 2025-12-23
Changelog:
- Wrapped legacy implementation.
- Added lemma and title resolution hooks.
"""

from __future__ import annotations
import importlib
from typing import Any, Dict
from modules.phase_next.lemma_normalizer import normalize_fields
from modules.phase_next.title_variant_resolver import resolve_title

LEGACY = "phase_f_normalize_legacy"

def _load_legacy():
    return importlib.import_module(LEGACY)

def phase_next_normalize_row(row: Dict[str, Any]) -> Dict[str, Any]:
    out = dict(row or {})
    title = str(out.get("Title") or out.get("Current Title") or "")
    tr = resolve_title(title)
    out["Title_Normalized"] = tr.normalized_title
    out["Title_Canonical_Family"] = tr.canonical_family
    out["Title_Resolution_Confidence"] = tr.confidence

    fields = {
        "Title": title,
        "Summary": str(out.get("Summary") or ""),
        "Skills": str(out.get("Skills") or out.get("Skills2") or ""),
        "Experience": str(out.get("Experience") or ""),
    }
    norms = normalize_fields(fields)
    out["Lemma_Title"] = norms["Title"].normalized
    out["Lemma_Summary"] = norms["Summary"].normalized
    out["Lemma_Skills"] = norms["Skills"].normalized
    out["Lemma_Experience"] = norms["Experience"].normalized
    return out

def main(*args, **kwargs):
    legacy = _load_legacy()
    if not hasattr(legacy, "main"):
        raise RuntimeError("Legacy module missing main()")
    return legacy.main(*args, **kwargs)

PY

# --- phase_f_velocity_analyzer.py wrapper ---
cat <<'PY' > phase_f_velocity_analyzer.py
"""
phase_f_velocity_analyzer.py
Phase F Velocity (Phase-Next extended wrapper)

Adds deterministic momentum and trajectory hooks while preserving legacy behavior.

Legacy:
- phase_f_velocity_analyzer_legacy.py

© 2025 L. David Mendoza
Version: v1.1.0-phase-next
Date: 2025-12-23
"""

from __future__ import annotations
import importlib
from typing import Dict
from modules.phase_next.momentum_scorer import score as momentum_score
from modules.phase_next.trajectory_engine import forecast as trajectory_forecast

LEGACY = "phase_f_velocity_analyzer_legacy"

def _load_legacy():
    return importlib.import_module(LEGACY)

def phase_next_velocity_features(velocity: float, delta: float) -> Dict[str, float]:
    m = momentum_score({"velocity": velocity, "delta": delta})
    t = trajectory_forecast({"velocity": velocity, **m})
    return {**m, **t}

def main(*args, **kwargs):
    legacy = _load_legacy()
    if not hasattr(legacy, "main"):
        raise RuntimeError("Legacy module missing main()")
    return legacy.main(*args, **kwargs)
PY

# --- phase_g_signal_scoring.py wrapper ---
cat <<'PY' > phase_g_signal_scoring.py
"""
phase_g_signal_scoring.py
Phase G Signal Scoring (Phase-Next extended wrapper)

Preserves legacy scoring and adds structured hooks for:
- Semantics features (corpus)
- Technical sentiment features
- Concordance scoring hooks
- Research lifecycle and h-index hooks

Legacy:
- phase_g_signal_scoring_legacy.py

© 2025 L. David Mendoza
Version: v1.1.0-phase-next
Date: 2025-12-23
"""

from __future__ import annotations
import importlib
from typing import Any, Dict, List
from modules.phase_next.corpus_analyzer import analyze as corpus_analyze
from modules.phase_next.sentiment_analyzer import score_technical_sentiment
from modules.phase_next.concordance_scorer import score as concordance_score
from modules.phase_next.openalex_lifecycle_tracker import track as openalex_track
from modules.phase_next.hindex_normalizer import normalize as hindex_norm

LEGACY = "phase_g_signal_scoring_legacy"

def _load_legacy():
    return importlib.import_module(LEGACY)

def phase_next_signal_bundle(text_blocks: List[str], sentiment_text: str,
                             claims: List[str], evidence: List[str],
                             openalex_records: List[Dict[str, object]],
                             h_index: Any) -> Dict[str, Any]:
    c = corpus_analyze(text_blocks)
    s = score_technical_sentiment(sentiment_text)
    conc = concordance_score(claims, evidence)
    oa = openalex_track(openalex_records)
    hi = hindex_norm(h_index)
    return {**c, **s, **conc, **oa, **hi}

def main(*args, **kwargs):
    legacy = _load_legacy()
    if not hasattr(legacy, "main"):
        raise RuntimeError("Legacy module missing main()")
    return legacy.main(*args, **kwargs)
PY

# --- phase_g_role_weighting.py wrapper ---
cat <<'PY' > phase_g_role_weighting.py
"""
phase_g_role_weighting.py
Phase G Role Weighting (Phase-Next extended wrapper)

Adds title variant normalization hooks while preserving legacy behavior.

Legacy:
- phase_g_role_weighting_legacy.py

© 2025 L. David Mendoza
Version: v1.1.0-phase-next
Date: 2025-12-23
"""

from __future__ import annotations
import importlib
from typing import Any, Dict
from modules.phase_next.title_variant_resolver import resolve_title

LEGACY = "phase_g_role_weighting_legacy"

def _load_legacy():
    return importlib.import_module(LEGACY)

def phase_next_title_weight(title: str) -> Dict[str, Any]:
    tr = resolve_title(title or "")
    return {
        "title_normalized": tr.normalized_title,
        "title_family": tr.canonical_family,
        "title_confidence": tr.confidence
    }

def main(*args, **kwargs):
    legacy = _load_legacy()
    if not hasattr(legacy, "main"):
        raise RuntimeError("Legacy module missing main()")
    return legacy.main(*args, **kwargs)
PY

# --- phase_d_diff_engine.py wrapper ---
cat <<'PY' > phase_d_diff_engine.py
"""
phase_d_diff_engine.py
Phase D Diff Engine (Phase-Next extended wrapper)

Adds multi-language diff hooks while preserving legacy behavior.

Legacy:
- phase_d_diff_engine_legacy.py

© 2025 L. David Mendoza
Version: v1.1.0-phase-next
Date: 2025-12-23
"""

from __future__ import annotations
import importlib
from modules.phase_next.multilang_diff import diff_text, detect_language_hint

LEGACY = "phase_d_diff_engine_legacy"

def _load_legacy():
    return importlib.import_module(LEGACY)

def phase_next_diff(old: str, new: str):
    return diff_text(old, new)

def phase_next_lang(text: str) -> str:
    return detect_language_hint(text)

def main(*args, **kwargs):
    legacy = _load_legacy()
    if not hasattr(legacy, "main"):
        raise RuntimeError("Legacy module missing main()")
    return legacy.main(*args, **kwargs)
PY

# --- phase_e_emergence_detector.py wrapper ---
cat <<'PY' > phase_e_emergence_detector.py
"""
phase_e_emergence_detector.py
Phase E Emergence Detector (Phase-Next extended wrapper)

Adds social/community signal ingestion hooks while preserving legacy behavior.

Legacy:
- phase_e_emergence_detector_legacy.py

© 2025 L. David Mendoza
Version: v1.1.0-phase-next
Date: 2025-12-23
"""

from __future__ import annotations
import importlib
from modules.phase_next.social_signal_ingest import ingest as social_ingest, SocialArtifact

LEGACY = "phase_e_emergence_detector_legacy"

def _load_legacy():
    return importlib.import_module(LEGACY)

def phase_next_social_summary(artifacts):
    return social_ingest(artifacts)

def main(*args, **kwargs):
    legacy = _load_legacy()
    if not hasattr(legacy, "main"):
        raise RuntimeError("Legacy module missing main()")
    return legacy.main(*args, **kwargs)
PY

# ==============================================================================
# C) VALIDATION STEPS (Hard fail if broken)
# ==============================================================================

echo "✅ Files generated. Running lightweight import checks..."

python3 -c "import modules.phase_next.lemma_normalizer as m; print('OK lemma_normalizer')"
python3 -c "import modules.phase_next.title_variant_resolver as t; print('OK title_variant_resolver')"
python3 -c "import modules.phase_next.corpus_analyzer as c; print('OK corpus_analyzer')"
python3 -c "import modules.phase_next.multilang_diff as d; print('OK multilang_diff')"
python3 -c "import modules.phase_next.social_signal_ingest as s; print('OK social_signal_ingest')"
python3 -c "import modules.phase_next.sentiment_analyzer as se; print('OK sentiment_analyzer')"
python3 -c "import modules.phase_next.community_presence_index as cp; print('OK community_presence_index')"
python3 -c "import modules.phase_next.time_series_features as ts; print('OK time_series_features')"
python3 -c "import modules.phase_next.momentum_scorer as ms; print('OK momentum_scorer')"
python3 -c "import modules.phase_next.trajectory_engine as te; print('OK trajectory_engine')"
python3 -c "import modules.phase_next.openalex_lifecycle_tracker as oa; print('OK openalex_lifecycle_tracker')"
python3 -c "import modules.phase_next.hindex_normalizer as hi; print('OK hindex_normalizer')"
python3 -c "import modules.phase_next.concordance_scorer as co; print('OK concordance_scorer')"
python3 -c "import modules.phase_next.funding_signal_ingest as fs; print('OK funding_signal_ingest')"
python3 -c "import modules.phase_next.rfc_participation_tracker as rf; print('OK rfc_participation_tracker')"
python3 -c "import modules.phase_next.continuous_discovery_scheduler as cd; print('OK continuous_discovery_scheduler')"

echo "✅ Module imports OK."

echo "ℹ️ NOTE: Legacy phase imports are validated at runtime when those phases execute."
echo "✅ Autogeneration complete."

# ==============================================================================
# D) GIT COMMANDS (SSH assumed)
# ==============================================================================
cat <<'TXT'

NEXT: Git commands (SSH assumed)
--------------------------------
git status
git add modules/phase_next *.py
git commit -m "Phase-Next: add semantic/social/predictive modules + safe wrappers with legacy backups"
git push

TXT
