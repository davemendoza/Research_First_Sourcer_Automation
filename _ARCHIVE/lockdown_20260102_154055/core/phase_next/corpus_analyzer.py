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
