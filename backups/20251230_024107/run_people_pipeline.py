#!/usr/bin/env python3
"""
AI Talent Engine – Run People Pipeline (Ultra)
Version: v1.0.0-ultra
Date: 2025-12-30
© 2025 L. David Mendoza. All Rights Reserved.

ENTRYPOINT
One command creates interview-ready people outputs:
- people_master.csv
- people_provenance.csv

HOW IT WORKS
- Reads scenario_control_matrix.xlsx if present, otherwise falls back to scenario_enumerator_map.yaml strategies.
- Enumerates people via:
  - OpenAlex (always)
  - GitHub (if GITHUB_TOKEN is provided, otherwise still runs limited)
  - Patents (only if explicit patent URLs are present)
- Resolves identities across sources
- Scores deterministically
- Enforces guardrails (no empty, no weak yields)
"""

from __future__ import annotations

import argparse
import os
import sys
import csv
from datetime import datetime
from typing import Dict, List

import yaml
import pandas as pd

from enumerator_openalex import enumerate_people_from_topics as oa_enum
from enumerator_github import enumerate_people_from_topics as gh_enum
from enumerator_patents import extract_inventors as pat_enum
from people_resolver import resolve_people
from people_scorer import score_people
from people_quality_guardrails import GuardrailConfig, validate_scenario_yields, validate_total_people, validate_evidence_urls

