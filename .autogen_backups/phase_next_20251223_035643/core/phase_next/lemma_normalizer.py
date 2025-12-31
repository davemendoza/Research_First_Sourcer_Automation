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
