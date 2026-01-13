#!/usr/bin/env python3
"""
phase7_oss_contribution_intel.py
------------------------------------------------------------
Version: v7.0.0
Author: © 2026 L. David Mendoza

Purpose
- Phase 7: Open-Source Contribution Intelligence (deterministic, evidence-only).
- Extract OSS contribution signals from already-present evidence fields (no network calls).
- Adds Phase 7 columns if missing. Never overwrites populated Phase 7 fields.

Inputs
- CSV rows containing evidence fields such as:
  - GitHub_URL, GitHub_Username, GitHub_Repo_Text, GitHub_Readme_Text
  - Any repo list / evidence blobs already harvested upstream
  - Notes / Summary / Skills etc. (best-effort)

Outputs (additive, no overwrites):
- OSS_Repos_Relevant (pipe)
- OSS_AI_Frameworks (pipe)
- OSS_Contribution_Strength (single: High/Medium/Low/None)
- OSS_Signal_Tier (single: Hardcore/Applied/Generic/None)
- OSS_Evidence_Summary (single sentence, evidence-only)

Validation Steps
1) Self-test:
   python3 EXECUTION_CORE/phase7_oss_contribution_intel.py --self-test

2) Apply to CSV:
   python3 EXECUTION_CORE/phase7_oss_contribution_intel.py input.csv output.csv

Git Commands
git add SCHEMA/oss_contribution_taxonomy.json EXECUTION_CORE/phase7_oss_contribution_intel.py
git commit -m "Phase 7: add deterministic OSS contribution intelligence (taxonomy-driven)"
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


PHASE7_COLUMNS: Tuple[str, ...] = (
    "OSS_Repos_Relevant",
    "OSS_AI_Frameworks",
    "OSS_Contribution_Strength",
    "OSS_Signal_Tier",
    "OSS_Evidence_Summary",
)

DEFAULT_TAXONOMY_PATH = Path("SCHEMA") / "oss_contribution_taxonomy.json"


def _non_empty(v: str) -> bool:
    return bool(v and str(v).strip())


def _norm_space(s: str) -> str:
    return re.sub(r"\s+", " ", (s or "").strip())


def _split_pipe(v: str) -> List[str]:
    return [x.strip() for x in (v or "").split("|") if x.strip()]


def _join_pipe_unique(items: List[str]) -> str:
    dedup = sorted({x.strip() for x in items if x and x.strip()})
    return "|".join(dedup)


def load_taxonomy(path: Path) -> Dict:
    if not path.exists():
        raise FileNotFoundError(f"Missing taxonomy file: {path}")
    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)
    return data


def _compile_patterns(items: List[Dict]) -> List[Tuple[str, List[re.Pattern]]]:
    compiled: List[Tuple[str, List[re.Pattern]]] = []
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
                continue
        if regs:
            compiled.append((canonical, regs))
    return compiled


def _match_any(text: str, regs: List[re.Pattern]) -> bool:
    return any(r.search(text) for r in regs)


def _safe_text_from_row(row: Dict[str, str], fields: List[str]) -> str:
    parts: List[str] = []
    for f in fields:
        v = row.get(f, "")
        if _non_empty(v):
            parts.append(str(v))
    return _norm_space(" ".join(parts))


def _tier_from_keywords(text: str, tax: Dict) -> str:
    tiers = tax.get("tiers", {})
    hardcore = tiers.get("hardcore", {}).get("keywords", [])
    applied = tiers.get("applied", {}).get("keywords", [])
    generic = tiers.get("generic", {}).get("keywords", [])

    t = text.lower()

    def hit(keys: List[str]) -> bool:
        for k in keys:
            if k and k.lower() in t:
                return True
        return False

    if hit(hardcore):
        return "Hardcore"
    if hit(applied):
        return "Applied"
    if hit(generic):
        return "Generic"
    return "None"


def _strength_from_density(framework_count: int, repo_relevance_count: int, tier: str) -> str:
    """
    Deterministic rule:
    - High: Hardcore tier AND (>=2 frameworks OR >=2 relevance hits)
    - Medium: Applied tier AND (>=1 framework OR >=1 relevance hit)
    - Low: Generic tier AND (>=1 framework OR >=1 relevance hit)
    - None: otherwise
    """
    if tier == "Hardcore" and (framework_count >= 2 or repo_relevance_count >= 2):
        return "High"
    if tier == "Applied" and (framework_count >= 1 or repo_relevance_count >= 1):
        return "Medium"
    if tier == "Generic" and (framework_count >= 1 or repo_relevance_count >= 1):
        return "Low"
    return "None"


def _extract_frameworks(text: str, compiled_frameworks: List[Tuple[str, List[re.Pattern]]]) -> List[str]:
    found: List[str] = []
    for canonical, regs in compiled_frameworks:
        if _match_any(text, regs):
            found.append(canonical)
    return sorted(set(found))


def _extract_repo_relevance(text: str, compiled_relevance: List[Tuple[str, List[re.Pattern]]]) -> List[str]:
    found: List[str] = []
    for canonical, regs in compiled_relevance:
        if _match_any(text, regs):
            found.append(canonical)
    return sorted(set(found))


def _extract_repo_names_best_effort(text: str) -> List[str]:
    """
    Best-effort repo token extraction from evidence blobs.
    No network calls. No assumptions.
    Looks for patterns like:
      - owner/repo
      - github.com/owner/repo
    """
    repos: List[str] = []
    for m in re.findall(r"\bgithub\.com/([A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+)\b", text, flags=re.I):
        repos.append(m.strip())
    for m in re.findall(r"\b([A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+)\b", text):
        # avoid obvious false positives
        if m.count("/") == 1 and len(m) <= 80 and "." not in m.split("/")[0]:
            repos.append(m.strip())
    # keep only plausible and unique, cap to avoid runaway
    dedup = []
    seen = set()
    for r in repos:
        if r.lower() in seen:
            continue
        seen.add(r.lower())
        dedup.append(r)
        if len(dedup) >= 25:
            break
    return dedup


def ensure_columns(fieldnames: List[str]) -> List[str]:
    existing = list(fieldnames or [])
    for c in PHASE7_COLUMNS:
        if c not in existing:
            existing.append(c)
    return existing


def enrich_row_in_place(row: Dict[str, str], tax: Dict) -> None:
    # Do not overwrite populated Phase 7 outputs
    if any(_non_empty(row.get(c, "")) for c in PHASE7_COLUMNS):
        return

    evidence_fields = [
        "GitHub_URL",
        "GitHub_Username",
        "GitHub_Bio",
        "GitHub_Repo_Text",
        "GitHub_Readme_Text",
        "Personal_Site_Text",
        "Summary",
        "Skills",
        "Skills2",
        "Experience",
        "Notes",
    ]
    text = _safe_text_from_row(row, evidence_fields)

    compiled_frameworks = _compile_patterns(tax.get("frameworks", []))
    compiled_relevance = _compile_patterns(tax.get("repo_relevance_patterns", []))

    frameworks = _extract_frameworks(text, compiled_frameworks)
    relevance_hits = _extract_repo_relevance(text, compiled_relevance)
    repos = _extract_repo_names_best_effort(text)

    tier = _tier_from_keywords(text, tax)
    strength = _strength_from_density(len(frameworks), len(relevance_hits), tier)

    row["OSS_AI_Frameworks"] = _join_pipe_unique(frameworks)
    row["OSS_Repos_Relevant"] = _join_pipe_unique(repos)
    row["OSS_Signal_Tier"] = tier
    row["OSS_Contribution_Strength"] = strength

    # Evidence-only summary (no inference)
    bits: List[str] = []
    if frameworks:
        bits.append(f"Frameworks: {', '.join(frameworks[:6])}")
    if relevance_hits:
        bits.append(f"Signals: {', '.join(relevance_hits[:4])}")
    if repos:
        bits.append(f"Repos: {', '.join(repos[:3])}")
    if not bits:
        row["OSS_Evidence_Summary"] = ""
    else:
        row["OSS_Evidence_Summary"] = _norm_space("; ".join(bits))

    # If everything is empty, normalize tier/strength to None
    if not frameworks and not relevance_hits and not repos:
        row["OSS_Signal_Tier"] = "None"
        row["OSS_Contribution_Strength"] = "None"


def process_csv(input_csv: Path, output_csv: Path, taxonomy_path: Path) -> None:
    tax = load_taxonomy(taxonomy_path)

    with input_csv.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        fieldnames = ensure_columns(reader.fieldnames or [])
        rows = list(reader)

    for row in rows:
        enrich_row_in_place(row, tax)

    with output_csv.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def self_test(taxonomy_path: Path) -> int:
    try:
        tax = load_taxonomy(taxonomy_path)
        sample = "github.com/org/vllm text-generation-inference CUDA Triton LangChain RAG FAISS Kubernetes"
        compiled_frameworks = _compile_patterns(tax.get("frameworks", []))
        compiled_relevance = _compile_patterns(tax.get("repo_relevance_patterns", []))

        fws = _extract_frameworks(sample, compiled_frameworks)
        rel = _extract_repo_relevance(sample, compiled_relevance)
        repos = _extract_repo_names_best_effort(sample)
        tier = _tier_from_keywords(sample, tax)
        strength = _strength_from_density(len(fws), len(rel), tier)

        if not fws or not rel or tier == "None" or strength == "None":
            print("FAIL: self-test did not detect expected OSS signals", file=sys.stderr)
            return 2
        if not repos:
            print("FAIL: self-test did not extract repo token(s)", file=sys.stderr)
            return 3

        print("OK: self-test passed")
        return 0
    except Exception as e:
        print(f"FAIL: self-test error: {e}", file=sys.stderr)
        return 1


def main() -> int:
    ap = argparse.ArgumentParser(description="Phase 7: deterministic OSS contribution intelligence (taxonomy-driven).")
    ap.add_argument("input_csv", nargs="?", help="Input CSV path")
    ap.add_argument("output_csv", nargs="?", help="Output CSV path")
    ap.add_argument("--taxonomy", default=str(DEFAULT_TAXONOMY_PATH), help="Taxonomy JSON path")
    ap.add_argument("--self-test", action="store_true", help="Run self-test and exit")
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
