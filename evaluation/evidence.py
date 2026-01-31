# ==============================================================================
# AI TALENT ENGINE – SIGNAL INTELLIGENCE
# Proprietary and Confidential
# © 2025–2026 L. David Mendoza. All Rights Reserved.
# ==============================================================================
#
# This file contains proprietary intellectual property and trade secrets of
# L. David Mendoza and is part of the AI Talent Engine – Signal Intelligence system.
#
# Unauthorized access, use, copying, modification, distribution, disclosure,
# reverse engineering, or derivative use, in whole or in part, is strictly
# prohibited without prior written authorization.
#
# ==============================================================================
#
# FILE: evaluation/evidence.py
# VERSION: v1.0.0
#
# CHANGELOG:
# - v1.0.0 (2026-01-31): Evidence normalizer and term extraction.
#
# VALIDATION:
# - python3 -c "from evaluation.evidence import EvidenceNormalizer; print('ok')"
#
# GIT:
# - git add evaluation/evidence.py
# - git commit -m "Add evidence normalizer (v1.0.0)"
# - git push
#

from __future__ import annotations

import json
import os
import re
from typing import Dict, List, Set, Tuple


_DEFAULT_NORMALIZATION: Dict[str, str] = {
    # Normalization seeds. Final bible-derived expansions live in knowledge JSON files.
    "retrieval augmented generation": "RAG",
    "retrieval-augmented generation": "RAG",
    "vector database": "Vector DB",
    "vector db": "Vector DB",
    "lang chain": "LangChain",
    "llama index": "LlamaIndex",
    "fast api": "FastAPI",
    "gpt4": "GPT-4",
    "gpt-4o": "GPT-4o",
    "claude3": "Claude 3",
    "gemini pro": "Gemini Pro",
    "grok": "Grok",
}

_WORD_RE = re.compile(r"[A-Za-z0-9\-\.\+/#_]{2,}")


class EvidenceNormalizer:
    """
    Normalizes terminology drift using evaluation/knowledge/terminology_normalization_map.json if present.
    """

    def __init__(self, repo_root: str) -> None:
        self.repo_root = repo_root
        self.knowledge_path = os.path.join(repo_root, "evaluation", "knowledge", "terminology_normalization_map.json")
        self.map: Dict[str, str] = dict(_DEFAULT_NORMALIZATION)
        self._load()

    def _load(self) -> None:
        if not os.path.isfile(self.knowledge_path):
            return
        with open(self.knowledge_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        if not isinstance(data, dict):
            return
        pairs = data.get("pairs", [])
        if not isinstance(pairs, list):
            return
        for item in pairs:
            if not isinstance(item, dict):
                continue
            src = (item.get("src") or "").strip().lower()
            dst = (item.get("dst") or "").strip()
            if src and dst:
                self.map[src] = dst

    def normalize_text(self, text: str) -> str:
        if not text:
            return ""
        # Lowercase for matching, then replace token-level by lookup.
        words = _WORD_RE.findall(text)
        out_words: List[str] = []
        for w in words:
            key = w.strip().lower()
            out_words.append(self.map.get(key, w))
        return " ".join(out_words)

    def extract_terms(self, text: str) -> List[str]:
        """
        Extract a de-duplicated list of normalized terms from text.
        """
        if not text:
            return []
        norm = self.normalize_text(text)
        tokens = _WORD_RE.findall(norm)
        seen: Set[str] = set()
        out: List[str] = []
        for t in tokens:
            k = t.strip()
            if not k:
                continue
            if k in seen:
                continue
            seen.add(k)
            out.append(k)
        return out