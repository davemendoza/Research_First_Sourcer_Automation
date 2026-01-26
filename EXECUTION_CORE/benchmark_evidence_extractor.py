"""
EXECUTION_CORE/benchmark_evidence_extractor.py
============================================================
BENCHMARK EVIDENCE EXTRACTOR (Sample.xlsx Gold Standard)

Maintainer: L. David Mendoza © 2026
Version: v1.0.0 (Autogen rebuild, best-in-class)

Mission:
Populate Sample.xlsx-style Benchmarks_Worked_On based on explicit benchmark evidence
present in provided row text. Evidence-only, no guessing.

Canonical benchmark set:
- MT-Bench
- BIG-Bench
- HellaSwag
- HumanEval
- MMLU
- SWE-bench
- Arena Elo

Contract:
- extract_benchmarks_worked_on(row: dict) -> list[str]
- apply_benchmarks_worked_on(rows: list[dict], out_field: str="Benchmarks_Worked_On") -> list[dict]

Safety:
- No network calls
- Deterministic
- No fabrication

Validation:
python3 -m py_compile EXECUTION_CORE/_AUTOGEN_STAGING/benchmark_evidence_extractor.py

Git:
git add EXECUTION_CORE/benchmark_evidence_extractor.py
git commit -m "Add benchmark evidence extractor (Sample.xlsx gold standard)"
git push
"""
from __future__ import annotations
import json
import re
from typing import Any, Dict, Iterable, List
_VERSION = 'v1.0.0'
_CANONICAL = ['MT-Bench', 'BIG-Bench', 'HellaSwag', 'HumanEval', 'MMLU', 'SWE-bench', 'Arena Elo']
_PATTERNS = {'MT-Bench': ['\\bmt[- ]?bench\\b'], 'BIG-Bench': ['\\bbig[- ]?bench\\b', '\\bbigbench\\b'], 'HellaSwag': ['\\bhellaswag\\b'], 'HumanEval': ['\\bhumaneval\\b', '\\bhuman[- ]?eval\\b'], 'MMLU': ['\\bmmlu\\b'], 'SWE-bench': ['\\bswe[- ]?bench\\b', '\\bswebench\\b'], 'Arena Elo': ['\\barena elo\\b', '\\belo\\b.*\\barena\\b', '\\blmsys\\b.*\\barena\\b']}

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
    preferred = ['Benchmarks_Worked_On', 'Repo_Readme_Text', 'Repo_README_Text', 'Repo_Text', 'Repo_Topics_Keywords', 'GitHub_Repo_Evidence_Why', 'Open_Source_Impact_Note', 'Publications_Text', 'Scholar_Abstracts', 'Paper_Abstracts', 'Citations_Text', 'Summary', 'Experience', 'Skills', 'Skills2', 'Headline', 'Title']
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

def _matches_any(text: str, regexes: Iterable[str]) -> bool:
    for rx in regexes:
        try:
            if re.search(rx, text, flags=re.IGNORECASE):
                return True
        except Exception:
            continue
    return False

def extract_benchmarks_worked_on(row: Dict[str, Any]) -> List[str]:
    text = _collect_text(row)
    found: List[str] = []
    reasons: Dict[str, str] = {}
    for name in _CANONICAL:
        if _matches_any(text, _PATTERNS.get(name, [])):
            found.append(name)
            reasons[name] = 'matched benchmark token in row evidence text'
    found = [x for x in _CANONICAL if x in set(found)]
    if 'Field_Level_Provenance_JSON' in row:
        _augment_provenance(row, 'Benchmarks_Worked_On', found, reasons)
    return found

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

def apply_benchmarks_worked_on(rows: List[Dict[str, Any]], out_field: str='Benchmarks_Worked_On') -> List[Dict[str, Any]]:
    for r in rows:
        b = extract_benchmarks_worked_on(r)
        r[out_field] = '; '.join(b) if b else r.get(out_field, '')
    return rows
__all__ = ['extract_benchmarks_worked_on', 'apply_benchmarks_worked_on']

def _cli_main():
    _WS_RE = re.compile('\\s+', re.UNICODE)
if __name__ == '__main__':
    _cli_main()
