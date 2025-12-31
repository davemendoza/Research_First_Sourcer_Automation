#!/usr/bin/env python3
"""
AI Talent Engine — People Expander (Ultra)
Version: v1.0.0-ultra
Date: 2025-12-28
© 2025 L. David Mendoza. All Rights Reserved.

PURPOSE
This script converts your Seed Hub / Scenario outputs (sources-to-enumerate) into REAL PEOPLE leads.

It is explicitly designed to solve the failure mode you just hit:
- Your current CSV is a Seed Hub table (Patents/Topics/Enumerators), not a People table.
- This script expands those seeds into named individuals, with provenance and evidence.

WHAT IT DOES (MAXIMALIST, PRODUCTION-SAFE)
- Auto-detects the latest CSV in ./output/ OR accepts --input
- Detects seed types by URL and seed_hub_type / seed_hub_class
- Expands to real individuals using public sources:
  - Google Patents assignee search pages -> enumerates patent result pages -> extracts inventors
  - Google Patents patent pages -> extracts inventors
- Writes two CSVs:
  1) people_leads_<timestamp>.csv  (one row per person lead)
  2) people_provenance_<timestamp>.csv (seed row -> person mapping with evidence)

GUARDRAILS (YOU ASKED FOR THIS)
- Deterministic: stable hashing + de-dupe across sources
- Cache: avoids re-scraping the same URL
- Rate limiting + backoff: reduces blocks
- Thread pool: fast enough to yield hundreds quickly
- Zero-LLM requirement: no OpenAI calls required
- No fake people: only names extracted from public pages
- Audit-ready provenance: every person ties to a source URL and seed row

CHANGELOG
- v1.0.0-ultra: Initial release. Patents expansion (assignee pages + patent pages) + caching + concurrency + provenance.

VALIDATION (RUN EXACTLY)
1) python3 ai_talent_people_expander_ultra.py --dry-run
2) python3 ai_talent_people_expander_ultra.py --max-total 800
3) open output/people_expanded/<run_ts>/

GIT (OPTIONAL)
git status
git add ai_talent_people_expander_ultra.py
git commit -m "Add People Expander Ultra (Seed Hub -> real individuals)"
git push

NOTES
- This file intentionally focuses on Patents first because it is the fastest, highest-yield “real people” path from your existing seed hub.
- Once you confirm volume and quality, you can extend additional adapters (OpenAlex/Semantic Scholar/GitHub) without changing the engine contract.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import random
import re
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Dict, List, Optional, Tuple

import pandas as pd

# Dependencies: requests + beautifulsoup4
try:
    import requests
    from bs4 import BeautifulSoup
except Exception as e:
    print("❌ Missing dependencies. Install with:")
    print("pip3 install requests beautifulsoup4")
    raise


# ---------------------------
# Constants / Defaults
# ---------------------------

DEFAULT_OUTPUT_DIR = "output"
DEFAULT_CACHE_DIR = ".cache/people_expander_ultra"
DEFAULT_USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123 Safari/537.36"

PATENTS_HOST = "patents.google.com"

# Threading and politeness
DEFAULT_WORKERS = 10
DEFAULT_TIMEOUT = 20
DEFAULT_SLEEP_MIN = 0.35
DEFAULT_SLEEP_MAX = 0.95
DEFAULT_MAX_RETRIES = 4

# Default volume controls
DEFAULT_MAX_SEEDS = 999999
DEFAULT_MAX_PER_SEED = 120     # max people extracted per seed (soft cap)
DEFAULT_MAX_PATENTS_PER_SEED = 30  # for assignee query pages: how many patent result pages to follow
DEFAULT_MAX_TOTAL = 1200       # global cap to keep runs bounded


# ---------------------------
# Models
# ---------------------------

@dataclass(frozen=True)
class SeedRow:
    seed_row_index: int
    tier: str
    category: str
    organization: str
    seed_hub_class: str
    seed_hub_type: str
    seed_hub_url: str
    primary_enumeration_target: str
    python_adapter: str
    expected_output: str
    notes: str
    source: str
    watchlist_flag: str
    monitoring_tier: str
    domain_type: str
    source_category: str
    language_code: str
    signal_score: float
    scenario: str


@dataclass
class PersonLead:
    # Core identity
    person_name: str
    organization_hint: str
    role_hint: str

    # Source + evidence
    source_system: str
    source_url: str
    evidence: str

    # Provenance
    seed_row_index: int
    seed_hub_type: str
    seed_hub_class: str
    seed_hub_url: str
    scenario: str
    tier: str
    category: str
    signal_score: float

    # Derived
    lead_id: str
    discovered_at_utc: str


# ---------------------------
# Utility
# ---------------------------

def now_utc_iso() -> str:
    return datetime.utcnow().replace(microsecond=0).isoformat() + "Z"


def stable_hash(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8", errors="ignore")).hexdigest()[:16]


def safe_str(x) -> str:
    if pd.isna(x):
        return ""
    return str(x).strip()


def mkdirp(path: str) -> None:
    os.makedirs(path, exist_ok=True)


def jitter_sleep(min_s: float, max_s: float) -> None:
    time.sleep(random.uniform(min_s, max_s))


def is_google_patents_url(url: str) -> bool:
    try:
        return PATENTS_HOST in url
    except Exception:
        return False


def normalize_patents_url(url: str) -> str:
    u = url.strip()
    if u.startswith("//"):
        u = "https:" + u
    if u.startswith("/patent/"):
        u = "https://" + PATENTS_HOST + u
    return u


def is_patent_detail_page(url: str) -> bool:
    # https://patents.google.com/patent/US123...
    return bool(re.search(r"patents\.google\.com/patent/", url))


def is_patents_query_page(url: str) -> bool:
    # Assignee / query search page tends to be patents.google.com/?assignee=...
    return is_google_patents_url(url) and (("?" in url and "assignee=" in url) or ("q=" in url and "/?" in url) or url.rstrip("/").endswith("patents.google.com"))


# ---------------------------
# Cache
# ---------------------------

class JsonCache:
    def __init__(self, cache_dir: str) -> None:
        self.cache_dir = cache_dir
        mkdirp(cache_dir)

    def _path(self, key: str) -> str:
        return os.path.join(self.cache_dir, f"{key}.json")

    def get(self, key: str) -> Optional[dict]:
        p = self._path(key)
        if not os.path.exists(p):
            return None
        try:
            with open(p, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return None

    def set(self, key: str, obj: dict) -> None:
        p = self._path(key)
        tmp = p + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(obj, f, ensure_ascii=False)
        os.replace(tmp, p)


# ---------------------------
# HTTP
# ---------------------------

def http_get(url: str, *, timeout: int, max_retries: int, user_agent: str) -> Optional[str]:
    headers = {"User-Agent": user_agent}
    for attempt in range(1, max_retries + 1):
        try:
            r = requests.get(url, headers=headers, timeout=timeout)
            if r.status_code == 200 and r.text:
                return r.text
            # soft backoff on non-200
            time.sleep(0.6 * attempt)
        except Exception:
            time.sleep(0.7 * attempt)
    return None


# ---------------------------
# Patents parsing
# ---------------------------

def parse_patent_inventors(html: str) -> List[str]:
    soup = BeautifulSoup(html, "html.parser")
    names: List[str] = []

    # Current patents.google.com structure frequently uses:
    # <dd itemprop="inventor"><span itemprop="name">Name</span></dd>
    for tag in soup.select("dd[itemprop='inventor'] span[itemprop='name']"):
        t = tag.get_text(strip=True)
        if t:
            names.append(t)

    # fallback: older / alternative structures
    if not names:
        for tag in soup.select("[itemprop='inventor'] [itemprop='name']"):
            t = tag.get_text(strip=True)
            if t:
                names.append(t)

    # de-dupe preserving order
    seen = set()
    out = []
    for n in names:
        if n not in seen:
            seen.add(n)
            out.append(n)
    return out


def parse_patent_title(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")
    h1 = soup.select_one("h1")
    if h1:
        return h1.get_text(strip=True)[:240]
    title = soup.title.get_text(strip=True) if soup.title else ""
    return title[:240]


def parse_query_result_patent_links(html: str, max_links: int) -> List[str]:
    soup = BeautifulSoup(html, "html.parser")
    links: List[str] = []

    for a in soup.find_all("a", href=True):
        href = a["href"]
        if href.startswith("/patent/"):
            links.append(normalize_patents_url(href))

    # de-dupe preserving order
    seen = set()
    out = []
    for u in links:
        if u not in seen:
            seen.add(u)
            out.append(u)
        if len(out) >= max_links:
            break
    return out


# ---------------------------
# Expansion Adapters
# ---------------------------

def expand_seed_patents(seed: SeedRow,
                        cache: JsonCache,
                        *,
                        timeout: int,
                        max_retries: int,
                        user_agent: str,
                        sleep_min: float,
                        sleep_max: float,
                        max_per_seed: int,
                        max_patents_per_seed: int) -> List[PersonLead]:
    """
    Expands:
    - patents.google.com/patent/... pages -> inventors
    - patents.google.com/?assignee=... query pages -> follow top patent results -> inventors
    """
    url = normalize_patents_url(seed.seed_hub_url)
    cache_key = "pat_" + stable_hash(url)

    cached = cache.get(cache_key)
    if cached and isinstance(cached.get("people"), list):
        leads = []
        for obj in cached["people"]:
            try:
                leads.append(PersonLead(**obj))
            except Exception:
                continue
        return leads

    people: List[PersonLead] = []
    html = http_get(url, timeout=timeout, max_retries=max_retries, user_agent=user_agent)
    jitter_sleep(sleep_min, sleep_max)

    if not html:
        cache.set(cache_key, {"people": []})
        return []

    # Case A: patent detail page
    if is_patent_detail_page(url):
        inventors = parse_patent_inventors(html)
        title = parse_patent_title(html)
        for name in inventors[:max_per_seed]:
            lead_id = stable_hash(f"{name}|{seed.organization}|{url}")
            people.append(PersonLead(
                person_name=name,
                organization_hint=seed.organization or "",
                role_hint="Inventor",
                source_system="Google Patents",
                source_url=url,
                evidence=f"Inventor listed on patent page. Patent: {title}",
                seed_row_index=seed.seed_row_index,
                seed_hub_type=seed.seed_hub_type,
                seed_hub_class=seed.seed_hub_class,
                seed_hub_url=seed.seed_hub_url,
                scenario=seed.scenario,
                tier=seed.tier,
                category=seed.category,
                signal_score=float(seed.signal_score) if seed.signal_score is not None else 0.0,
                lead_id=lead_id,
                discovered_at_utc=now_utc_iso()
            ))

        cache.set(cache_key, {"people": [asdict(p) for p in people]})
        return people

    # Case B: query page -> collect patent links -> visit patents -> extract inventors
    if is_patents_query_page(url):
        patent_links = parse_query_result_patent_links(html, max_links=max_patents_per_seed)
        for purl in patent_links:
            purl = normalize_patents_url(purl)
            ph = http_get(purl, timeout=timeout, max_retries=max_retries, user_agent=user_agent)
            jitter_sleep(sleep_min, sleep_max)
            if not ph:
                continue
            inventors = parse_patent_inventors(ph)
            title = parse_patent_title(ph)
            for name in inventors:
                lead_id = stable_hash(f"{name}|{seed.organization}|{purl}")
                people.append(PersonLead(
                    person_name=name,
                    organization_hint=seed.organization or "",
                    role_hint="Inventor",
                    source_system="Google Patents",
                    source_url=purl,
                    evidence=f"Inventor listed on patent. Discovered via query seed: {url}. Patent: {title}",
                    seed_row_index=seed.seed_row_index,
                    seed_hub_type=seed.seed_hub_type,
                    seed_hub_class=seed.seed_hub_class,
                    seed_hub_url=seed.seed_hub_url,
                    scenario=seed.scenario,
                    tier=seed.tier,
                    category=seed.category,
                    signal_score=float(seed.signal_score) if seed.signal_score is not None else 0.0,
                    lead_id=lead_id,
                    discovered_at_utc=now_utc_iso()
                ))
                if len(people) >= max_per_seed:
                    break
            if len(people) >= max_per_seed:
                break

        # de-dupe by lead_id
        uniq = {}
        for p in people:
            uniq[p.lead_id] = p
        people = list(uniq.values())

        cache.set(cache_key, {"people": [asdict(p) for p in people]})
        return people

    # If it's patents domain but unknown format, attempt inventor parse anyway
    inventors = parse_patent_inventors(html)
    title = parse_patent_title(html)
    for name in inventors[:max_per_seed]:
        lead_id = stable_hash(f"{name}|{seed.organization}|{url}")
        people.append(PersonLead(
            person_name=name,
            organization_hint=seed.organization or "",
            role_hint="Inventor",
            source_system="Google Patents",
            source_url=url,
            evidence=f"Inventor extracted from patents page (fallback). Title: {title}",
            seed_row_index=seed.seed_row_index,
            seed_hub_type=seed.seed_hub_type,
            seed_hub_class=seed.seed_hub_class,
            seed_hub_url=seed.seed_hub_url,
            scenario=seed.scenario,
            tier=seed.tier,
            category=seed.category,
            signal_score=float(seed.signal_score) if seed.signal_score is not None else 0.0,
            lead_id=lead_id,
            discovered_at_utc=now_utc_iso()
        ))

    cache.set(cache_key, {"people": [asdict(p) for p in people]})
    return people


# ---------------------------
# IO / Seed Loading
# ---------------------------

def find_latest_csv(output_dir: str) -> str:
    if not os.path.isdir(output_dir):
        raise SystemExit(f"❌ output dir not found: {output_dir}")
    csvs = sorted([f for f in os.listdir(output_dir) if f.endswith(".csv")])
    if not csvs:
        raise SystemExit(f"❌ no CSV files found in: {output_dir}")
    return os.path.join(output_dir, csvs[-1])


def load_seeds(input_csv: str, max_seeds: int) -> List[SeedRow]:
    df = pd.read_csv(input_csv)
    df.columns = [c.lower().strip() for c in df.columns]

    required = ["seed_hub_url", "seed_hub_type", "seed_hub_class"]
    for c in required:
        if c not in df.columns:
            raise SystemExit(f"❌ required column missing: {c}")

    seeds: List[SeedRow] = []

    for idx, r in df.iterrows():
        seed = SeedRow(
            seed_row_index=int(idx),
            tier=safe_str(r.get("tier", "")),
            category=safe_str(r.get("category", "")),
            organization=safe_str(r.get("organization", "")),
            seed_hub_class=safe_str(r.get("seed_hub_class", "")),
            seed_hub_type=safe_str(r.get("seed_hub_type", "")),
            seed_hub_url=safe_str(r.get("seed_hub_url", "")),
            primary_enumeration_target=safe_str(r.get("primary_enumeration_target", "")),
            python_adapter=safe_str(r.get("python_adapter", "")),
            expected_output=safe_str(r.get("expected_output", "")),
            notes=safe_str(r.get("notes", "")),
            source=safe_str(r.get("source", "")),
            watchlist_flag=safe_str(r.get("watchlist_flag", "")),
            monitoring_tier=safe_str(r.get("monitoring_tier", "")),
            domain_type=safe_str(r.get("domain_type", "")),
            source_category=safe_str(r.get("source_category", "")),
            language_code=safe_str(r.get("language_code", "")),
            signal_score=float(r.get("signal_score", 0.0)) if str(r.get("signal_score", "")).strip() != "" else 0.0,
            scenario=safe_str(r.get("scenario", "")),
        )
        if seed.seed_hub_url:
            seeds.append(seed)
        if len(seeds) >= max_seeds:
            break

    return seeds


# ---------------------------
# Orchestration
# ---------------------------

def pick_adapter(seed: SeedRow) -> str:
    url = seed.seed_hub_url.lower()
    if PATENTS_HOST in url:
        return "patents"
    # future adapters (openalex / semantic scholar / github) can be added here
    return "unsupported"


def write_csv(path: str, rows: List[dict], fieldnames: List[str]) -> None:
    mkdirp(os.path.dirname(path))
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for r in rows:
            w.writerow(r)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", default="", help="Input seed CSV. If omitted, uses latest CSV in ./output/")
    ap.add_argument("--output-dir", default=DEFAULT_OUTPUT_DIR, help="Base output dir (default: output)")
    ap.add_argument("--workers", type=int, default=DEFAULT_WORKERS, help="Thread workers (default: 10)")
    ap.add_argument("--max-seeds", type=int, default=DEFAULT_MAX_SEEDS, help="Max seed rows to process")
    ap.add_argument("--max-per-seed", type=int, default=DEFAULT_MAX_PER_SEED, help="Max people per seed")
    ap.add_argument("--max-patents-per-seed", type=int, default=DEFAULT_MAX_PATENTS_PER_SEED, help="Max patents to follow per assignee/query seed")
    ap.add_argument("--max-total", type=int, default=DEFAULT_MAX_TOTAL, help="Global max people leads")
    ap.add_argument("--timeout", type=int, default=DEFAULT_TIMEOUT)
    ap.add_argument("--retries", type=int, default=DEFAULT_MAX_RETRIES)
    ap.add_argument("--sleep-min", type=float, default=DEFAULT_SLEEP_MIN)
    ap.add_argument("--sleep-max", type=float, default=DEFAULT_SLEEP_MAX)
    ap.add_argument("--dry-run", action="store_true", help="Inventory only (no expansion)")
    args = ap.parse_args()

    base_out = args.output_dir
    mkdirp(base_out)

    input_csv = args.input.strip() or find_latest_csv(base_out)
    if not os.path.exists(input_csv):
        print(f"❌ input not found: {input_csv}")
        return 2

    run_ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    run_dir = os.path.join(base_out, "people_expanded", run_ts)
    mkdirp(run_dir)

    print(f"✅ INPUT: {input_csv}")
    seeds = load_seeds(input_csv, args.max_seeds)
    print(f"✅ SEEDS LOADED: {len(seeds)}")

    # Inventory coverage
    adapter_counts: Dict[str, int] = {}
    for s in seeds:
        a = pick_adapter(s)
        adapter_counts[a] = adapter_counts.get(a, 0) + 1

    print("✅ ADAPTER COVERAGE:")
    for k in sorted(adapter_counts.keys()):
        print(f"  - {k}: {adapter_counts[k]}")

    if args.dry_run:
        print("✅ DRY RUN COMPLETE (no expansion performed)")
        return 0

    cache = JsonCache(DEFAULT_CACHE_DIR)

    # Expand seeds concurrently
    people: List[PersonLead] = []
    prov_rows: List[dict] = []

    def job(seed: SeedRow) -> Tuple[SeedRow, List[PersonLead]]:
        adapter = pick_adapter(seed)
        if adapter == "patents":
            return seed, expand_seed_patents(
                seed,
                cache,
                timeout=args.timeout,
                max_retries=args.retries,
                user_agent=DEFAULT_USER_AGENT,
                sleep_min=args.sleep_min,
                sleep_max=args.sleep_max,
                max_per_seed=args.max_per_seed,
                max_patents_per_seed=args.max_patents_per_seed,
            )
        return seed, []

    with ThreadPoolExecutor(max_workers=args.workers) as ex:
        futures = [ex.submit(job, s) for s in seeds]

        for fut in as_completed(futures):
            seed, leads = fut.result()

            # provenance rows regardless
            for p in leads:
                prov_rows.append({
                    "lead_id": p.lead_id,
                    "person_name": p.person_name,
                    "source_system": p.source_system,
                    "source_url": p.source_url,
                    "seed_row_index": seed.seed_row_index,
                    "seed_hub_type": seed.seed_hub_type,
                    "seed_hub_class": seed.seed_hub_class,
                    "seed_hub_url": seed.seed_hub_url,
                    "organization": seed.organization,
                    "scenario": seed.scenario,
                    "tier": seed.tier,
                    "category": seed.category,
                    "signal_score": seed.signal_score,
                })

            people.extend(leads)

            # Global cap enforcement
            if len(people) >= args.max_total:
                break

    # De-dupe leads by lead_id
    uniq: Dict[str, PersonLead] = {}
    for p in people:
        uniq[p.lead_id] = p
    people = list(uniq.values())

    # Sort by signal_score desc, then name
    people.sort(key=lambda x: (-float(x.signal_score), x.person_name.lower()))

    people_rows = [asdict(p) for p in people]

    people_csv = os.path.join(run_dir, f"people_leads_{run_ts}.csv")
    prov_csv = os.path.join(run_dir, f"people_provenance_{run_ts}.csv")

    if people_rows:
        # stable column order
        people_fields = [
            "lead_id", "person_name", "organization_hint", "role_hint",
            "source_system", "source_url", "evidence",
            "seed_row_index", "seed_hub_type", "seed_hub_class", "seed_hub_url",
            "scenario", "tier", "category", "signal_score",
            "discovered_at_utc",
        ]
        write_csv(people_csv, people_rows, people_fields)

        prov_fields = [
            "lead_id", "person_name", "source_system", "source_url",
            "seed_row_index", "seed_hub_type", "seed_hub_class", "seed_hub_url",
            "organization", "scenario", "tier", "category", "signal_score",
        ]
        write_csv(prov_csv, prov_rows, prov_fields)

        print(f"🔥 PEOPLE LEADS: {len(people_rows)} → {people_csv}")
        print(f"🧾 PROVENANCE: {len(prov_rows)} → {prov_csv}")
        print(f"📂 OPEN FOLDER: open '{run_dir}'")
    else:
        print("❌ ZERO PEOPLE EXTRACTED.")
        print("Likely causes:")
        print("- Seed URLs are not patents.google.com OR are blocked/throttled")
        print("- Increase --max-seeds or ensure seed_hub_url contains patents.google.com")
        print("- Try: --workers 4 --sleep-min 0.8 --sleep-max 1.8")
        return 3

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
