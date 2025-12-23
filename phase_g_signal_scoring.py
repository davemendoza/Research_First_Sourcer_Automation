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