def _load_yaml(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def _write_csv(path: str, rows: List[dict], fieldnames: List[str]) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for r in rows:
            w.writerow(r)

def _infer_strategy(s: str, mapping: dict) -> str:
    s = (s or "").strip()
    aliases = mapping.get("scenario_aliases", {}) or {}
    if s in aliases:
        return aliases[s]
    # heuristic fallback
    sl = s.lower()
    if "infra" in sl or "gpu" in sl or "distributed" in sl:
        return "INFRA"
    if "applied" in sl or "rag" in sl or "vector" in sl:
        return "APPLIED"
    if "health" in sl or "clinical" in sl or "bio" in sl:
        return "HEALTHCARE"
    if "robot" in sl or "autonomy" in sl:
        return "ROBOTICS"
    return "FOUNDATIONAL"

def _load_scenarios_from_excel(xlsx_path: str) -> List[str]:
    # Minimal assumption: sheet contains a column named "scenario" or similar.
    # If not found, fallback to a single default scenario.
    try:
        df = pd.read_excel(xlsx_path)
        cols = [c.lower().strip() for c in df.columns]
        df.columns = cols
        for c in ["scenario", "scenario_name", "name"]:
            if c in df.columns:
                vals = [str(x).strip() for x in df[c].dropna().tolist() if str(x).strip()]
                return list(dict.fromkeys(vals))
    except Exception:
        pass
    return ["FOUNDATIONAL_DEFAULT"]

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--max-total", type=int, default=2000)
    ap.add_argument("--openalex-per-scenario", type=int, default=250)
    ap.add_argument("--github-per-scenario", type=int, default=200)
    ap.add_argument("--min-per-scenario", type=int, default=120)
    ap.add_argument("--min-total", type=int, default=600)
    ap.add_argument("--outdir", default="output/people")
    args = ap.parse_args()

    if not os.path.exists("scenario_enumerator_map.yaml"):
        print("❌ Missing scenario_enumerator_map.yaml")
        return 2

    mapping = _load_yaml("scenario_enumerator_map.yaml")
    defaults = mapping.get("defaults", {}) or {}
    strategies = mapping.get("strategies", {}) or {}

    guard_cfg = GuardrailConfig(
        min_people_per_scenario=int(args.min_per_scenario),
        min_people_total=int(args.min_total),
        require_evidence_urls=bool(defaults.get("require_evidence_urls", True)),
    )

    scenarios = []
    if os.path.exists("scenario_control_matrix.xlsx"):
        scenarios = _load_scenarios_from_excel("scenario_control_matrix.xlsx")
    if not scenarios:
        scenarios = list((mapping.get("scenario_aliases", {}) or {}).keys()) or ["FOUNDATIONAL_DEFAULT"]

    run_ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_base = os.path.join(args.outdir, run_ts)
    os.makedirs(out_base, exist_ok=True)

    raw_people: List[dict] = []
    provenance: List[dict] = []
    scenario_yields: Dict[str, int] = {}

    total_cap = int(args.max_total)

    for sc in scenarios:
        if len(raw_people) >= total_cap:
            break

        strat = _infer_strategy(sc, mapping)
        strat_obj = strategies.get(strat, {}) or {}
        enumerators = strat_obj.get("enumerators", ["openalex"]) or ["openalex"]

        topics_oa = strat_obj.get("openalex_topics", []) or []
        topics_gh = strat_obj.get("github_topics", []) or []

        people_sc: List[dict] = []

        if "openalex" in enumerators:
            oa_target = int(args.openalex_per_scenario)
            people_sc.extend(oa_enum(topics_oa or [strat], per_scenario_target=oa_target))

        if "github" in enumerators:
            gh_target = int(args.github_per_scenario)
            people_sc.extend(gh_enum(topics_gh or [strat], per_scenario_target=gh_target))

        # Patents enumerator is only used when a patent URL appears inside the mapping topics (rare).
        # It exists for completeness, not volume. If you want it, add patent URLs into topics_oa.
        for t in (topics_oa or []):
            if "patents.google.com/patent/" in t:
                people_sc.extend(pat_enum(t))

        # Attach scenario tags and provenance
        for p in people_sc:
            p["scenario_tags"] = list(dict.fromkeys((p.get("scenario_tags") or []) + [sc]))
            raw_people.append(p)
            provenance.append({
                "scenario": sc,
                "strategy": strat,
                "source_systems": ",".join(p.get("source_systems", [])),
                "full_name": p.get("full_name", ""),
                "primary_affiliation": p.get("primary_affiliation", ""),
                "evidence_urls": "|".join(p.get("evidence_urls", [])[:10]),
                "openalex_author_id": p.get("openalex_author_id", ""),
                "github_login": p.get("github_login", ""),
            })
            if len(raw_people) >= total_cap:
                break

        scenario_yields[sc] = len(people_sc)

    # Resolve and score
    resolved = resolve_people(raw_people)
    scored = score_people(resolved)

    # Final contract rows
    people_rows = []
    for p in scored:
        people_rows.append({
            "person_id": p.get("person_id", ""),
            "full_name": p.get("full_name", ""),
            "primary_affiliation": p.get("primary_affiliation", ""),
            "role_cluster": p.get("role_hint", ""),
            "scenario_tags": "|".join(sorted(set(p.get("scenario_tags") or []))),
            "source_systems": "|".join(sorted(set(p.get("source_systems") or []))),
            "evidence_urls": "|".join(p.get("evidence_urls") or []),
            "signal_score": p.get("signal_score", 0.0),
            "first_seen_utc": run_ts,
            "last_seen_utc": run_ts,
        })

    # Guardrails
    validate_scenario_yields(scenario_yields, guard_cfg)
    validate_total_people(len(people_rows), guard_cfg)
    validate_evidence_urls(people_rows, guard_cfg)

    people_path = os.path.join(out_base, "people_master.csv")
    prov_path = os.path.join(out_base, "people_provenance.csv")

    _write_csv(
        people_path,
        people_rows,
        fieldnames=[
            "person_id","full_name","primary_affiliation","role_cluster",
            "scenario_tags","source_systems","evidence_urls","signal_score",
            "first_seen_utc","last_seen_utc"
        ],
    )

    _write_csv(
        prov_path,
        provenance,
        fieldnames=[
            "scenario","strategy","source_systems","full_name","primary_affiliation",
            "evidence_urls","openalex_author_id","github_login"
        ],
    )

    print("")
    print("✅ PEOPLE PIPELINE COMPLETE")
    print(f"people_master.csv: {people_path}")
    print(f"people_provenance.csv: {prov_path}")
    print(f"Total people (unique): {len(people_rows)}")
    print("")
    print("Next:")
    print(f"open '{out_base}'")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
