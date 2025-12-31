#!/usr/bin/env bash
set -euo pipefail

ROOT="$(pwd)"
PY_BIN="${PY_BIN:-python3}"

if [[ ! -d ".git" ]]; then
  echo "ERROR: Must run from repo root (missing .git). Current: $ROOT" >&2
  exit 1
fi

mkdir -p core/phase_next
mkdir -p scripts
mkdir -p outputs/phase_next_cache

###############################################################################
# core/phase_next/__init__.py
###############################################################################
cat <<'PY' > core/phase_next/__init__.py
# -*- coding: utf-8 -*-
"""
AI Talent Engine - Research_First_Sourcer_Automation
Phase-Next (C/D/E) activation modules

© 2025 L. David Mendoza. All Rights Reserved.
License: Proprietary. For authorized use only.

Version: v1.0.0-phase-next-activation
Changelog:
- v1.0.0: Initial Phase 1-3 activation stack (signals, excel writeback, GPT writeback)

Validation:
- python3 -m core.phase_next.run_phase_next --help
"""
PY

###############################################################################
# core/phase_next/config.py
###############################################################################
cat <<'PY' > core/phase_next/config.py
# -*- coding: utf-8 -*-
"""
Phase-Next configuration and safety toggles.

© 2025 L. David Mendoza. All Rights Reserved.
License: Proprietary. For authorized use only.

Safety model:
- Defaults to SAFE/READ-ONLY.
- Excel writes and GPT writeback are hard-gated by env flags.
- GPT writeback uses ONLY an evidence envelope already produced, no fresh scraping.

Environment flags:
- PHASE_NEXT_READ_ONLY (default "1")
- PHASE_NEXT_EXCEL_WRITE_ENABLED (default "0")
- PHASE_NEXT_GPT_WRITEBACK_ENABLED (default "0")
- PHASE_NEXT_DRY_RUN (default "1")  # even when write enabled, defaults to dry-run unless explicitly set to 0
- PHASE_NEXT_LOG_LEVEL (default "INFO")

Inputs:
- PHASE_NEXT_SEED_HUB_XLSX (path to workbook)
- PHASE_NEXT_WORKSHEET_FILTER (optional comma-separated sheet names; blank means all)
- PHASE_NEXT_PERSON_NAME_COLUMN (default "Full Name")
- PHASE_NEXT_PERSON_ORG_COLUMN (default "Current Employer / Affiliation")
- PHASE_NEXT_GITHUB_COLUMN (default "Github")
- PHASE_NEXT_SCHOLAR_COLUMN (default "Google Scholar")
- PHASE_NEXT_SEMSCHOLAR_COLUMN (default "Semantic Scholar")
- PHASE_NEXT_OPENALEX_COLUMN (default "OpenAlex")
- PHASE_NEXT_WATCHLIST_FLAG_COLUMN (default "Watchlist_Flag")
- PHASE_NEXT_MONITORING_TIER_COLUMN (default "Monitoring_Tier")

Caching:
- PHASE_NEXT_CACHE_DIR (default "outputs/phase_next_cache")

OpenAI (Phase 3):
- OPENAI_API_KEY (required when enabled)
- OPENAI_BASE_URL (default "https://api.openai.com/v1")
- OPENAI_MODEL (default "gpt-5")
- OPENAI_REASONING_EFFORT (default "low")
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


def _env_bool(name: str, default: str) -> bool:
    v = os.environ.get(name, default).strip().lower()
    return v in ("1", "true", "yes", "y", "on")


def _env_str(name: str, default: str) -> str:
    return os.environ.get(name, default)


@dataclass(frozen=True)
class PhaseNextConfig:
    read_only: bool
    excel_write_enabled: bool
    gpt_writeback_enabled: bool
    dry_run: bool
    log_level: str

    seed_hub_xlsx: str
    worksheet_filter: list[str]

    person_name_column: str
    person_org_column: str
    github_column: str
    scholar_column: str
    semscholar_column: str
    openalex_column: str

    watchlist_flag_column: str
    monitoring_tier_column: str

    cache_dir: Path

    openai_api_key: str
    openai_base_url: str
    openai_model: str
    openai_reasoning_effort: str


def load_config() -> PhaseNextConfig:
    worksheet_filter_raw = _env_str("PHASE_NEXT_WORKSHEET_FILTER", "").strip()
    worksheet_filter = [s.strip() for s in worksheet_filter_raw.split(",") if s.strip()] if worksheet_filter_raw else []

    cache_dir = Path(_env_str("PHASE_NEXT_CACHE_DIR", "outputs/phase_next_cache")).resolve()

    return PhaseNextConfig(
        read_only=_env_bool("PHASE_NEXT_READ_ONLY", "1"),
        excel_write_enabled=_env_bool("PHASE_NEXT_EXCEL_WRITE_ENABLED", "0"),
        gpt_writeback_enabled=_env_bool("PHASE_NEXT_GPT_WRITEBACK_ENABLED", "0"),
        dry_run=_env_bool("PHASE_NEXT_DRY_RUN", "1"),
        log_level=_env_str("PHASE_NEXT_LOG_LEVEL", "INFO").strip().upper(),

        seed_hub_xlsx=_env_str("PHASE_NEXT_SEED_HUB_XLSX", "").strip(),
        worksheet_filter=worksheet_filter,

        person_name_column=_env_str("PHASE_NEXT_PERSON_NAME_COLUMN", "Full Name").strip(),
        person_org_column=_env_str("PHASE_NEXT_PERSON_ORG_COLUMN", "Current Employer / Affiliation").strip(),
        github_column=_env_str("PHASE_NEXT_GITHUB_COLUMN", "Github").strip(),
        scholar_column=_env_str("PHASE_NEXT_SCHOLAR_COLUMN", "Google Scholar").strip(),
        semscholar_column=_env_str("PHASE_NEXT_SEMSCHOLAR_COLUMN", "Semantic Scholar").strip(),
        openalex_column=_env_str("PHASE_NEXT_OPENALEX_COLUMN", "OpenAlex").strip(),

        watchlist_flag_column=_env_str("PHASE_NEXT_WATCHLIST_FLAG_COLUMN", "Watchlist_Flag").strip(),
        monitoring_tier_column=_env_str("PHASE_NEXT_MONITORING_TIER_COLUMN", "Monitoring_Tier").strip(),

        cache_dir=cache_dir,

        openai_api_key=_env_str("OPENAI_API_KEY", "").strip(),
        openai_base_url=_env_str("OPENAI_BASE_URL", "https://api.openai.com/v1").strip().rstrip("/"),
        openai_model=_env_str("OPENAI_MODEL", "gpt-5").strip(),
        openai_reasoning_effort=_env_str("OPENAI_REASONING_EFFORT", "low").strip(),
    )
PY

###############################################################################
# core/phase_next/logging_utils.py
###############################################################################
cat <<'PY' > core/phase_next/logging_utils.py
# -*- coding: utf-8 -*-
"""
Logging utilities.

