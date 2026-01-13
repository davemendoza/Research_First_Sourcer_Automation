#!/usr/bin/env python3
"""
phase6_ai_stack_signals.py
------------------------------------------------------------
Version: v6.0.0
Author: © 2026 L. David Mendoza

Purpose
- Phase 6: Deterministic Deep AI Stack Signal Extraction
- Extract explicit AI stack signals from existing evidence-only text fields.
- No network calls. No inference. No fabrication.
- Adds Phase 6 columns if missing. Never overwrites populated Phase 6 fields.

Inputs
- CSV rows containing any subset of evidence-bearing fields (bio, summary, skills, repo text, notes, etc.).

Outputs
- Adds (pipe-delimited, unique, sorted) columns:
  - LLM_Names
  - VectorDB_Tech
  - RAG_Stack
  - Inference_Stack
  - Optimization_Tech
  - GPU_Infra_Signals

Changelog
- v6.0.0: Initial Phase 6 extractor with taxonomy-driven regex matching, additive writeback, no overwrites.

Validation Steps
1) Unit sanity on taxonomy load:
   python3 EXECUTION_CORE/phase6_ai_stack_signals.py --self-test

2) Apply to a CSV (no overwrites of populated fields):
   python3 EXECUTION_CORE/phase6_ai_stack_signals.py input.csv output.csv

Git Commands
git add SCHEMA/ai_stack_taxonomy.json EXECUTION_CORE/phase6_ai_stack_signals.py
git commit -m "Phase 6: add deterministic AI stack signal extraction (taxonomy-driven)"
git push
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from pathlib import Path
from typing import Dict, List, Tuple


PHASE6_COLUMNS: Tuple[str, ...] = (
    "LLM_Names",
    "VectorDB_Tech",
    "RAG_Stack",
    "Inference_Stack",
    "Optimization_Tech",
    "GPU_Infra_Signals",
)

DEFAULT_TAXONOMY_PATH = Path("SCHEMA") / "ai_stack_taxonomy.json"


def _non_empty(v: str) -> bool:
    return bool(v and str(v).strip())


def _norm_space(s: str) -> str:
    return re.sub(r"\s+", " ", (s or "").strip())


def _split_pipe(v: str) -> List[str]:
    return [x.strip() for x in (v or "").split("|") if x.strip()]


def _join_pipe_unique(items: List[str]) -> str:
    dedup = sorted({x.strip() for x in items if x and x.strip()})
    return "|".join(dedup)


def _safe_text_from_row(row: Dict[str, str], candidate_fields: List[str]) -> str:
    parts: List[str] = []
    for f in candidate_fields:
        val = row.get(f, "")
        if _non_empty(val):
            parts.append(str(val))
    return _norm_space(" ".join(parts))


def load_taxonomy(tax_path: Path) -> Dict:
    if not tax_path.exists():
        raise FileNotFoundError(f"Missing taxonomy file: {tax_path}")
    with tax_path.open("r", encoding="utf-8") as f:
        data = json.load(f)
    if "categories" not in data:
        raise ValueError("Taxonomy missing required key: categories")
    return data


def compile_taxonomy(tax: Dict) -> Dict[str, List[Tuple[str, List[re.Pattern]]]]:
    compiled: Dict[str, List[Tuple[str, List[re.Pattern]]]] = {}
    for cat in tax.get("categories", []):
        name = cat.get("name")
        items = cat.get("items", [])
        if not name or not isinstance(items, list):
            continue
        compiled[name] = []
        for it in items:
            canonical = it.get("canonical")
            patterns = it.get("patterns", [])
            if not canonical or not isinstance(patterns, list) or not patterns:
                continue
            regs: List[re.Pattern] = []
            for p in patterns:
                try:
                    regs.append(re.compile(p, flags=re.IGNORECASE))
                except re.error:
                    # Fail closed in development mode; in production we skip invalid patterns
                    continue
            if regs:
                compiled[name].append((canonical, regs))
    return compiled


def extract_signals(text: str, compiled: Dict[str, List[Tuple[str, List[re.Pattern]]]]) -> Dict[str, List[str]]:
    found: Dict[str, List[str]] = {k: [] for k in PHASE6_COLUMNS}
    if not text:
        return found

    for category_name in PHASE6_COLUMNS:
        rules = compiled.get(category_name, [])
        for canonical, regs in rules:
            if any(r.search(text) for r in regs):
                found[category_name].append(canonical)

    return found


def enrich_row_in_place(
    row: Dict[str, str],
    compiled: Dict[str, List[Tuple[str, List[re.Pattern]]]],
    evidence_fields: List[str],
) -> None:
    """
    Additive enrichment:
    - Detect signals from evidence_fields (existing row text only)
    - Write to PHASE6_COLUMNS only if target field is empty
    - Never overwrite populated Phase 6 fields
    """
    text = _safe_text_from_row(row, evidence_fields)
    signals = extract_signals(text, compiled)

    for col in PHASE6_COLUMNS:
        if _non_empty(row.get(col, "")):
            continue
        row[col] = _join_pipe_unique(signals.get(col, []))


def ensure_columns(fieldnames: List[str]) -> List[str]:
    existing = list(fieldnames or [])
    for col in PHASE6_COLUMNS:
        if col not in existing:
            existing.append(col)
    return existing


def process_csv(input_csv: Path, output_csv: Path, taxonomy_path: Path) -> None:
    tax = load_taxonomy(taxonomy_path)
    compiled = compile_taxonomy(tax)

    with input_csv.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        fieldnames = ensure_columns(reader.fieldnames or [])
        rows = list(reader)

    # Evidence-bearing columns (best-effort, no assumptions)
    evidence_fields = [
        "Full_Name",
        "Headline",
        "Title",
        "Summary",
        "Skills",
        "Skills2",
        "Experience",
        "Strengths",
        "Weaknesses",
        "GitHub_Bio",
        "GitHub_Repo_Text",
        "GitHub_Readme_Text",
        "Personal_Site_Text",
        "Notes",
    ]

    for row in rows:
        enrich_row_in_place(row, compiled, evidence_fields)

    with output_csv.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def self_test(taxonomy_path: Path) -> int:
    try:
        tax = load_taxonomy(taxonomy_path)
        compiled = compile_taxonomy(tax)
        # Ensure all Phase 6 columns exist in compiled taxonomy
        missing = [c for c in PHASE6_COLUMNS if c not in compiled]
        if missing:
            print(f"FAIL: taxonomy missing categories: {missing}", file=sys.stderr)
            return 2

        sample = "GPT-4 RAG LangChain FAISS vLLM TensorRT-LLM CUDA Kubernetes FlashAttention"
        signals = extract_signals(sample, compiled)
        for col in PHASE6_COLUMNS:
            if not signals.get(col):
                print(f"FAIL: no signals found for column {col} on sample", file=sys.stderr)
                return 3

        print("OK: self-test passed")
        return 0
    except Exception as e:
        print(f"FAIL: self-test error: {e}", file=sys.stderr)
        return 1


def main() -> int:
    ap = argparse.ArgumentParser(description="Phase 6: deterministic AI stack signal extraction (taxonomy-driven).")
    ap.add_argument("input_csv", nargs="?", help="Input CSV path")
    ap.add_argument("output_csv", nargs="?", help="Output CSV path")
    ap.add_argument("--taxonomy", default=str(DEFAULT_TAXONOMY_PATH), help="Taxonomy JSON path")
    ap.add_argument("--self-test", action="store_true", help="Run taxonomy self-test and exit")

    args = ap.parse_args()
    taxonomy_path = Path(args.taxonomy)

    if args.self_test:
        return self_test(taxonomy_path)

    if not args.input_csv or not args.output_csv:
        ap.print_help()
        return 2

    input_csv = Path(args.input_csv)
    output_csv = Path(args.output_csv)

    if not input_csv.exists():
        print(f"ERROR: input CSV not found: {input_csv}", file=sys.stderr)
        return 2

    process_csv(input_csv, output_csv, taxonomy_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
