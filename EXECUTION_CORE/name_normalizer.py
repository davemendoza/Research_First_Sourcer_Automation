"""
EXECUTION_CORE/name_normalizer.py
============================================================
NAME NORMALIZER AND REAL NAME RESOLUTION (Evidence-only)

Maintainer: L. David Mendoza © 2026
Version: v1.0.0 (Autogen rebuild, best-in-class)

Mission:
Ensure every row has a non-empty Full_Name while never fabricating a real name.

Hierarchy:
1) Use explicit Full_Name if already present (cleaned).
2) Use GitHub profile name fields if present.
3) Use commit author name fields if present.
4) Use email local-part heuristic only if it looks like a human name.
5) Fallback to handle-based name (non-synthetic) derived from GitHub username or seed handle.
   Mark low confidence and record provenance.

Contract:
- resolve_full_name(row: dict) -> dict with:
    Full_Name, First_Name, Last_Name, Name_Source, Name_Confidence
- apply_name_normalization(rows: list[dict]) -> list[dict]

Safety:
- Deterministic
- Evidence-only
- No network calls
- No fabricated identities

Validation:
python3 -m py_compile EXECUTION_CORE/_AUTOGEN_STAGING/name_normalizer.py
"""
from __future__ import annotations
import json
import re
from typing import Any, Dict, List, Tuple
_VERSION = 'v1.0.0'

def _clean(s: str) -> str:
    s = (s or '').strip()
    return _WS_RE.sub(' ', s)

def _safe_str(v: Any) -> str:
    if v is None:
        return ''
    try:
        return str(v)
    except Exception:
        return ''

def _looks_like_human_name(s: str) -> bool:
    s = _clean(s)
    if not s or len(s) < 3:
        return False
    if _BAD_NAME_RE.match(s):
        return False
    if '_' in s:
        return False
    if sum((c.isdigit() for c in s)) >= 2:
        return False
    parts = s.split(' ')
    alpha_parts = [p for p in parts if any((c.isalpha() for c in p))]
    return len(alpha_parts) >= 2

def _split_first_last(full: str) -> Tuple[str, str]:
    parts = _clean(full).split(' ')
    if len(parts) == 1:
        return (parts[0], '')
    return (parts[0], parts[-1])

def _title_case_handle(s: str) -> str:
    s = _safe_str(s).strip().strip('@')
    if not s:
        return ''
    s = s.rstrip('/').split('/')[-1]
    s = re.sub('[_\\-.]+', ' ', s)
    s = re.sub('\\b\\d+\\b', '', s)
    s = _clean(s)
    if not s:
        return ''
    words = []
    for w in s.split(' '):
        if len(w) == 1:
            words.append(w.upper())
        else:
            words.append(w[:1].upper() + w[1:].lower())
    return ' '.join(words)

def resolve_full_name(row: Dict[str, Any]) -> Dict[str, str]:
    out: Dict[str, str] = {}
    existing = _clean(_safe_str(row.get('Full_Name', '')))
    if existing and _looks_like_human_name(existing):
        return _finalize(existing, 'existing_full_name', 'high', row)
    for k in ['GitHub_Profile_Name', 'Github_Profile_Name', 'Profile_Name', 'Name']:
        v = _clean(_safe_str(row.get(k)))
        if v and _looks_like_human_name(v):
            return _finalize(v, f'github_profile:{k}', 'high', row)
    for k in ['Commit_Author_Name', 'CommitAuthorName', 'Author_Name', 'Git_Commit_Author']:
        v = _clean(_safe_str(row.get(k)))
        if v and _looks_like_human_name(v):
            return _finalize(v, f'commit_author:{k}', 'medium', row)
    email = _safe_str(row.get('Primary_Email')) or _safe_str(row.get('Email'))
    if '@' in email:
        local = email.split('@', 1)[0]
        guess = _title_case_handle(local)
        if _looks_like_human_name(guess):
            return _finalize(guess, 'email_localpart', 'low', row)
    handle = _safe_str(row.get('GitHub_Username')) or _safe_str(row.get('Github_Username')) or _safe_str(row.get('Seed_Query_Or_Handle')) or _safe_str(row.get('Handle')) or _safe_str(row.get('GitHub_URL'))
    fallback = _title_case_handle(handle)
    if not fallback:
        fallback = _safe_str(row.get('Person_ID')) or 'Unknown'
    return _finalize(fallback, 'handle_fallback', 'low', row)

def _finalize(full: str, source: str, confidence: str, row: Dict[str, Any]) -> Dict[str, str]:
    first, last = _split_first_last(full)
    result = {'Full_Name': full, 'First_Name': first, 'Last_Name': last, 'Name_Source': source, 'Name_Confidence': confidence}
    _attach_provenance(row, result)
    return result

def _attach_provenance(row: Dict[str, Any], resolved: Dict[str, str]) -> None:
    key = 'Field_Level_Provenance_JSON'
    raw = _safe_str(row.get(key))
    obj: Dict[str, Any] = {}
    if raw:
        try:
            obj = json.loads(raw)
            if not isinstance(obj, dict):
                obj = {}
        except Exception:
            obj = {}
    obj['Full_Name'] = {'version': _VERSION, 'source': resolved.get('Name_Source'), 'confidence': resolved.get('Name_Confidence'), 'value': resolved.get('Full_Name'), 'evidence_basis': 'row_fields_only'}
    row[key] = json.dumps(obj, sort_keys=True)

def apply_name_normalization(rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    for r in rows:
        resolved = resolve_full_name(r)
        for k, v in resolved.items():
            r[k] = v
    return rows
__all__ = ['resolve_full_name', 'apply_name_normalization']

def _cli_main():
    _WS_RE = re.compile('\\s+', re.UNICODE)
    _BAD_NAME_RE = re.compile('^[\\W_]+$', re.UNICODE)
if __name__ == '__main__':
    _cli_main()