© 2025 L. David Mendoza. All Rights Reserved.
License: Proprietary. For authorized use only.
"""

from __future__ import annotations

import json
import logging
import sys
from datetime import datetime
from typing import Any


def setup_logger(name: str, level: str = "INFO") -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level, logging.INFO))
    logger.propagate = False

    if not logger.handlers:
        h = logging.StreamHandler(sys.stdout)
        fmt = logging.Formatter("%(asctime)s | %(levelname)s | %(name)s | %(message)s")
        h.setFormatter(fmt)
        logger.addHandler(h)

    return logger


def json_dumps_safe(obj: Any) -> str:
    def default(o: Any) -> Any:
        try:
            return str(o)
        except Exception:
            return "<unserializable>"

    return json.dumps(obj, ensure_ascii=False, default=default, indent=2)


def utc_ts() -> str:
    return datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
PY

###############################################################################
# core/phase_next/http_client.py
###############################################################################
cat <<'PY' > core/phase_next/http_client.py
# -*- coding: utf-8 -*-
"""
Small HTTP helper with caching, timeouts, and polite user-agent.

© 2025 L. David Mendoza. All Rights Reserved.
License: Proprietary. For authorized use only.
"""

from __future__ import annotations

import hashlib
import json
import os
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Optional
from urllib.parse import urlencode

import requests


@dataclass(frozen=True)
class HttpResult:
    ok: bool
    status_code: int
    url: str
    data: Any
    error: str


class HttpClient:
    def __init__(self, cache_dir: Path, timeout_s: int = 20, user_agent: str = "AI-Talent-Engine/PhaseNext (public-source research)"):
        self.cache_dir = cache_dir
        self.timeout_s = timeout_s
        self.user_agent = user_agent
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def _cache_key(self, url: str, params: Optional[dict[str, Any]]) -> str:
        raw = url + "?" + (urlencode(params or {}, doseq=True))
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()

    def get_json(self, url: str, params: Optional[dict[str, Any]] = None, cache_ttl_s: int = 3600) -> HttpResult:
        key = self._cache_key(url, params)
        cache_path = self.cache_dir / f"http_{key}.json"
        now = time.time()

        if cache_path.exists():
            age = now - cache_path.stat().st_mtime
            if age <= cache_ttl_s:
                try:
                    return HttpResult(True, 200, url, json.loads(cache_path.read_text(encoding="utf-8")), "")
                except Exception:
                    pass

        headers = {"User-Agent": self.user_agent}
        try:
            r = requests.get(url, params=params, headers=headers, timeout=self.timeout_s)
            status = r.status_code
            if status >= 200 and status < 300:
                data = r.json()
                cache_path.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
                return HttpResult(True, status, r.url, data, "")
            return HttpResult(False, status, r.url, None, f"HTTP {status}")
        except Exception as e:
            return HttpResult(False, 0, url, None, str(e))

    def post_json(self, url: str, payload: dict[str, Any], headers_extra: Optional[dict[str, str]] = None) -> HttpResult:
        headers = {"User-Agent": self.user_agent, "Content-Type": "application/json"}
        if headers_extra:
            headers.update(headers_extra)
        try:
            r = requests.post(url, json=payload, headers=headers, timeout=self.timeout_s)
            status = r.status_code
            if status >= 200 and status < 300:
                return HttpResult(True, status, r.url, r.json(), "")
            return HttpResult(False, status, r.url, None, f"HTTP {status}: {r.text[:500]}")
        except Exception as e:
            return HttpResult(False, 0, url, None, str(e))
PY

###############################################################################
# core/phase_next/signals.py  (Phase 1)
###############################################################################
cat <<'PY' > core/phase_next/signals.py
# -*- coding: utf-8 -*-
"""
Phase 1: Richer watchlist signals (READ-ONLY).
Signals produced:
- Citation velocity scoring (OpenAlex)
- GitHub repo activity deltas (GitHub API)
- Conference appearance change detection (OpenAlex venues, configurable list)
- Patent event detection (PatentsView)

Design goals:
- Deterministic, explainable scoring.
- API-only public sources.
- Cache everything.
- No writes to Excel and no schema changes.

© 2025 L. David Mendoza. All Rights Reserved.
License: Proprietary. For authorized use only.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Optional

from .http_client import HttpClient
from .logging_utils import utc_ts

DEFAULT_CONFERENCES = [
    "NeurIPS",
    "ICLR",
    "ICML",
    "ACL",
    "EMNLP",
    "CVPR",
    "ICCV",
    "ECCV",
]

GITHUB_REPO_RE = re.compile(r"(https?://github\.com/[^/\s]+/[^/\s#?]+)")
GITHUB_USER_RE = re.compile(r"(https?://github\.com/([^/\s#?]+))/?$")


@dataclass(frozen=True)
class SignalBundle:
    citation_velocity_score: float
    citation_velocity_details: dict[str, Any]

    github_activity_score: float
    github_activity_details: dict[str, Any]

    conference_change_score: float
    conference_change_details: dict[str, Any]

    patent_event_score: float
    patent_event_details: dict[str, Any]

    signal_list: list[str]
    generated_utc: str


def _safe_float(x: Any, default: float = 0.0) -> float:
    try:
        return float(x)
    except Exception:
        return default


def _parse_github_repo(url: str) -> Optional[str]:
    m = GITHUB_REPO_RE.search(url or "")
    if not m:
        return None
    repo = m.group(1)
    repo = repo.replace("http://", "https://")
    return repo


def _extract_github_user(url: str) -> Optional[str]:
    if not url:
        return None
    url = url.strip().rstrip("/")
    m = GITHUB_USER_RE.match(url)
    if not m:
        return None
    username = m.group(2)
    if username.lower() in ("features", "topics", "explore", "marketplace", "settings"):
        return None
    return username


def _normalize_name_for_patents(name: str) -> str:
    return re.sub(r"\s+", " ", (name or "").strip())


