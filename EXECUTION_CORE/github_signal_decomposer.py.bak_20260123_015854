#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EXECUTION_CORE/github_signal_decomposer.py
============================================================
GITHUB SIGNAL DECOMPOSER (Sample.xlsx Evidence Planes)

Maintainer: L. David Mendoza © 2026
Version: v1.0.0 (Autogen rebuild, best-in-class)

Mission:
Decompose GitHub-related evidence into Sample.xlsx-like evidence planes.

This module does not fetch network data. It transforms fields already present
in a row into:
- Repo_Topics_Keywords
- GitHub_Repo_Evidence_Why
- Downstream_Adoption_Signal
- Open_Source_Impact_Note

Contract:
- decompose_github_signals(row: dict) -> dict[str,str]
- apply_github_signal_decomposition(rows: list[dict], out_map: dict | None=None) -> list[dict]

Safety:
- No network calls
- Deterministic
- No fabrication
- Uses only row fields and conservative tokenization

Validation:
python3 -m py_compile EXECUTION_CORE/_AUTOGEN_STAGING/github_signal_decomposer.py

Git:
git add EXECUTION_CORE/github_signal_decomposer.py
git commit -m "Add GitHub signal decomposer (Sample.xlsx evidence planes)"
git push
"""

from __future__ import annotations

import json
import re
from typing import Any, Dict, List, Set, Tuple

_VERSION = "v1.0.0"

_WS_RE = re.compile(r"\s+", re.UNICODE)
_SPLIT_RE = re.compile(r"[,;/|]+|\s{2,}", re.UNICODE)


def _norm(s: str) -> str:
    s = (s or "").strip()
    s = _WS_RE.sub(" ", s)
    return s


def _low(s: str) -> str:
    return _norm(s).lower()


def _safe_str(v: Any) -> str:
    if v is None:
        return ""
    try:
        return str(v)
    except Exception:
        return ""


def _parse_json_maybe(s: str) -> Any:
    s = (s or "").strip()
    if not s:
        return None
    try:
        return json.loads(s)
    except Exception:
        return None


def _extract_repo_tokens(row: Dict[str, Any]) -> Tuple[Set[str], List[str]]:
    """
    Attempts to harvest repo topics/keywords from common schema fields.
    Returns (token_set, evidence_lines).
    """
    evidence_lines: List[str] = []
    tokens: Set[str] = set()

    candidate_fields = [
        "Repo_Topics_Keywords",
        "Repo_Topics",
        "Repo_Topics_JSON",
        "Repo_Languages",
        "Repo_Languages_JSON",
        "Repo_Descriptions",
        "Repo_Description",
        "Repo_Readme_Text",
        "Repo_README_Text",
        "Repo_Text",
        "OSS_Evidence",
        "OSS_Signals",
    ]

    for k in candidate_fields:
        if k in row and row.get(k):
            v = _safe_str(row.get(k))
            evidence_lines.append(f"{k}: {v[:500]}")

            if k.endswith("_JSON"):
                obj = _parse_json_maybe(v)
                if isinstance(obj, dict):
                    for kk, vv in obj.items():
                        tokens.add(_low(kk))
                        if isinstance(vv, str):
                            tokens.add(_low(vv))
                        elif isinstance(vv, (int, float)):
                            tokens.add(_low(str(vv)))
                elif isinstance(obj, list):
                    for it in obj:
                        tokens.add(_low(_safe_str(it)))
            else:
                for part in _SPLIT_RE.split(v):
                    p = _low(part)
                    if not p:
                        continue
                    if len(p) < 2:
                        continue
                    tokens.add(p)

    # also mine URLs for hint tokens (repo names)
    for url_key in ["GitHub_URL", "Github_URL", "GitHub_Profile_URL", "Repo_URLs", "Repos", "Repos_URLs"]:
        if url_key in row and row.get(url_key):
            u = _safe_str(row.get(url_key))
            evidence_lines.append(f"{url_key}: {u[:500]}")
            # split on whitespace, commas
            for tok in re.split(r"[\s,;]+", u):
                tok = tok.strip()
                if not tok:
                    continue
                # take repo tail segments
                parts = tok.rstrip("/").split("/")
                if len(parts) >= 2:
                    repo = parts[-1]
                    owner = parts[-2]
                    for x in (owner, repo):
                        x = _low(x)
                        if x and len(x) >= 2 and not x.startswith("http"):
                            tokens.add(x)

    return tokens, evidence_lines


def _summarize_keywords(tokens: Set[str]) -> str:
    """
    Produces a compact, deterministic keyword string.
    Filters to technical-ish tokens and dedupes.
    """
    stop = {
        "the", "and", "or", "a", "an", "of", "to", "in", "for", "with",
        "github", "com", "www", "http", "https",
        "readme", "license", "mit", "apache", "bsd",
        "project", "repo", "repository",
    }
    keep: List[str] = []
    for t in sorted(tokens):
        if t in stop:
            continue
        if len(t) < 3:
            continue
        # discard pure numbers
        if t.isdigit():
            continue
        keep.append(t)

    # cap to avoid exploding cell size
    keep = keep[:60]
    return "; ".join(keep)


def _derive_adoption_signal(row: Dict[str, Any], tokens: Set[str]) -> str:
    """
    Conservative adoption signal from explicit fork/star/use language if available.
    """
    fields = [
        "Downstream_Adoption_Signal",
        "Open_Source_Impact_Note",
        "GitHub_Repo_Evidence_Why",
        "OSS_Evidence",
        "OSS_Signals",
    ]
    text = " ".join(_low(_safe_str(row.get(k, ""))) for k in fields)
    cues = []
    if "fork" in text or "forks" in text:
        cues.append("fork graph referenced")
    if "star" in text or "stars" in text:
        cues.append("stars referenced")
    if "used by" in text or "depend" in text or "dependency" in text:
        cues.append("dependency usage referenced")
    if "download" in text or "pip install" in text or "npm install" in text:
        cues.append("installation footprint referenced")
    if "production" in text or "deployed" in text or "serving" in text:
        cues.append("deployment language present")
    if not cues:
        # try token-based inference only if explicit phrases exist in row
        # still conservative: requires at least one adoption term in any field
        adoption_terms = ["used by", "adopt", "adoption", "deploy", "production", "customers", "enterprise", "integrat"]
        if any(t in text for t in adoption_terms):
            return "adoption language present (details not enumerated)"
        return ""
    return "; ".join(cues)


def _derive_repo_why(row: Dict[str, Any]) -> str:
    """
    Builds a minimal evidence why string from existing explicit fields, without making claims.
    """
    preferred = [
        "GitHub_Repo_Evidence_Why",
        "Open_Source_Impact_Note",
        "OSS_Evidence",
        "OSS_Signals",
        "Repo_Descriptions",
        "Repo_Description",
    ]
    parts: List[str] = []
    for k in preferred:
        v = _safe_str(row.get(k, "")).strip()
        if v:
            parts.append(v)
    if not parts:
        return ""
    # deterministic truncation
    joined = " | ".join(parts)
    return joined[:900]


def decompose_github_signals(row: Dict[str, Any]) -> Dict[str, str]:
    tokens, _ev = _extract_repo_tokens(row)

    repo_topics_keywords = _summarize_keywords(tokens)
    repo_why = _derive_repo_why(row)
    adoption = _derive_adoption_signal(row, tokens)

    impact_note = _safe_str(row.get("Open_Source_Impact_Note", "")).strip()
    if not impact_note:
        # fallback: use repo_why if present, but do not invent
        impact_note = repo_why[:600] if repo_why else ""

    out = {
        "Repo_Topics_Keywords": repo_topics_keywords,
        "GitHub_Repo_Evidence_Why": repo_why,
        "Downstream_Adoption_Signal": adoption,
        "Open_Source_Impact_Note": impact_note,
    }

    if "Field_Level_Provenance_JSON" in row:
        _augment_provenance(row, out)

    return out


def _augment_provenance(row: Dict[str, Any], out: Dict[str, Any]) -> None:
    raw = _safe_str(row.get("Field_Level_Provenance_JSON", "")).strip()
    obj: Dict[str, Any] = {}
    if raw:
        try:
            obj = json.loads(raw)
            if not isinstance(obj, dict):
                obj = {}
        except Exception:
            obj = {}
    obj["GitHub_Signal_Decomposer"] = {
        "version": _VERSION,
        "evidence_basis": "row_text_fields_only",
        "outputs": {k: out.get(k, "") for k in out.keys()},
    }
    row["Field_Level_Provenance_JSON"] = json.dumps(obj, sort_keys=True)


def apply_github_signal_decomposition(
    rows: List[Dict[str, Any]],
    out_map: Dict[str, str] | None = None,
) -> List[Dict[str, Any]]:
    """
    out_map maps standard output keys to your schema keys.
    Example: {"Repo_Topics_Keywords": "Repo_Topics_Keywords"}
    """
    out_map = out_map or {
        "Repo_Topics_Keywords": "Repo_Topics_Keywords",
        "GitHub_Repo_Evidence_Why": "GitHub_Repo_Evidence_Why",
        "Downstream_Adoption_Signal": "Downstream_Adoption_Signal",
        "Open_Source_Impact_Note": "Open_Source_Impact_Note",
    }
    for r in rows:
        out = decompose_github_signals(r)
        for k_std, k_row in out_map.items():
            if not k_row:
                continue
            v = out.get(k_std, "")
            if v:
                r[k_row] = v
            else:
                r[k_row] = r.get(k_row, "")
    return rows


__all__ = [
    "decompose_github_signals",
    "apply_github_signal_decomposition",
]
