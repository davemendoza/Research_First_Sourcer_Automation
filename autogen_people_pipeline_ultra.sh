#!/usr/bin/env bash
set -euo pipefail

ROOT="$(pwd)"
REQ_FILES=(
  "scenario_control_matrix.xlsx"
  "scenario_enumerator_map.yaml"
  "run_people_pipeline.py"
  "enumerator_openalex.py"
  "enumerator_github.py"
  "enumerator_patents.py"
  "people_resolver.py"
  "people_quality_guardrails.py"
  "people_scorer.py"
)

echo ""
echo "============================================================"
echo "AI Talent Engine: People Pipeline Ultra Autogen"
echo "Root: $ROOT"
echo "============================================================"
echo ""

echo "Inventory:"
missing=0
for f in "${REQ_FILES[@]}"; do
  if [[ -f "$f" ]]; then
    echo "  ✅ $f"
  else
    echo "  ❌ $f"
    missing=$((missing+1))
  fi
done

echo ""
if [[ $missing -eq 0 ]]; then
  echo "All required files exist already. No autogen performed."
  echo "If you want a forced overwrite, delete the files first, then re-run."
  exit 0
fi

echo ""
echo "Creating backups for any existing files that will be replaced..."
TS="$(date +%Y%m%d_%H%M%S)"
mkdir -p .bak_autogen/"$TS"
for f in "${REQ_FILES[@]}"; do
  if [[ -f "$f" && "$f" != "scenario_control_matrix.xlsx" ]]; then
    cp -p "$f" ".bak_autogen/$TS/$f"
  fi
done

echo ""
echo "Generating files with maximalist hardening built-in..."
echo ""

# ----------------------------
# scenario_enumerator_map.yaml
# ----------------------------
cat > scenario_enumerator_map.yaml <<'YAML'
# AI Talent Engine – Scenario → Enumerator Map
# Version: v1.0.0-ultra
# Date: 2025-12-30
# © 2025 L. David Mendoza. All Rights Reserved.
#
# PURPOSE
# Maps scenario labels into enumerator strategies and minimum yield guarantees.
# The pipeline will still auto-infer strategy when scenarios are unfamiliar, but
# this file locks expected behavior for interview-safe determinism.

defaults:
  min_people_per_scenario: 120
  min_people_total: 600
  openalex_per_scenario_target: 250
  github_per_scenario_target: 200
  max_total_people: 2000
  require_evidence_urls: true

strategies:
  FOUNDATIONAL:
    enumerators: ["openalex", "github"]
    openalex_topics:
      - "foundation model"
      - "large language model"
      - "transformer"
      - "scaling law"
      - "mixture of experts"
      - "diffusion model"
      - "multimodal"
      - "reinforcement learning from human feedback"
    github_topics:
      - "llm"
      - "transformer"
      - "rlhf"
      - "megatron"
      - "deepspeed"
      - "triton"
      - "jax"
      - "pytorch"
      - "vllm"

  APPLIED:
    enumerators: ["openalex", "github"]
    openalex_topics:
      - "retrieval augmented generation"
      - "rag"
      - "vector database"
      - "llm applications"
      - "agent"
      - "langchain"
      - "llamaindex"
    github_topics:
      - "rag"
      - "langchain"
      - "llamaindex"
      - "vector database"
      - "qdrant"
      - "milvus"
      - "weaviate"
      - "faiss"
      - "ollama"

  INFRA:
    enumerators: ["github", "openalex"]
    openalex_topics:
      - "distributed training"
      - "inference optimization"
      - "gpu"
      - "cuda"
      - "tensor parallel"
      - "pipeline parallel"
    github_topics:
      - "cuda"
      - "nccl"
      - "triton"
      - "tensorrt"
      - "kubernetes"
      - "ray"
      - "vllm"
      - "tgi"
      - "llama.cpp"
      - "onnx"

  HEALTHCARE:
    enumerators: ["openalex"]
    openalex_topics:
      - "biomedical"
      - "clinical"
      - "healthcare"
      - "medical imaging"
      - "genomics"
      - "bioinformatics"

  ROBOTICS:
    enumerators: ["openalex", "github"]
    openalex_topics:
      - "robotics"
      - "autonomy"
      - "control"
      - "computer vision"
      - "reinforcement learning"
    github_topics:
      - "robotics"
      - "ros"
      - "slam"
      - "reinforcement learning"
      - "vision"