class SignalEngine:
    def __init__(self, cache_dir: Path):
        self.http = HttpClient(cache_dir=cache_dir, timeout_s=25)
        self.cache_dir = cache_dir

    # -------------------------
    # Citation velocity (OpenAlex)
    # -------------------------
    def citation_velocity(self, openalex_id_or_url: str) -> tuple[float, dict[str, Any]]:
        """
        Approach:
        - Resolve author and fetch works in last 365 days via OpenAlex.
        - Compute citations in last 365 days by summing cited_by_count for those works (proxy).
        - Produce a bounded score 0..1 using log scaling.
        """
        if not openalex_id_or_url:
            return 0.0, {"ok": False, "reason": "missing_openalex"}

        author_id = self._openalex_author_id(openalex_id_or_url)
        if not author_id:
            return 0.0, {"ok": False, "reason": "cannot_resolve_author"}

        one_year_ago = (datetime.utcnow() - timedelta(days=365)).date().isoformat()
        works_url = "https://api.openalex.org/works"
        params = {
            "filter": f"authorships.author.id:{author_id},from_publication_date:{one_year_ago}",
            "per-page": 200,
        }

        res = self.http.get_json(works_url, params=params, cache_ttl_s=6 * 3600)
        if not res.ok or not res.data:
            return 0.0, {"ok": False, "reason": "openalex_works_fetch_failed", "error": res.error, "url": res.url}

        results = res.data.get("results", []) or []
        cited = 0
        pubs = 0
        top_titles: list[str] = []
        for w in results:
            pubs += 1
            cited += int(w.get("cited_by_count") or 0)
            t = (w.get("title") or "").strip()
            if t and len(top_titles) < 5:
                top_titles.append(t)

        # bounded log scaling
        import math
        score = min(1.0, math.log10(1 + cited) / 4.0)  # ~10k citations => 1.0
        details = {
            "ok": True,
            "author_id": author_id,
            "works_last_365d": pubs,
            "cited_by_count_sum_proxy": cited,
            "top_recent_titles_sample": top_titles,
        }
        return float(score), details

    def _openalex_author_id(self, openalex_id_or_url: str) -> Optional[str]:
        s = (openalex_id_or_url or "").strip()
        if not s:
            return None
        # allow full URL like https://openalex.org/A123...
        if "openalex.org/" in s:
            tail = s.split("openalex.org/")[-1].strip().split("?")[0].strip().split("#")[0]
            if tail.startswith("A"):
                return f"https://openalex.org/{tail}"
        # allow bare A123...
        if s.startswith("A") and s[1:].isdigit():
            return f"https://openalex.org/{s}"
        # allow already-normalized id
        if s.startswith("https://openalex.org/A"):
            return s.split("?")[0]
        return None

    # -------------------------
    # GitHub repo activity deltas
    # -------------------------
    def github_activity(self, github_url: str, github_repo_url: str) -> tuple[float, dict[str, Any]]:
        """
        Approach:
        - Prefer explicit repo URL if present.
        - Else use user and fetch public events count in last 90 days (lightweight proxy).
        - Compute score 0..1 via log scaling.
        """
        repo = _parse_github_repo(github_repo_url or "")
        user = _extract_github_user(github_url or "")

        if not repo and not user:
            return 0.0, {"ok": False, "reason": "missing_github"}

        if repo:
            # GitHub API: /repos/{owner}/{repo}
            owner_repo = repo.replace("https://github.com/", "").strip("/")
            api_url = f"https://api.github.com/repos/{owner_repo}"
            res = self.http.get_json(api_url, params=None, cache_ttl_s=3 * 3600)
            if not res.ok or not res.data:
                return 0.0, {"ok": False, "reason": "github_repo_fetch_failed", "error": res.error, "url": res.url}

            pushed_at = res.data.get("pushed_at") or ""
            stargazers = int(res.data.get("stargazers_count") or 0)
            forks = int(res.data.get("forks_count") or 0)
            open_issues = int(res.data.get("open_issues_count") or 0)

            # proxy scoring: recent push + popularity
            import math
            recency_bonus = 0.0
            try:
                if pushed_at:
                    dt = datetime.fromisoformat(pushed_at.replace("Z", "+00:00"))
                    days = (datetime.utcnow().replace(tzinfo=dt.tzinfo) - dt).days
                    if days <= 14:
                        recency_bonus = 0.35
                    elif days <= 60:
                        recency_bonus = 0.20
                    elif days <= 180:
                        recency_bonus = 0.10
            except Exception:
                recency_bonus = 0.0

            pop = math.log10(1 + stargazers) / 6.0 + math.log10(1 + forks) / 6.0
            score = min(1.0, recency_bonus + pop)

            details = {
                "ok": True,
                "mode": "repo",
                "repo": repo,
                "pushed_at": pushed_at,
                "stargazers": stargazers,
                "forks": forks,
                "open_issues": open_issues,
            }
            return float(score), details

        # user-based fallback
        api_url = f"https://api.github.com/users/{user}/events/public"
        res = self.http.get_json(api_url, params={"per_page": 100}, cache_ttl_s=2 * 3600)
        if not res.ok or res.data is None:
            return 0.0, {"ok": False, "reason": "github_user_events_failed", "error": res.error, "url": res.url}

        events = res.data if isinstance(res.data, list) else []
        # count events in last 90 days
        cutoff = datetime.utcnow() - timedelta(days=90)
        cnt = 0
        types: dict[str, int] = {}
        for e in events:
            try:
                created = e.get("created_at")
                if not created:
                    continue
                dt = datetime.fromisoformat(created.replace("Z", "+00:00"))
                if dt.replace(tzinfo=None) >= cutoff:
                    cnt += 1
                    t = e.get("type") or "Unknown"
                    types[t] = types.get(t, 0) + 1
            except Exception:
                continue

        import math
        score = min(1.0, math.log10(1 + cnt) / 2.0)  # ~100 events -> 1.0
        details = {"ok": True, "mode": "user_events", "user": user, "events_last_90d": cnt, "type_counts": types}
        return float(score), details

    # -------------------------
    # Conference appearance changes (OpenAlex)
    # -------------------------
    def conference_changes(self, openalex_id_or_url: str, conference_names: Optional[list[str]] = None) -> tuple[float, dict[str, Any]]:
        """
        Approach:
        - Fetch works in last 365 days for author (OpenAlex).
        - Detect venue display_name containing target conference strings.
        - Score by count and novelty (cache previous counts).
        """
        if not openalex_id_or_url:
            return 0.0, {"ok": False, "reason": "missing_openalex"}

        author_id = self._openalex_author_id(openalex_id_or_url)
        if not author_id:
            return 0.0, {"ok": False, "reason": "cannot_resolve_author"}

        targets = conference_names or DEFAULT_CONFERENCES
        targets_norm = [t.lower() for t in targets]

        one_year_ago = (datetime.utcnow() - timedelta(days=365)).date().isoformat()
        works_url = "https://api.openalex.org/works"
        params = {
            "filter": f"authorships.author.id:{author_id},from_publication_date:{one_year_ago}",
            "per-page": 200,
        }

        res = self.http.get_json(works_url, params=params, cache_ttl_s=6 * 3600)
        if not res.ok or not res.data:
            return 0.0, {"ok": False, "reason": "openalex_works_fetch_failed", "error": res.error, "url": res.url}

        results = res.data.get("results", []) or []
        hits: dict[str, int] = {t: 0 for t in targets}
        sample_titles: list[str] = []

        for w in results:
            venue = ((w.get("host_venue") or {}).get("display_name") or "").strip()
            vlow = venue.lower()
            for i, t in enumerate(targets_norm):
                if t and t in vlow:
                    hits[targets[i]] += 1
                    if len(sample_titles) < 5:
                        title = (w.get("title") or "").strip()
                        if title:
                            sample_titles.append(title)
                    break

        total = sum(hits.values())

        # novelty: compare to cached prior snapshot
        snap_key = re.sub(r"[^a-zA-Z0-9]+", "_", author_id).strip("_")
        snap_path = self.cache_dir / f"conf_snapshot_{snap_key}.json"
        prior_total = 0
        prior_hits: dict[str, int] = {}
        try:
            if snap_path.exists():
                import json
                prior = json.loads(snap_path.read_text(encoding="utf-8"))
                prior_total = int(prior.get("total") or 0)
                prior_hits = prior.get("hits") or {}
        except Exception:
            prior_total = 0
            prior_hits = {}

        delta = max(0, total - prior_total)

        # write snapshot (cache is allowed; not Excel)
        try:
            import json
            snap_path.write_text(json.dumps({"total": total, "hits": hits, "updated_utc": utc_ts()}, ensure_ascii=False, indent=2), encoding="utf-8")
        except Exception:
            pass

        import math
        base = min(1.0, math.log10(1 + total) / 1.6)  # 0..1
        novelty_bonus = min(0.35, 0.15 * delta)
        score = min(1.0, base + novelty_bonus)

        details = {
            "ok": True,
            "author_id": author_id,
            "targets": targets,
            "hits": hits,
            "total": total,
            "prior_total": prior_total,
            "delta": delta,
            "sample_titles": sample_titles,
            "prior_hits": prior_hits,
        }
        return float(score), details

    # -------------------------
    # Patent events (PatentsView)
    # -------------------------
    def patent_events(self, person_name: str) -> tuple[float, dict[str, Any]]:
        """
        Approach:
        - Query PatentsView for inventor last 365 days by name string.
        - Count patents and produce a bounded score.
        Note: Name matching is fuzzy and imperfect, so score is conservative.
        """
        name = _normalize_name_for_patents(person_name)
        if not name or len(name) < 4:
            return 0.0, {"ok": False, "reason": "missing_name"}

        one_year_ago = (datetime.utcnow() - timedelta(days=365)).date().isoformat()

        # PatentsView v1 endpoint style
        # Docs: https://patentsview.org/apis/patents
        url = "https://search.patentsview.org/api/v1/patents/query"
        # conservative query: inventor name contains token and patent_date >=
        # Using simple text query syntax (PatentsView supports Lucene-like query)
        query = f'inventors.inventor_name:"{name}" AND patent_date:[{one_year_ago} TO *]'
        payload = {
            "q": {"_text_any": {"patent_title": ""}},  # placeholder structure for service robustness
        }

        # PatentsView endpoint varies; attempt a simpler GET fallback first
        # Many deployments accept:
        # GET https://search.patentsview.org/api/v1/patents/query?q=...&f=...
        fields = "patent_number,patent_date,patent_title"
        params = {"q": query, "f": fields, "o": '{"per_page":25}'}

        res = self.http.get_json(url, params=params, cache_ttl_s=12 * 3600)
        if not res.ok or not res.data:
            # soft-fail: patents are optional
            return 0.0, {"ok": False, "reason": "patentsview_fetch_failed", "error": res.error, "url": res.url}

        patents = res.data.get("patents") or res.data.get("results") or []
        cnt = len(patents) if isinstance(patents, list) else 0
        sample = []
        for p in patents[:5]:
            sample.append({
                "patent_number": p.get("patent_number") or p.get("patentNumber"),
                "patent_date": p.get("patent_date") or p.get("patentDate"),
                "patent_title": p.get("patent_title") or p.get("patentTitle"),
            })

        import math
        score = min(1.0, math.log10(1 + cnt) / 1.2)  # 0..1 quickly
        details = {"ok": True, "name": name, "patents_last_365d": cnt, "sample": sample}
        return float(score), details

    # -------------------------
    # Bundle for a person row
    # -------------------------
    def build_bundle(
        self,
        person_name: str,
        openalex_id_or_url: str,
        github_url: str,
        github_repo_url: str,
        conferences: Optional[list[str]] = None,
    ) -> SignalBundle:
        cv_s, cv_d = self.citation_velocity(openalex_id_or_url)
        gh_s, gh_d = self.github_activity(github_url, github_repo_url)
        conf_s, conf_d = self.conference_changes(openalex_id_or_url, conference_names=conferences)
        pat_s, pat_d = self.patent_events(person_name)

        signal_list = []
        if cv_s > 0:
            signal_list.append(f"Citation velocity: {cv_s:.2f}")
        if gh_s > 0:
            signal_list.append(f"GitHub activity: {gh_s:.2f}")
        if conf_s > 0:
            signal_list.append(f"Conference delta: {conf_s:.2f}")
        if pat_s > 0:
            signal_list.append(f"Patent events: {pat_s:.2f}")

        return SignalBundle(
            citation_velocity_score=cv_s,
            citation_velocity_details=cv_d,
            github_activity_score=gh_s,
            github_activity_details=gh_d,
            conference_change_score=conf_s,
            conference_change_details=conf_d,
            patent_event_score=pat_s,
            patent_event_details=pat_d,
            signal_list=signal_list,
            generated_utc=utc_ts(),
        )
