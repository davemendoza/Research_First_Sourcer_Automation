"""
EXECUTION_CORE/model_family_attribution.py
============================================================
PRIMARY MODEL FAMILY ATTRIBUTION (Sample.xlsx Gold Standard)

Maintainer: L. David Mendoza © 2026
Version: v1.0.0 (Autogen rebuild, best-in-class)

Mission:
Populate Sample.xlsx-style Primary_Model_Families using evidence in provided row text.

This is evidence-only attribution based on explicit model family mentions.
It does not claim authorship. It attributes model families referenced in the candidate's
evidence corpus (repos, READMEs, abstracts, etc).

Contract:
- attribute_primary_model_families(row: dict) -> list[str]
- apply_primary_model_families(rows: list[dict], out_field: str="Primary_Model_Families") -> list[dict]

Safety:
- No network calls
- Deterministic
- No fabrication

Validation:
python3 -m py_compile EXECUTION_CORE/_AUTOGEN_STAGING/model_family_attribution.py

Git:
git add EXECUTION_CORE/model_family_attribution.py
git commit -m "Add model family attribution (Sample.xlsx gold standard)"
git push
"""
from __future__ import annotations
import json
import re
from typing import Any, Dict, List, Tuple
_VERSION = 'v1.0.0'
_CANONICAL_ORDER = ['GPT-4', 'GPT-4o', 'Claude 3', 'Gemini 1.5', 'LLaMA 3', 'Qwen 2', 'DeepSeek-MoE', 'Mistral', 'Mixtral', 'DBRX']

def _norm(s: str) -> str:
    s = (s or '').strip().lower()
    s = _WS_RE.sub(' ', s)
    return s

def _safe_str(v: Any) -> str:
    if v is None:
        return ''
    try:
        return str(v)
    except Exception:
        return ''

def _collect_text(row: Dict[str, Any]) -> str:
    preferred = ['Primary_Model_Families', 'Repo_Readme_Text', 'Repo_README_Text', 'Repo_Text', 'Repo_Topics_Keywords', 'GitHub_Repo_Evidence_Why', 'Open_Source_Impact_Note', 'Publications_Text', 'Scholar_Abstracts', 'Paper_Abstracts', 'Summary', 'Experience', 'Skills', 'Skills2', 'Headline', 'Title']
    parts: List[str] = []
    for k in preferred:
        if k in row and row.get(k):
            parts.append(_safe_str(row.get(k)))
    for k, v in row.items():
        if k in preferred:
            continue
        if isinstance(v, str) and v.strip():
            if k.endswith('_JSON') or k.endswith('_json'):
                continue
            parts.append(v)
    return _norm(' \n '.join(parts))

def _rx(pattern: str) -> re.Pattern:
    return re.compile(pattern, flags=re.IGNORECASE)

def attribute_primary_model_families(row: Dict[str, Any]) -> List[str]:
    text = _collect_text(row)
    found: List[str] = []
    reasons: Dict[str, str] = {}
    for name, pat in _PATTERNS:
        if pat.search(text):
            found.append(name)
            reasons[name] = 'matched model family token in row evidence text'
    found_set = set(found)
    ordered = [x for x in _CANONICAL_ORDER if x in found_set]
    extras = sorted([x for x in found_set if x not in set(_CANONICAL_ORDER)])
    out = ordered + extras
    if 'Field_Level_Provenance_JSON' in row:
        _augment_provenance(row, 'Primary_Model_Families', out, reasons)
    return out

def _augment_provenance(row: Dict[str, Any], field: str, value: Any, reasons: Dict[str, Any]) -> None:
    raw = _safe_str(row.get('Field_Level_Provenance_JSON', '')).strip()
    obj: Dict[str, Any] = {}
    if raw:
        try:
            obj = json.loads(raw)
            if not isinstance(obj, dict):
                obj = {}
        except Exception:
            obj = {}
    obj[field] = {'version': _VERSION, 'evidence_basis': 'row_text_fields_only', 'value': value, 'reasons': reasons}
    row['Field_Level_Provenance_JSON'] = json.dumps(obj, sort_keys=True)

def apply_primary_model_families(rows: List[Dict[str, Any]], out_field: str='Primary_Model_Families') -> List[Dict[str, Any]]:
    for r in rows:
        fam = attribute_primary_model_families(r)
        r[out_field] = '; '.join(fam) if fam else r.get(out_field, '')
    return rows
__all__ = ['attribute_primary_model_families', 'apply_primary_model_families']

def _cli_main():
    _WS_RE = re.compile('\\s+', re.UNICODE)
    _PATTERNS: List[Tuple[str, re.Pattern]] = [('GPT-4o', _rx('\\bgpt[- ]?4o\\b')), ('GPT-4', _rx('\\bgpt[- ]?4\\b')), ('Claude 3', _rx('\\bclaude\\b.*\\b3\\b|\\bclaude[- ]?3\\b')), ('Gemini 1.5', _rx('\\bgemini\\b.*\\b1\\.?5\\b|\\bgemini[- ]?1\\.?5\\b')), ('LLaMA 3', _rx('\\bllama\\b.*\\b3\\b|\\bllama[- ]?3\\b|\\bllama3\\b')), ('Qwen 2', _rx('\\bqwen\\b.*\\b2\\b|\\bqwen[- ]?2\\b|\\bqwen2\\b')), ('DeepSeek-MoE', _rx('\\bdeepseek\\b.*\\bmoe\\b|\\bdeepseek[- ]?moe\\b')), ('Mixtral', _rx('\\bmixtral\\b')), ('Mistral', _rx('\\bmistral\\b')), ('DBRX', _rx('\\bdbrx\\b'))]
if __name__ == '__main__':
    _cli_main()