scenario_aliases:
  # Map any scenario names you use into one of the strategies above
  # Examples (extend freely):
  "scenario_FOUNDATIONAL_TOP_200": "FOUNDATIONAL"
  "scenario_APPLIED_AI_TOP_300": "APPLIED"
  "scenario_INFRA_TOP_300": "INFRA"
  "scenario_TOP_300_OVERALL": "FOUNDATIONAL"
YAML


# ----------------------------
# people_quality_guardrails.py
# ----------------------------
cat > people_quality_guardrails.py <<'PY'
#!/usr/bin/env python3
"""
AI Talent Engine – People Quality Guardrails
Version: v1.0.0-ultra
Date: 2025-12-30
© 2025 L. David Mendoza. All Rights Reserved.

MANDATE
This project is maximalist by default.
No "optional hardening". No silent successes. No empty runs.

This module enforces:
- Per-scenario minimum yield
- Global minimum yield
- Evidence URL requirements
- Fail-fast behavior on unacceptable outputs
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional

@dataclass
class GuardrailConfig:
    min_people_per_scenario: int = 120
    min_people_total: int = 600
    require_evidence_urls: bool = True

class GuardrailViolation(RuntimeError):
    pass

def validate_scenario_yields(yields: Dict[str, int], cfg: GuardrailConfig) -> None:
    bad = {k: v for k, v in yields.items() if v < cfg.min_people_per_scenario}
    if bad:
        msg = "Guardrail violation: scenarios below minimum yield:\n"
        for k, v in sorted(bad.items(), key=lambda x: x[0]):
            msg += f"  - {k}: {v} (min {cfg.min_people_per_scenario})\n"
        raise GuardrailViolation(msg)

def validate_total_people(total: int, cfg: GuardrailConfig) -> None:
    if total < cfg.min_people_total:
        raise GuardrailViolation(
            f"Guardrail violation: total people {total} is below minimum {cfg.min_people_total}"
        )

def validate_evidence_urls(people_rows: List[dict], cfg: GuardrailConfig) -> None:
    if not cfg.require_evidence_urls:
        return
    missing = 0
    for r in people_rows:
        urls = str(r.get("evidence_urls", "") or "").strip()
        if not urls:
            missing += 1
    if missing:
        raise GuardrailViolation(
            f"Guardrail violation: {missing} people rows missing evidence_urls"
        )
PY


# ----------------------------
# enumerator_openalex.py
# ----------------------------
cat > enumerator_openalex.py <<'PY'
#!/usr/bin/env python3
"""
AI Talent Engine – OpenAlex Enumerator (People Discovery)
Version: v1.0.0-ultra
Date: 2025-12-30
© 2025 L. David Mendoza. All Rights Reserved.

WHAT IT DOES
- Uses OpenAlex public API to enumerate authors relevant to a scenario strategy.
- Produces candidate people rows with evidence URLs.