PY

###############################################################################
# core/phase_next/watchlist_eval.py  (Phase 1 consumer)
###############################################################################
cat <<'PY' > core/phase_next/watchlist_eval.py
# -*- coding: utf-8 -*-
"""
Phase-Next watchlist evaluation (READ-ONLY by default).

Outputs:
- watchlist decision (flag)
- monitoring tier
- rationale
- signal list (human readable and auditable)
- evidence envelope (structured)

No Excel writes here. No GPT calls here.

© 2025 L. David Mendoza. All Rights Reserved.
License: Proprietary. For authorized use only.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List

from .signals import SignalBundle


@dataclass(frozen=True)
class WatchlistDecision:
    watchlist_flag: str
    monitoring_tier: str
    score: float
    rationale: str
    signals: List[str]
    evidence_envelope: Dict[str, Any]


def _clamp01(x: float) -> float:
    return max(0.0, min(1.0, float(x)))


def evaluate_watchlist(bundle: SignalBundle) -> WatchlistDecision:
    """
    Deterministic scoring:
    Weighted sum of Phase 1 signals:
    - citation velocity: 0.35
    - github activity: 0.25
    - conference changes: 0.25
    - patent events: 0.15

    Monitoring tiers:
    - Tier 1: score >= 0.70 (high priority)
    - Tier 2: score >= 0.45
    - Tier 3: score >= 0.25
    - Tier 4: else (low)

    Watchlist flag:
    - Y if tier 1-2, else N
    """
    score = (
        0.35 * _clamp01(bundle.citation_velocity_score)
        + 0.25 * _clamp01(bundle.github_activity_score)
        + 0.25 * _clamp01(bundle.conference_change_score)
        + 0.15 * _clamp01(bundle.patent_event_score)
    )
    score = _clamp01(score)

    if score >= 0.70:
        tier = "Tier_1"
    elif score >= 0.45:
        tier = "Tier_2"
    elif score >= 0.25:
        tier = "Tier_3"
    else:
        tier = "Tier_4"

    flag = "Y" if tier in ("Tier_1", "Tier_2") else "N"

    rationale_parts = []
    rationale_parts.append(f"Composite signal score {score:.2f} from public evidence feeds.")
    if bundle.citation_velocity_score > 0:
        rationale_parts.append("Citation velocity indicates research influence or rising output.")
    if bundle.github_activity_score > 0:
        rationale_parts.append("GitHub activity suggests ongoing engineering output.")
    if bundle.conference_change_score > 0:
        rationale_parts.append("Conference signal suggests visible publication or venue presence changes.")
    if bundle.patent_event_score > 0:
        rationale_parts.append("Patent signal suggests recent IP activity (name match is conservative).")

    rationale = " ".join(rationale_parts).strip()

    envelope = {
        "generated_utc": bundle.generated_utc,
        "signals": {
            "citation_velocity": {"score": bundle.citation_velocity_score, "details": bundle.citation_velocity_details},
            "github_activity": {"score": bundle.github_activity_score, "details": bundle.github_activity_details},
            "conference_change": {"score": bundle.conference_change_score, "details": bundle.conference_change_details},
            "patent_events": {"score": bundle.patent_event_score, "details": bundle.patent_event_details},
        },
        "composite": {"score": score, "tier": tier, "flag": flag},
    }

    return WatchlistDecision(
        watchlist_flag=flag,
        monitoring_tier=tier,
        score=score,
        rationale=rationale,
        signals=bundle.signal_list,
        evidence_envelope=envelope,
    )
PY

###############################################################################
# core/phase_next/excel_io.py  (Phase 2 support)
###############################################################################
cat <<'PY' > core/phase_next/excel_io.py
# -*- coding: utf-8 -*-
"""
Excel read/write helpers.

