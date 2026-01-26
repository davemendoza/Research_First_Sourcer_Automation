# ============================================================
#  Research_First_Sourcer_Automation
#  File: EXECUTION_CORE/long_running_enrichment_pass.py
#
#  Purpose:
#    Long-running public enrichment pass (demo-safe):
#      - OpenAlex author enrichment (works + citations) when identifiers exist
#      - GitHub repo topic enrichment (topics keywords) when repo URL exists
#    Uses disk cache and strict failure isolation (no pipeline crashes).
#
#  Contract:
#    run(input_csv: str, output_csv: str) -> None
#
#  Version: v3.2.0-long-running-enrichment
#  Author: Dave Mendoza
# ============================================================

from __future__ import annotations

import csv
import hashlib
import json
import os
import time
import urllib.parse
import urllib.request
from typing import Dict, List, Optional, Tuple

PIPELINE_VERSION = "v3.2.0-long-running-enrichment"

OPENALEX_API = "https://api.openalex.org"
GITHUB_API = "https://api.github.com"
UA = "Research_First_Sourcer_Automation/long_running_enrichment_pass (public-only)"

CACHE_DIR = os.path.join("EXECUTION_CORE", "_cache", "enrichment")
CACHE_TTL = 7 * 24 * 3600

TIMEOUT = 25

def run(input_csv: str, output_csv: str) -> None:
    os.makedirs(CACHE_DIR, exist_ok=True)
    rows, cols = _read_rows(input_csv)
    if not rows:
        _write_header_only(output_csv, cols)
        return

    out_rows: List[Dict[str, str]] = []
    for r in rows:
        rr = dict(r)

        # OpenAlex enrichment: only if we have ORCID_URL or OpenAlex_URL or Semantic Scholar URL
        openalex_url = (rr.get("OpenAlex_URL") or "").strip()
        orcid_url = (rr.get("ORCID_URL") or "").strip()

        oa_author = None
        if openalex_url:
            oa_author = _openalex_author_from_openalex_url(openalex_url)
        elif orcid_url:
            oa_author = _openalex_author_from_orcid(orcid_url)

        if oa_author:
            rr["OpenAlex_URL"] = oa_author.get("id", rr.get("OpenAlex_URL", ""))
            rr["Publications_Count_Raw"] = str(oa_author.get("works_count", rr.get("Publications_Count_Raw", "")) or "")
            rr["Citation_Count_Raw"] = str(oa_author.get("cited_by_count", rr.get("Citation_Count_Raw", "")) or "")
            rr["Citation_Provenance"] = "OpenAlex author cited_by_count + works_count (public)."

        # GitHub repo topics enrichment
        repo_urls = (rr.get("Repo_Evidence_URLs") or "").strip()
        if repo_urls and "github.com/" in repo_urls:
            owner, repo = _parse_repo(repo_urls)
            if owner and repo:
                topics = _github_repo_topics(owner, repo)
                if topics:
                    # Deterministic join
                    rr["Repo_Topics_Keywords"] = ", ".join(sorted(set(topics), key=lambda x: x.lower()))

        out_rows.append(rr)

    _write_rows(output_csv, out_rows, cols)

def _parse_repo(url: str) -> Tuple[str, str]:
    try:
        parts = urllib.parse.urlparse(url)
        path = parts.path.strip("/").split("/")
        if len(path) >= 2:
            return path[0], path[1]
    except Exception:
        pass
    return "", ""

def _openalex_author_from_openalex_url(url: str) -> Optional[Dict[str, object]]:
    # Accept https://openalex.org/A123... or API variant
    u = url.strip()
    if not u:
        return None
    if "openalex.org/" in u and "/A" in u:
        author_id = u.split("openalex.org/")[-1].strip().split("?")[0]
        api = f"{OPENALEX_API}/authors/{urllib.parse.quote(author_id)}"
        data = _get_json_cached(api)
        return data if isinstance(data, dict) else None
    return None

def _openalex_author_from_orcid(orcid_url: str) -> Optional[Dict[str, object]]:
    # ORCID format: https://orcid.org/0000-....
    orcid = orcid_url.strip().split("orcid.org/")[-1].strip()
    if not orcid:
        return None
    q = urllib.parse.urlencode({"filter": f"orcid:{orcid}"})
    api = f"{OPENALEX_API}/authors?{q}"
    data = _get_json_cached(api)
    if isinstance(data, dict):
        results = data.get("results")
        if isinstance(results, list) and results:
            top = results[0]
            return top if isinstance(top, dict) else None
    return None

def _github_repo_topics(owner: str, repo: str) -> List[str]:
    # Requires special preview header historically; still safe to request.
    api = f"{GITHUB_API}/repos/{urllib.parse.quote(owner)}/{urllib.parse.quote(repo)}"
    data = _get_json_cached(api, headers={"Accept": "application/vnd.github+json"})
    if isinstance(data, dict):
        topics = data.get("topics")
        if isinstance(topics, list):
            return [str(t).strip() for t in topics if str(t).strip()]
    return []

def _cache_path(url: str) -> str:
    h = hashlib.sha256(url.encode("utf-8")).hexdigest()
    return os.path.join(CACHE_DIR, f"{h}.json")

def _get_json_cached(url: str, headers: Optional[Dict[str, str]] = None) -> object:
    path = _cache_path(url)
    if os.path.exists(path) and time.time() - os.path.getmtime(path) < CACHE_TTL:
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass

    hdrs = {"User-Agent": UA}
    if headers:
        hdrs.update(headers)

    try:
        req = urllib.request.Request(url, headers=hdrs, method="GET")
        with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
            raw = resp.read().decode("utf-8", errors="replace")
        data = json.loads(raw)
        try:
            tmp = path + ".tmp"
            with open(tmp, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            os.replace(tmp, path)
        except Exception:
            pass
        return data
    except Exception:
        # Fail isolated: never crash pipeline
        return {}

def _read_rows(path: str) -> Tuple[List[Dict[str, str]], List[str]]:
    if not path or not os.path.exists(path):
        return [], []
    with open(path, "r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        cols = list(reader.fieldnames or [])
        if not cols:
            return [], []
        rows: List[Dict[str, str]] = []
        for row in reader:
            if row and any((v or "").strip() for v in row.values()):
                rows.append({k: (v if v is not None else "") for k, v in row.items()})
        return rows, cols

def _write_header_only(path: str, cols: List[str]) -> None:
    _write_rows(path, [], cols)

def _write_rows(path: str, rows: List[Dict[str, str]], cols: List[str]) -> None:
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=cols, extrasaction="ignore")
        writer.writeheader()
        for r in rows:
            writer.writerow({c: ("" if r.get(c) is None else str(r.get(c, ""))) for c in cols})