No scraping. No hallucinations. Deterministic volume controls.
"""

from __future__ import annotations

import time
import random
import requests
from typing import Dict, List, Tuple, Optional

OPENALEX = "https://api.openalex.org"
UA = "AI-Talent-Engine/PeopleEnumerator (contact: public-source-only)"

def _sleep():
    time.sleep(random.uniform(0.15, 0.45))

def _get(url: str, params: dict, timeout: int = 30, retries: int = 6) -> Optional[dict]:
    headers = {"User-Agent": UA}
    backoff = 0.6
    for i in range(retries):
        try:
            r = requests.get(url, params=params, headers=headers, timeout=timeout)
            if r.status_code == 200:
                return r.json()
            if r.status_code in (429, 500, 502, 503):
                time.sleep(backoff * (i + 1))
                backoff *= 1.6
                continue
        except Exception:
            time.sleep(backoff * (i + 1))
            backoff *= 1.6
    return None

def enumerate_people_from_topics(
    topics: List[str],
    per_scenario_target: int,
    max_pages: int = 10,
) -> List[dict]:
    """
    Strategy:
    - Query works for each topic.
    - Pull authorships from works.
    - Aggregate authors, keep affiliation and evidence.
    """
    people: Dict[str, dict] = {}

    # Use works search to get authors; OpenAlex supports search= for works.
    for topic in topics:
        if len(people) >= per_scenario_target:
            break

        cursor = "*"
        pages = 0

        while pages < max_pages and len(people) < per_scenario_target:
            url = f"{OPENALEX}/works"
            params = {
                "search": topic,
                "per-page": 200,
                "cursor": cursor,
                "select": "id,doi,title,authorships,primary_location,publication_year",
            }
            data = _get(url, params)
            _sleep()
            if not data or "results" not in data:
                break

            for w in data["results"]:
                evidence = []
                if w.get("id"):
                    evidence.append(w["id"])
                if w.get("doi"):
                    evidence.append(f"https://doi.org/{w['doi']}")
                pl = w.get("primary_location") or {}
                if pl.get("landing_page_url"):
                    evidence.append(pl["landing_page_url"])

                for a in (w.get("authorships") or []):
                    auth = a.get("author") or {}
                    aid = auth.get("id")
                    name = auth.get("display_name") or ""
                    if not aid or not name:
                        continue

                    inst = ""
                    insts = a.get("institutions") or []
                    if insts:
                        inst = insts[0].get("display_name") or ""

                    key = aid
                    if key not in people:
                        people[key] = {
                            "source_systems": ["OpenAlex"],
                            "openalex_author_id": aid,
                            "github_login": "",
                            "full_name": name,
                            "primary_affiliation": inst,
                            "role_hint": "Research Author",
                            "evidence_urls": list(dict.fromkeys(evidence))[:5],
                            "raw_signals": {"topics": [topic]},
                        }
                    else:
                        # merge evidence and topic tags
                        people[key]["evidence_urls"] = list(dict.fromkeys(people[key]["evidence_urls"] + evidence))[:10]
                        people[key]["raw_signals"]["topics"] = list(dict.fromkeys(people[key]["raw_signals"]["topics"] + [topic]))

                if len(people) >= per_scenario_target:
                    break

            cursor = data.get("meta", {}).get("next_cursor")
            if not cursor:
                break
            pages += 1

    return list(people.values())[:per_scenario_target]
PY


# ----------------------------
# enumerator_github.py
# ----------------------------
cat > enumerator_github.py <<'PY'
#!/usr/bin/env python3
"""
AI Talent Engine – GitHub Enumerator (People Discovery)
Version: v1.0.0-ultra
Date: 2025-12-30
© 2025 L. David Mendoza. All Rights Reserved.

WHAT IT DOES
- Uses GitHub Search API to enumerate developer accounts related to scenario topics.
- Requires a token for scale: export GITHUB_TOKEN=...