Phase 2 gates all writes by:
- config.read_only must be False
- config.excel_write_enabled must be True
- config.dry_run must be False to actually write
- target columns must already exist (no schema changes)

© 2025 L. David Mendoza. All Rights Reserved.
License: Proprietary. For authorized use only.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

from openpyxl import load_workbook
from openpyxl.worksheet.worksheet import Worksheet


@dataclass(frozen=True)
class SheetHeaderMap:
    header_row: int
    col_to_idx: Dict[str, int]


def _cell_str(v: Any) -> str:
    return ("" if v is None else str(v)).strip()


def find_header_map(ws: Worksheet, required_cols: List[str]) -> SheetHeaderMap:
    """
    Finds the header row by scanning top 50 rows and selecting the first row that contains
    all required columns.
    """
    required_norm = {c.strip(): c.strip() for c in required_cols if c.strip()}
    for r in range(1, 51):
        col_to_idx: Dict[str, int] = {}
        for c in range(1, ws.max_column + 1):
            v = _cell_str(ws.cell(row=r, column=c).value)
            if v:
                col_to_idx[v] = c
        if all(col in col_to_idx for col in required_norm.keys()):
            return SheetHeaderMap(header_row=r, col_to_idx=col_to_idx)

    raise ValueError(f"Could not find header row containing required columns: {required_cols}")


def iter_data_rows(ws: Worksheet, header_row: int) -> range:
    return range(header_row + 1, ws.max_row + 1)


def read_cell(ws: Worksheet, row: int, col_idx: int) -> Any:
    return ws.cell(row=row, column=col_idx).value


def write_cell(ws: Worksheet, row: int, col_idx: int, value: Any) -> None:
    ws.cell(row=row, column=col_idx).value = value


def open_workbook(path: str):
    return load_workbook(path)
PY

