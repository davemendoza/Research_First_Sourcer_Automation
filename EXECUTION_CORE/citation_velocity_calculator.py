from __future__ import annotations
import csv
import json
import os
from datetime import datetime
from typing import Dict, List, Tuple
PIPELINE_VERSION = 'v2.1.0-citation-velocity'

def run(input_csv: str, output_csv: str) -> None:
    rows, cols = _read_rows(input_csv)
    if not rows:
        _write_header_only(output_csv, cols)
        return
    required = ['Citation_Count_Raw', 'Normalized_Citation_Count', 'Citations_per_Year', 'Citation_Velocity_3yr', 'Citation_Velocity_5yr', 'Citation_Provenance']
    for c in required:
        if c not in cols:
            cols.append(c)
    out_rows: List[Dict[str, str]] = []
    for r in rows:
        rr = dict(r)
        raw = _to_int(rr.get('Citation_Count_Raw', ''))
        norm = raw
        rr['Normalized_Citation_Count'] = str(norm) if norm is not None else ''
        rr['Citation_Provenance'] = (rr.get('Citation_Provenance') or '').strip() or 'Computed from Citation_Count_Raw (deterministic).'
        c3, c5, cpy, prov_extra = _compute_velocities_from_optional_hist(rr)
        if cpy is not None:
            rr['Citations_per_Year'] = _fmt_float(cpy)
        if c3 is not None:
            rr['Citation_Velocity_3yr'] = _fmt_float(c3)
        if c5 is not None:
            rr['Citation_Velocity_5yr'] = _fmt_float(c5)
        if prov_extra:
            rr['Citation_Provenance'] = rr['Citation_Provenance'] + ' ' + prov_extra
        out_rows.append(rr)
    _write_rows(output_csv, out_rows, cols)

def _compute_velocities_from_optional_hist(r: Dict[str, str]) -> Tuple[float | None, float | None, float | None, str]:
    """
    Looks for a yearly citation histogram JSON in these fields:
      - Graph_Evidence_JSON
      - Evidence_Tier_Ledger_JSON
    Expected shape (example):
      {"citations_by_year": {"2021": 12, "2022": 30, "2023": 44, "2024": 50}}
    If missing, returns (None, None, None, "").
    """
    hist = None
    for field in ('Graph_Evidence_JSON', 'Evidence_Tier_Ledger_JSON'):
        blob = (r.get(field) or '').strip()
        if not blob:
            continue
        try:
            data = json.loads(blob)
            if isinstance(data, dict) and isinstance(data.get('citations_by_year'), dict):
                hist = data.get('citations_by_year')
                break
        except Exception:
            continue
    if not isinstance(hist, dict) or not hist:
        return (None, None, None, '')
    by_year: Dict[int, int] = {}
    for k, v in hist.items():
        try:
            y = int(str(k))
            by_year[y] = int(v)
        except Exception:
            continue
    if not by_year:
        return (None, None, None, '')

    def sum_years(n: int) -> int:
        years = list(range(NOW_YEAR - n + 1, NOW_YEAR + 1))
        return sum((by_year.get(y, 0) for y in years))
    s3 = sum_years(3)
    s5 = sum_years(5)
    v3 = s3 / 3.0
    v5 = s5 / 5.0
    min_year = min(by_year.keys())
    span = max(1, NOW_YEAR - min_year + 1)
    total = sum(by_year.values())
    cpy = total / float(span)
    prov = 'Velocities computed from citations_by_year histogram (deterministic).'
    return (v3, v5, cpy, prov)

def _to_int(v: str) -> int | None:
    s = (v or '').strip()
    if not s:
        return None
    try:
        return int(float(s))
    except Exception:
        return None

def _fmt_float(x: float) -> str:
    return f'{x:.2f}'

def _read_rows(path: str) -> Tuple[List[Dict[str, str]], List[str]]:
    if not path or not os.path.exists(path):
        return ([], [])
    with open(path, 'r', encoding='utf-8-sig', newline='') as f:
        reader = csv.DictReader(f)
        cols = list(reader.fieldnames or [])
        if not cols:
            return ([], [])
        rows: List[Dict[str, str]] = []
        for row in reader:
            if row and any(((vv or '').strip() for vv in row.values())):
                rows.append({k: v if v is not None else '' for k, v in row.items()})
        return (rows, cols)

def _write_header_only(path: str, cols: List[str]) -> None:
    _write_rows(path, [], cols)

def _write_rows(path: str, rows: List[Dict[str, str]], cols: List[str]) -> None:
    os.makedirs(os.path.dirname(path) or '.', exist_ok=True)
    with open(path, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=cols, extrasaction='ignore')
        writer.writeheader()
        for r in rows:
            writer.writerow({c: '' if r.get(c) is None else str(r.get(c, '')) for c in cols})

def _cli_main():
    NOW_YEAR = datetime.utcnow().year
if __name__ == '__main__':
    _cli_main()