HARDENING
- Rate limit awareness
- Retries with backoff
- Deterministic caps
"""

from __future__ import annotations

import os
import time
import random
import requests
from typing import Dict, List, Optional

API = "https://api.github.com"
UA = "AI-Talent-Engine/GitHubEnumerator (public-only)"

def _sleep():
    time.sleep(random.uniform(0.2, 0.6))

def _headers() -> dict:
    h = {"User-Agent": UA, "Accept": "application/vnd.github+json"}
    tok = os.getenv("GITHUB_TOKEN", "").strip()
    if tok:
        h["Authorization"] = f"Bearer {tok}"
    return h

def _get(url: str, params: dict, timeout: int = 30, retries: int = 6) -> Optional[dict]:
    backoff = 0.8
    for i in range(retries):
        r = requests.get(url, headers=_headers(), params=params, timeout=timeout)
        if r.status_code == 200:
            return r.json()
        if r.status_code in (403, 429):
            # rate limit; sleep longer
            time.sleep(backoff * (i + 2))
            backoff *= 1.9
            continue
        if r.status_code in (500, 502, 503):
            time.sleep(backoff * (i + 1))
            backoff *= 1.6
            continue
        time.sleep(backoff * (i + 1))
        backoff *= 1.5
    return None

def enumerate_people_from_topics(topics: List[str], per_scenario_target: int) -> List[dict]:
    people: Dict[str, dict] = {}

    # Search users by topic in repos (proxy): query users with repos mentioning keywords.
    # Example: q="cuda repos:>5"
    for t in topics:
        if len(people) >= per_scenario_target:
            break

        q = f"{t} repos:>5"
        page = 1
        while page <= 10 and len(people) < per_scenario_target:
            url = f"{API}/search/users"
            params = {"q": q, "per_page": 50, "page": page}
            data = _get(url, params)
            _sleep()
            if not data or "items" not in data:
                break

            for u in data["items"]:
                login = u.get("login") or ""
                html = u.get("html_url") or ""
                if not login:
                    continue

                if login not in people:
                    people[login] = {
                        "source_systems": ["GitHub"],
                        "openalex_author_id": "",
                        "github_login": login,
                        "full_name": login,  # resolved later if desired (public profile name)
                        "primary_affiliation": "",
                        "role_hint": "Software Engineer (GitHub)",
                        "evidence_urls": [html],
                        "raw_signals": {"topics": [t]},
                    }
                else:
                    people[login]["raw_signals"]["topics"] = list(dict.fromkeys(people[login]["raw_signals"]["topics"] + [t]))

                if len(people) >= per_scenario_target:
                    break

            page += 1

    return list(people.values())[:per_scenario_target]
PY


# ----------------------------
# enumerator_patents.py
# ----------------------------
cat > enumerator_patents.py <<'PY'
#!/usr/bin/env python3
"""
AI Talent Engine – Patents Enumerator (Enrichment)
Version: v1.0.0-ultra
Date: 2025-12-30
© 2025 L. David Mendoza. All Rights Reserved.

NOTE
This enumerator is included for completeness and enrichment.
It is NOT relied upon for primary volume due to throttling risk.

It supports extracting inventors from explicit patents.google.com/patent/... pages.
"""

from __future__ import annotations

import time
import random
import requests
from bs4 import BeautifulSoup
from typing import List, Optional

UA = "AI-Talent-Engine/PatentsEnumerator (polite)"

def _sleep():
    time.sleep(random.uniform(1.0, 2.2))

def _get(url: str, timeout: int = 30, retries: int = 5) -> Optional[str]:
    headers = {"User-Agent": UA}
    backoff = 1.0
    for i in range(retries):
        try:
            r = requests.get(url, headers=headers, timeout=timeout)
            if r.status_code == 200 and r.text:
                txt = r.text.lower()
                if "unusual traffic" in txt or "/sorry/" in txt:
                    time.sleep(backoff * (i + 2))
                    backoff *= 1.7
                    continue
                return r.text
            if r.status_code in (429, 503):
                time.sleep(backoff * (i + 2))
                backoff *= 1.7
                continue
        except Exception:
            time.sleep(backoff * (i + 2))
            backoff *= 1.7
    return None

def extract_inventors(patent_url: str) -> List[dict]:
    html = _get(patent_url)
    _sleep()
    if not html:
        return []

    soup = BeautifulSoup(html, "html.parser")
    inv = []
    for tag in soup.select("dd[itemprop='inventor'] span[itemprop='name']"):
        name = tag.get_text(strip=True)
        if name:
            inv.append(name)

    out = []
    for n in list(dict.fromkeys(inv))[:50]:
        out.append({
            "source_systems": ["Patents"],
            "openalex_author_id": "",
            "github_login": "",
            "full_name": n,
            "primary_affiliation": "",
            "role_hint": "Inventor",
            "evidence_urls": [patent_url],
            "raw_signals": {"topics": ["patent_inventor"]},
        })
    return out
PY


# ----------------------------
# people_resolver.py
# ----------------------------
cat > people_resolver.py <<'PY'
#!/usr/bin/env python3
"""
AI Talent Engine – People Resolver (Identity Merge)
Version: v1.0.0-ultra
Date: 2025-12-30
© 2025 L. David Mendoza. All Rights Reserved.

PURPOSE
Merge and deduplicate people across enumerators into stable person_id rows.