###############################################################################
# core/phase_next/excel_writeback.py  (Phase 2)
###############################################################################
cat <<'PY' > core/phase_next/excel_writeback.py
# -*- coding: utf-8 -*-
"""
Phase 2: Deterministic Excel writeback (NO GPT).

Writes:
- Watchlist_Flag
- Monitoring_Tier

Rules:
- Idempotent writes only.
- Clear logging and per-cell audit records.
- Dry-run preserved (default on).
- No schema changes (columns must exist).

© 2025 L. David Mendoza. All Rights Reserved.
License: Proprietary. For authorized use only.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List

from .config import PhaseNextConfig
from .excel_io import find_header_map, iter_data_rows, open_workbook, read_cell, write_cell
from .logging_utils import json_dumps_safe


@dataclass(frozen=True)
class WriteRecord:
    sheet: str
    row: int
    column: str
    old_value: Any
    new_value: Any


@dataclass(frozen=True)
class WritebackResult:
    ok: bool
    dry_run: bool
    wrote_any: bool
    records: List[WriteRecord]
    errors: List[str]


def _norm(v: Any) -> str:
    return ("" if v is None else str(v)).strip()


def writeback_operational_fields(
    cfg: PhaseNextConfig,
    decisions_by_rowkey: Dict[str, Dict[str, Any]],
) -> WritebackResult:
    """
    decisions_by_rowkey key:
      f"{sheet_name}::{row_number}"
    values:
      {"Watchlist_Flag": "Y/N", "Monitoring_Tier": "Tier_1..Tier_4"}
    """
    errors: List[str] = []
    records: List[WriteRecord] = []

    if cfg.read_only:
        return WritebackResult(False, cfg.dry_run, False, records, ["READ_ONLY is enabled. No writes allowed."])

    if not cfg.excel_write_enabled:
        return WritebackResult(False, cfg.dry_run, False, records, ["EXCEL_WRITE is not enabled. No writes allowed."])

    if not cfg.seed_hub_xlsx:
        return WritebackResult(False, cfg.dry_run, False, records, ["Missing PHASE_NEXT_SEED_HUB_XLSX."])

    required = [
        cfg.watchlist_flag_column,
        cfg.monitoring_tier_column,
    ]

    wb = None
    try:
        wb = open_workbook(cfg.seed_hub_xlsx)
    except Exception as e:
        return WritebackResult(False, cfg.dry_run, False, records, [f"Failed to open workbook: {e}"])

    wrote_any = False

    for ws in wb.worksheets:
        if cfg.worksheet_filter and ws.title not in cfg.worksheet_filter:
            continue

        try:
            header = find_header_map(ws, required_cols=required)
        except Exception as e:
            errors.append(f"[{ws.title}] header error: {e}")
            continue

        flag_idx = header.col_to_idx[cfg.watchlist_flag_column]
        tier_idx = header.col_to_idx[cfg.monitoring_tier_column]

        for row in iter_data_rows(ws, header.header_row):
            rowkey = f"{ws.title}::{row}"
            if rowkey not in decisions_by_rowkey:
                continue

            d = decisions_by_rowkey[rowkey]
            new_flag = d.get("Watchlist_Flag")
            new_tier = d.get("Monitoring_Tier")

            # idempotent writes: only change when different and non-empty
            if new_flag is not None:
                old = read_cell(ws, row, flag_idx)
                if _norm(old) != _norm(new_flag) and _norm(new_flag):
                    records.append(WriteRecord(ws.title, row, cfg.watchlist_flag_column, old, new_flag))
                    wrote_any = True
                    if not cfg.dry_run:
                        write_cell(ws, row, flag_idx, new_flag)

            if new_tier is not None:
                old = read_cell(ws, row, tier_idx)
                if _norm(old) != _norm(new_tier) and _norm(new_tier):
                    records.append(WriteRecord(ws.title, row, cfg.monitoring_tier_column, old, new_tier))
                    wrote_any = True
                    if not cfg.dry_run:
                        write_cell(ws, row, tier_idx, new_tier)

    if errors:
        # do not write file if structural errors exist
        return WritebackResult(False, cfg.dry_run, wrote_any, records, errors)

    if wrote_any and not cfg.dry_run:
        try:
            wb.save(cfg.seed_hub_xlsx)
        except Exception as e:
            return WritebackResult(False, cfg.dry_run, wrote_any, records, [f"Failed to save workbook: {e}"])

    return WritebackResult(True, cfg.dry_run, wrote_any, records, errors)
PY

###############################################################################
# core/phase_next/evidence_envelope.py  (Phase 1 output persistence)
###############################################################################
cat <<'PY' > core/phase_next/evidence_envelope.py
# -*- coding: utf-8 -*-
"""
Evidence envelope persistence.

This file writes to local cache only (allowed).
No Excel writes. No schema changes.

© 2025 L. David Mendoza. All Rights Reserved.
License: Proprietary. For authorized use only.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional

from .logging_utils import utc_ts


@dataclass(frozen=True)
class EnvelopePaths:
    envelope_path: Path


def envelope_filename(person_name: str, sheet: str, row: int) -> str:
    safe = "".join(ch if ch.isalnum() else "_" for ch in (person_name or "unknown")).strip("_")
    safe = safe[:80] if safe else "unknown"
    return f"envelope_{sheet}_{row}_{safe}.json"


def write_envelope(cache_dir: Path, person_name: str, sheet: str, row: int, envelope: Dict[str, Any]) -> EnvelopePaths:
    cache_dir.mkdir(parents=True, exist_ok=True)
    fname = envelope_filename(person_name, sheet, row)
    path = cache_dir / fname
    payload = {
        "generated_utc": utc_ts(),
        "person_name": person_name,
        "sheet": sheet,
        "row": row,
        "envelope": envelope,
    }
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return EnvelopePaths(envelope_path=path)


def read_envelope(path: Path) -> Optional[Dict[str, Any]]:
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None
PY

###############################################################################
# core/phase_next/gpt_writeback.py  (Phase 3)
###############################################################################
cat <<'PY' > core/phase_next/gpt_writeback.py
# -*- coding: utf-8 -*-
"""
Phase 3: GPT writeback (FINAL).

Rules:
- Uses ONLY the evidence envelope already generated (no fresh scraping).
- Deterministic input -> explainable output:
  - We preserve the evidence envelope verbatim.
  - GPT is asked to generate narrative fields only (Strengths, Weaknesses, Notes, Confidence).
- Clear separation between evidence and narrative.

Output is a JSON object with:
{
  "Strengths": "...",
  "Weaknesses": "...",
  "Notes": "...",
  "Confidence": "High|Medium|Low"
}

This module calls the OpenAI Responses API:
POST {OPENAI_BASE_URL}/responses

Docs reference:
- Responses API is the recommended endpoint for new projects. :contentReference[oaicite:0]{index=0}

© 2025 L. David Mendoza. All Rights Reserved.
License: Proprietary. For authorized use only.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, Dict, Optional

from .config import PhaseNextConfig
from .http_client import HttpClient
from .logging_utils import json_dumps_safe


SYSTEM_INSTRUCTIONS = """You are an evidence-based talent research assistant.
You must ONLY use the provided evidence envelope. Do not assume facts not present in evidence.
Write hiring-manager-ready language, concise but specific.

Return ONLY valid JSON with keys:
Strengths, Weaknesses, Notes, Confidence

