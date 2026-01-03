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