Identity keys (highest to lowest):
1) OpenAlex author id
2) GitHub login
3) Normalized full name + affiliation (fallback)
"""

from __future__ import annotations

import hashlib
import re
from typing import Dict, List, Tuple

def _stable_id(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8", errors="ignore")).hexdigest()[:16]

def _norm_name(name: str) -> str:
    n = (name or "").strip().lower()
    n = re.sub(r"\s+", " ", n)
    n = re.sub(r"[^a-z0-9 \-']", "", n)
    return n

def resolve_people(raw_people: List[dict]) -> List[dict]:
    merged: Dict[str, dict] = {}

    for p in raw_people:
        oa = (p.get("openalex_author_id") or "").strip()
        gh = (p.get("github_login") or "").strip().lower()
        name = (p.get("full_name") or "").strip()
        aff = (p.get("primary_affiliation") or "").strip()

        if oa:
            key = f"openalex:{oa}"
        elif gh:
            key = f"github:{gh}"
        else:
            key = f"nameaff:{_norm_name(name)}|{_norm_name(aff)}"

        if key not in merged:
            merged[key] = {
                "person_id": "P-" + _stable_id(key),
                "full_name": name or gh or "Unknown",
                "primary_affiliation": aff,
                "role_hint": p.get("role_hint", ""),
                "source_systems": list(dict.fromkeys(p.get("source_systems", []))),
                "evidence_urls": list(dict.fromkeys(p.get("evidence_urls", []))),
                "raw_signals": p.get("raw_signals", {}),
                "openalex_author_id": oa,
                "github_login": gh,
                "scenario_tags": [],
            }
        else:
            m = merged[key]
            m["source_systems"] = list(dict.fromkeys(m["source_systems"] + p.get("source_systems", [])))
            m["evidence_urls"] = list(dict.fromkeys(m["evidence_urls"] + p.get("evidence_urls", [])))[:25]

            # prefer richer name/aff if missing
            if (not m["full_name"] or m["full_name"] == m.get("github_login")) and name:
                m["full_name"] = name
            if not m["primary_affiliation"] and aff:
                m["primary_affiliation"] = aff

            # merge signals shallowly
            rs = m.get("raw_signals") or {}
            prs = p.get("raw_signals") or {}
            for k, v in prs.items():
                if isinstance(v, list):
                    rs[k] = list(dict.fromkeys((rs.get(k) or []) + v))
                else:
                    rs[k] = v
            m["raw_signals"] = rs

    return list(merged.values())
PY


# ----------------------------
# people_scorer.py
# ----------------------------
cat > people_scorer.py <<'PY'
#!/usr/bin/env python3
"""
AI Talent Engine – People Scorer
Version: v1.0.0-ultra
Date: 2025-12-30
© 2025 L. David Mendoza. All Rights Reserved.

GOAL
Deterministic scoring for interview-safe ranking.
No hidden knobs. No unstable heuristics.

Score inputs:
- Count of scenarios triggered
- Count of evidence URLs
- Count of unique topics/keywords from raw_signals
"""

from __future__ import annotations

from typing import List, Dict

def score_people(people: List[dict]) -> List[dict]:
    out = []
    for p in people:
        scenario_count = len(set(p.get("scenario_tags") or []))
        evidence_count = len(set(p.get("evidence_urls") or []))
        rs = p.get("raw_signals") or {}
        topic_count = 0
        if isinstance(rs.get("topics"), list):
            topic_count = len(set(rs["topics"]))

        # deterministic linear score
        score = (scenario_count * 10.0) + (evidence_count * 2.0) + (topic_count * 1.5)

        p2 = dict(p)
        p2["signal_score"] = round(float(score), 2)
        out.append(p2)

    out.sort(key=lambda x: (-float(x.get("signal_score", 0.0)), (x.get("full_name") or "").lower()))
    return out
PY


# ----------------------------
# run_people_pipeline.py
# ----------------------------
cat > run_people_pipeline.py <<'PY'
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
PY

chmod +x run_people_pipeline.py
chmod +x enumerator_openalex.py enumerator_github.py enumerator_patents.py
chmod +x people_resolver.py people_quality_guardrails.py people_scorer.py

echo "✅ Autogen complete."
echo ""
echo "Installing required Python packages (idempotent)..."
pip3 install --quiet --upgrade requests beautifulsoup4 pyyaml pandas openpyxl

echo ""
echo "READY."
echo "To run with best defaults:"
echo "  export GITHUB_TOKEN='...your token...'   (recommended for volume)"
echo "  python3 run_people_pipeline.py"
echo ""