Confidence must be one of: High, Medium, Low
"""

USER_PROMPT_TEMPLATE = """EVIDENCE ENVELOPE (authoritative, do not add outside info):
{envelope_json}

Task:
Generate:
- Strengths: 2 to 4 sentences. Must cite concrete evidence signals.
- Weaknesses: 1 to 3 sentences. Must be realistic gaps or uncertainty based on missing signals.
- Notes: 1 to 3 sentences. Operational next steps for the reviewer (what to validate next).
- Confidence: High/Medium/Low based on evidence completeness.

Hard rules:
- Use only evidence.
- No web browsing suggestions.
- No sourcing IP or proprietary framework disclosure.
- No fluff.
Return valid JSON only.
"""


@dataclass(frozen=True)
class GPTWritebackResult:
    ok: bool
    model: str
    response_json: Optional[Dict[str, Any]]
    raw: Any
    error: str


def _validate_payload(obj: Dict[str, Any]) -> Optional[str]:
    req = ["Strengths", "Weaknesses", "Notes", "Confidence"]
    for k in req:
        if k not in obj:
            return f"Missing key: {k}"
    if str(obj.get("Confidence")) not in ("High", "Medium", "Low"):
        return "Confidence must be High, Medium, or Low"
    return None


def generate_narrative_from_envelope(cfg: PhaseNextConfig, envelope: Dict[str, Any], cache_dir) -> GPTWritebackResult:
    if cfg.read_only:
        return GPTWritebackResult(False, cfg.openai_model, None, None, "READ_ONLY is enabled. GPT writeback is blocked.")
    if not cfg.gpt_writeback_enabled:
        return GPTWritebackResult(False, cfg.openai_model, None, None, "PHASE_NEXT_GPT_WRITEBACK_ENABLED is not enabled.")
    if not cfg.openai_api_key:
        return GPTWritebackResult(False, cfg.openai_model, None, None, "Missing OPENAI_API_KEY.")

    http = HttpClient(cache_dir=cache_dir, timeout_s=60)

    url = f"{cfg.openai_base_url}/responses"
    envelope_json = json.dumps(envelope, ensure_ascii=False, indent=2)

    payload = {
        "model": cfg.openai_model,
        "reasoning": {"effort": cfg.openai_reasoning_effort},
        "instructions": SYSTEM_INSTRUCTIONS,
        "input": USER_PROMPT_TEMPLATE.format(envelope_json=envelope_json),
        "text": {"format": {"type": "json_object"}},
    }

    headers = {"Authorization": f"Bearer {cfg.openai_api_key}"}
    res = http.post_json(url, payload=payload, headers_extra=headers)
    if not res.ok or not res.data:
        return GPTWritebackResult(False, cfg.openai_model, None, res.error, f"OpenAI call failed: {res.error}")

    # Responses API output_text is typical; also handle structured output variations.
    out_text = None
    try:
        out_text = res.data.get("output_text")
    except Exception:
        out_text = None

    parsed = None
    if out_text:
        try:
            parsed = json.loads(out_text)
        except Exception:
            parsed = None

    # fallback: attempt to locate json in output array if needed
    if parsed is None:
        try:
            output = res.data.get("output") or []
            for item in output:
                content = item.get("content") or []
                for c in content:
                    if c.get("type") == "output_text" and c.get("text"):
                        try:
                            parsed = json.loads(c["text"])
                            break
                        except Exception:
                            pass
                if parsed is not None:
                    break
        except Exception:
            pass

    if not isinstance(parsed, dict):
        return GPTWritebackResult(False, cfg.openai_model, None, res.data, "Could not parse JSON from model response.")

    err = _validate_payload(parsed)
    if err:
        return GPTWritebackResult(False, cfg.openai_model, parsed, res.data, f"Invalid JSON payload: {err}")

    return GPTWritebackResult(True, cfg.openai_model, parsed, res.data, "")
PY

###############################################################################
# core/phase_next/run_phase_next.py  (End-to-end orchestrator)
###############################################################################
cat <<'PY' > core/phase_next/run_phase_next.py
# -*- coding: utf-8 -*-
"""
End-to-end Phase-Next runner (Phase 1-3).

Phase 1 (default):
- Load workbook rows
- Build signals (public feeds)
- Compute watchlist decisions
- Write evidence envelopes to local cache
- Print a structured summary
No Excel writes. No GPT calls.

Phase 2:
- If PHASE_NEXT_READ_ONLY=0 and PHASE_NEXT_EXCEL_WRITE_ENABLED=1
- Writes Watchlist_Flag and Monitoring_Tier
- Dry-run default remains ON unless PHASE_NEXT_DRY_RUN=0

Phase 3:
- If PHASE_NEXT_GPT_WRITEBACK_ENABLED=1
- Uses ONLY evidence envelopes
- Produces narrative JSON and writes to local cache outputs (not Excel)

