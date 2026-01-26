"""
EXECUTION_CORE/production_research_classifier.py
============================================================
PRODUCTION VS RESEARCH CLASSIFIER (Sample.xlsx Gold Standard)

Maintainer: L. David Mendoza © 2026
Version: v1.0.0 (Autogen rebuild, best-in-class)

Mission:
Classify each row as:
- Research
- Production
- Hybrid

Evidence-only based on provided row text fields.

Contract:
- classify_production_vs_research(row: dict) -> str
- apply_production_vs_research(rows: list[dict], out_field: str="Production_vs_Research") -> list[dict]

Safety:
- No network calls
- Deterministic
- No fabrication

Validation:
python3 -m py_compile EXECUTION_CORE/_AUTOGEN_STAGING/production_research_classifier.py

Git:
git add EXECUTION_CORE/production_research_classifier.py
git commit -m "Add production vs research classifier (Sample.xlsx gold standard)"
git push
"""
from __future__ import annotations
import json
import re
from typing import Any, Dict, List
_VERSION = 'v1.0.0'

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
    preferred = ['Production_vs_Research', 'Downstream_Adoption_Signal', 'Open_Source_Impact_Note', 'GitHub_Repo_Evidence_Why', 'Repo_Readme_Text', 'Repo_README_Text', 'Repo_Text', 'Publications_Text', 'Scholar_Abstracts', 'Paper_Abstracts', 'Experience', 'Summary', 'Title', 'Headline', 'Strengths']
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
_RESEARCH_CUES = ['arxiv', 'neurips', 'iclr', 'icml', 'acl', 'emnlp', 'naacl', 'cvpr', 'eccv', 'iccv', 'workshop', 'paper', 'preprint', 'theorem', 'proof', 'ablation', 'benchmark', 'evaluation', 'mmlu', 'humaneval', 'hellaswag', 'mt-bench', 'big-bench']
_PRODUCTION_CUES = ['production', 'in production', 'deployed', 'deployment', 'serving', 'inference service', 'slo', 'sla', 'oncall', 'observability', 'monitoring', 'latency', 'throughput', 'scaling', 'kubernetes', 'k8s', 'helm', 'terraform', 'aws', 'gcp', 'azure', 'sagemaker', 'vertex ai', 'ray serve', 'triton', 'tensorrt', 'onnxruntime', 'customer', 'enterprise', 'integration', 'forward deployed', 'fdse', 'fwd deployed']

def classify_production_vs_research(row: Dict[str, Any]) -> str:
    text = _collect_text(row)
    research_hits = sum((1 for t in _RESEARCH_CUES if t in text))
    prod_hits = sum((1 for t in _PRODUCTION_CUES if t in text))
    out = ''
    if research_hits == 0 and prod_hits == 0:
        out = ''
    elif research_hits > 0 and prod_hits > 0:
        out = 'Hybrid' if research_hits + prod_hits >= 2 else ''
    else:
        out = 'Research' if research_hits > prod_hits else 'Production'
    if 'Field_Level_Provenance_JSON' in row:
        _augment_provenance(row, 'Production_vs_Research', out, {'research_hits': research_hits, 'prod_hits': prod_hits})
    return out

def _augment_provenance(row: Dict[str, Any], field: str, value: Any, detail: Dict[str, Any]) -> None:
    raw = _safe_str(row.get('Field_Level_Provenance_JSON', '')).strip()
    obj: Dict[str, Any] = {}
    if raw:
        try:
            obj = json.loads(raw)
            if not isinstance(obj, dict):
                obj = {}
        except Exception:
            obj = {}
    obj[field] = {'version': _VERSION, 'evidence_basis': 'row_text_fields_only', 'value': value, 'detail': detail}
    row['Field_Level_Provenance_JSON'] = json.dumps(obj, sort_keys=True)

def apply_production_vs_research(rows: List[Dict[str, Any]], out_field: str='Production_vs_Research') -> List[Dict[str, Any]]:
    for r in rows:
        c = classify_production_vs_research(r)
        if c:
            r[out_field] = c
        else:
            r[out_field] = r.get(out_field, '')
    return rows
__all__ = ['classify_production_vs_research', 'apply_production_vs_research']

def _cli_main():
    _WS_RE = re.compile('\\s+', re.UNICODE)
if __name__ == '__main__':
    _cli_main()