© 2025 L. David Mendoza. All Rights Reserved.
License: Proprietary. For authorized use only.
"""

from __future__ import annotations

import argparse
from dataclasses import asdict
from pathlib import Path
from typing import Any, Dict, List

from .config import load_config
from .excel_io import find_header_map, iter_data_rows, open_workbook, read_cell
from .evidence_envelope import write_envelope
from .gpt_writeback import generate_narrative_from_envelope
from .logging_utils import setup_logger, json_dumps_safe
from .signals import SignalEngine
from .watchlist_eval import evaluate_watchlist
from .excel_writeback import writeback_operational_fields


def _s(v: Any) -> str:
    return ("" if v is None else str(v)).strip()


def main() -> int:
    ap = argparse.ArgumentParser(description="Phase-Next runner (C/D/E activation).")
    ap.add_argument("--limit", type=int, default=0, help="Limit rows processed per sheet (0 = no limit).")
    ap.add_argument("--conference-list", type=str, default="", help="Comma-separated conference keywords override.")
    ap.add_argument("--github-repo-column", type=str, default="Github_Repo", help="Optional repo URL column name.")
    ap.add_argument("--dump-json", action="store_true", help="Dump per-row decision JSON to stdout.")
    args = ap.parse_args()

    cfg = load_config()
    log = setup_logger("phase_next", level=cfg.log_level)

    if not cfg.seed_hub_xlsx:
        log.error("Missing PHASE_NEXT_SEED_HUB_XLSX.")
        return 2

    cache_dir = cfg.cache_dir
    cache_dir.mkdir(parents=True, exist_ok=True)

    log.info("Config (sanitized): %s", json_dumps_safe({
        "read_only": cfg.read_only,
        "excel_write_enabled": cfg.excel_write_enabled,
        "gpt_writeback_enabled": cfg.gpt_writeback_enabled,
        "dry_run": cfg.dry_run,
        "seed_hub_xlsx": cfg.seed_hub_xlsx,
        "worksheet_filter": cfg.worksheet_filter,
        "cache_dir": str(cfg.cache_dir),
        "openai_base_url": cfg.openai_base_url,
        "openai_model": cfg.openai_model,
    }))

    conferences = [s.strip() for s in args.conference_list.split(",") if s.strip()] if args.conference_list.strip() else None

    wb = open_workbook(cfg.seed_hub_xlsx)
    engine = SignalEngine(cache_dir=cache_dir)

    decisions_by_rowkey: Dict[str, Dict[str, Any]] = {}
    summary_rows: List[Dict[str, Any]] = []

    for ws in wb.worksheets:
        if cfg.worksheet_filter and ws.title not in cfg.worksheet_filter:
            continue

        required_cols = [
            cfg.person_name_column,
            cfg.person_org_column,
            cfg.github_column,
            cfg.openalex_column,
            cfg.scholar_column,
            cfg.semscholar_column,
            cfg.watchlist_flag_column,
            cfg.monitoring_tier_column,
        ]

        # GitHub repo column is optional; only required if present
        try:
            header = find_header_map(ws, required_cols=required_cols)
        except Exception as e:
            log.warning("[%s] Skipping: could not find required headers: %s", ws.title, e)
            continue

        col = header.col_to_idx
        gh_repo_idx = col.get(args.github_repo_column)

        processed = 0
        for row in iter_data_rows(ws, header.header_row):
            if args.limit and processed >= args.limit:
                break

            name = _s(read_cell(ws, row, col[cfg.person_name_column]))
            if not name:
                continue

            org = _s(read_cell(ws, row, col[cfg.person_org_column]))
            github = _s(read_cell(ws, row, col[cfg.github_column]))
            openalex = _s(read_cell(ws, row, col[cfg.openalex_column]))

            gh_repo = _s(read_cell(ws, row, gh_repo_idx)) if gh_repo_idx else ""

            bundle = engine.build_bundle(
                person_name=name,
                openalex_id_or_url=openalex,
                github_url=github,
                github_repo_url=gh_repo,
                conferences=conferences,
            )

            decision = evaluate_watchlist(bundle)

            # persist envelope locally
            env_paths = write_envelope(
                cache_dir=cache_dir,
                person_name=name,
                sheet=ws.title,
                row=row,
                envelope=decision.evidence_envelope,
            )

            rowkey = f"{ws.title}::{row}"
            decisions_by_rowkey[rowkey] = {
                "Watchlist_Flag": decision.watchlist_flag,
                "Monitoring_Tier": decision.monitoring_tier,
                "Envelope_Path": str(env_paths.envelope_path),
                "Score": decision.score,
            }

            summary = {
                "sheet": ws.title,
                "row": row,
                "name": name,
                "org": org,
                "watchlist_flag": decision.watchlist_flag,
                "monitoring_tier": decision.monitoring_tier,
                "score": round(decision.score, 4),
                "signals": decision.signals,
                "rationale": decision.rationale,
                "envelope_path": str(env_paths.envelope_path),
            }
            summary_rows.append(summary)

            if args.dump_json:
                log.info("Decision JSON: %s", json_dumps_safe(summary))
            else:
                log.info("[%s r%d] %s | %s | %s | score=%.2f | %s",
                         ws.title, row, name, decision.watchlist_flag, decision.monitoring_tier, decision.score,
                         "; ".join(decision.signals) if decision.signals else "no signals")

            processed += 1

    # Phase 2: Excel deterministic writeback
    if (not cfg.read_only) and cfg.excel_write_enabled:
        log.info("Phase 2: Excel writeback requested. dry_run=%s", cfg.dry_run)
        wb_res = writeback_operational_fields(cfg, decisions_by_rowkey=decisions_by_rowkey)
        if not wb_res.ok:
            log.error("Excel writeback failed: %s", json_dumps_safe({"errors": wb_res.errors}))
            return 3
        log.info("Excel writeback ok. wrote_any=%s records=%d", wb_res.wrote_any, len(wb_res.records))
        if wb_res.records:
            log.info("Write records sample: %s", json_dumps_safe([asdict(r) for r in wb_res.records[:10]]))

    # Phase 3: GPT narrative generation (cache only)
    if (not cfg.read_only) and cfg.gpt_writeback_enabled:
        log.info("Phase 3: GPT writeback requested.")
        out_dir = cache_dir / "gpt_narratives"
        out_dir.mkdir(parents=True, exist_ok=True)

        for s in summary_rows:
            envelope_path = Path(s["envelope_path"])
            try:
                envelope_payload = envelope_path.read_text(encoding="utf-8")
            except Exception:
                continue

            try:
                import json
                envelope_obj = json.loads(envelope_payload)
                envelope = envelope_obj.get("envelope") or {}
            except Exception:
                envelope = {}

            gpt_res = generate_narrative_from_envelope(cfg, envelope=envelope, cache_dir=cache_dir)
            if not gpt_res.ok:
                log.warning("GPT failed for %s: %s", s["name"], gpt_res.error)
                continue

            out_path = out_dir / (envelope_path.stem + "_narrative.json")
            out_path.write_text(json_dumps_safe(gpt_res.response_json), encoding="utf-8")
            log.info("GPT narrative saved: %s", str(out_path))

    log.info("Phase-Next run complete. rows=%d", len(summary_rows))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
PY

###############################################################################
# scripts/phase_next_run_readonly.sh  (Phase 1 default)
###############################################################################
cat <<'BASH' > scripts/phase_next_run_readonly.sh
#!/usr/bin/env bash
set -euo pipefail

# Phase 1: READ-ONLY (default safe)
export PHASE_NEXT_READ_ONLY=1
export PHASE_NEXT_EXCEL_WRITE_ENABLED=0
export PHASE_NEXT_GPT_WRITEBACK_ENABLED=0
export PHASE_NEXT_DRY_RUN=1

# REQUIRED: path to your Seed Hub workbook
# Example:
# export PHASE_NEXT_SEED_HUB_XLSX="data/AI_Talent_Landscape_Seed_Hub_Excel.xlsx"

python3 -m core.phase_next.run_phase_next "$@"
