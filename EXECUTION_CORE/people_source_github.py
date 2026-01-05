"""
AI Talent Engine — GitHub People Source (Broad Seed, Late Filter)
Version: v3.0.0-broad-seed-late-filter
Author: L. David Mendoza
Copyright: © 2026 L. David Mendoza. All rights reserved.

Purpose:
- Seed broadly using GitHub User Search (simple keyword queries only).
- Enrich each candidate using GitHub REST endpoints (user + repos).
- Apply strict AI relevance filtering AFTER enrichment (late filter).
- Return real people only. Never fabricate. Never pad.

Locked run behavior:
- Demo: produce 25–50 real people (bounded by max_rows).
- Scenario: produce 25–∞ real people (no max cap), bounded by GitHub search limits and available results.

Operational notes:
- GitHub user search supports only simple query strings (no OR, no parentheses, no in:readme).
- Each user-search query yields at most ~1000 results (GitHub search constraint).
- To scale scenario runs to hundreds or thousands, we iterate multiple broad seed terms and pages.

Environment variables:
- GITHUB_TOKEN (required)
- AI_TALENT_GH_USER_SEED_TERMS (optional, comma-separated override for seed terms)
- AI_TALENT_GH_MAX_WORKERS (optional, default 8)
- AI_TALENT_GH_REQUEST_TIMEOUT (optional seconds, default 15)
- AI_TALENT_GH_VALIDATE_GITHUB_IO (optional: "1" or "0", default: demo=1, scenario=0)
- AI_TALENT_GH_MIN_AI_SCORE (optional int, default 3)

Validation steps:
1) export GITHUB_TOKEN="..."
2) ./run_locked.sh demo "machine learning"
3) ./run_locked.sh scenario "machine learning"

Git (SSH) commands:
- git status
- git add EXECUTION_CORE/people_source_github.py
- git commit -m "Fix: broad GitHub seeding + late AI filtering; scenario unbounded scale [v3.0.0]"
- git push
"""

from __future__ import annotations

import os
import re
import time
from dataclasses import dataclass
from typing import Dict, Iterable, List, Optional, Tuple
from urllib.parse import urlparse

import pandas as pd
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed


GITHUB_API = "https://api.github.com"


# ----------------------------
# Config
# ----------------------------

def _env_int(name: str, default: int) -> int:
    v = os.environ.get(name, "").strip()
    if not v:
        return default
    try:
        return int(v)
    except ValueError:
        return default


def _env_bool(name: str, default: bool) -> bool:
    v = os.environ.get(name, "").strip().lower()
    if not v:
        return default
    return v in ("1", "true", "yes", "y", "on")


MAX_WORKERS = _env_int("AI_TALENT_GH_MAX_WORKERS", 8)
TIMEOUT_S = _env_int("AI_TALENT_GH_REQUEST_TIMEOUT", 15)
MIN_AI_SCORE = _env_int("AI_TALENT_GH_MIN_AI_SCORE", 3)

GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "").strip()
if not GITHUB_TOKEN:
    raise RuntimeError("GITHUB_TOKEN not set. Export GITHUB_TOKEN before running.")

SESSION = requests.Session()
SESSION.headers.update({
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github+json",
    "User-Agent": "AI-Talent-Engine/people_source_github",
})


# ----------------------------
# AI signal dictionaries (late filter)
# ----------------------------

AI_KEYWORDS = {
    # core
    "llm", "large language model", "language model", "transformer", "foundation model",
    "generative ai", "genai", "diffusion", "alignment", "rlhf", "dpo", "ppo",
    "inference", "serving", "rag", "retrieval augmented generation", "vector database",
    "embeddings", "tokenizer", "finetune", "fine-tune", "lora", "qlora", "peft",
    # tools and stacks
    "pytorch", "jax", "tensorflow", "cuda", "triton", "tensorrt", "onnx",
    "deepspeed", "fsdp", "xla", "ray", "vllm", "tgi", "llama.cpp",
    "langchain", "llamaindex", "faiss", "weaviate", "pinecone", "qdrant", "milvus",
}

# Stronger indicators (boosts score)
AI_STRONG = {
    "rlhf", "dpo", "ppo", "reward model", "alignment",
    "vllm", "tensorrt", "triton", "cuda", "deepspeed", "fsdp",
    "rag", "embeddings", "vector database", "faiss", "weaviate", "pinecone", "qdrant", "milvus",
    "transformer", "llm", "foundation model",
}

EMAIL_RE = re.compile(r"[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}", re.IGNORECASE)


# ----------------------------
# Helpers
# ----------------------------

def _get_json(url: str, params: Optional[dict] = None) -> dict:
    r = SESSION.get(url, params=params, timeout=TIMEOUT_S)
    if r.status_code == 401:
        raise RuntimeError("GitHub API: 401 Unauthorized. Check GITHUB_TOKEN validity/scopes.")
    if r.status_code == 403:
        # Rate limit or abuse detection. Provide actionable message.
        reset = r.headers.get("X-RateLimit-Reset", "")
        remaining = r.headers.get("X-RateLimit-Remaining", "")
        msg = f"GitHub API: 403 Forbidden (remaining={remaining}, reset={reset})."
        raise RuntimeError(msg)
    r.raise_for_status()
    return r.json()


def _safe_str(x: object) -> str:
    return (str(x).strip()) if x is not None else ""


def _normalize_url(url: str) -> str:
    u = _safe_str(url)
    if not u:
        return ""
    if u.startswith("http://") or u.startswith("https://"):
        return u
    # GitHub "blog" sometimes stored without scheme
    return "https://" + u


def _looks_like_url(u: str) -> bool:
    try:
        p = urlparse(u)
        return p.scheme in ("http", "https") and bool(p.netloc)
    except Exception:
        return False


def _extract_emails(text: str) -> List[str]:
    if not text:
        return []
    return sorted(set(EMAIL_RE.findall(text)))


def _validate_github_io(login: str) -> str:
    # Only return github.io if it actually responds.
    url = f"https://{login}.github.io/"
    try:
        resp = requests.get(url, timeout=6, allow_redirects=True)
        if 200 <= resp.status_code < 300:
            return url
    except Exception:
        pass
    return ""


def _repo_items(login: str, max_pages: int = 2) -> List[dict]:
    # Pull up to ~200 repos (2 pages * 100). Enough for signal extraction.
    repos: List[dict] = []
    for page in range(1, max_pages + 1):
        data = _get_json(
            f"{GITHUB_API}/users/{login}/repos",
            params={"per_page": 100, "page": page, "sort": "updated"},
        )
        if not data:
            break
        repos.extend(data)
        if len(data) < 100:
            break
    return repos


def _ai_score_from_text(text: str) -> int:
    t = (text or "").lower()
    score = 0
    for kw in AI_KEYWORDS:
        if kw in t:
            score += 1
    for kw in AI_STRONG:
        if kw in t:
            score += 2
    return score


def _summarize_ai_evidence(bio: str, repos: List[dict]) -> Tuple[int, str, List[str], List[str]]:
    """
    Returns:
      - ai_score (int)
      - evidence_note (str)
      - ai_repo_urls (list[str])
      - topic_keywords (list[str])
    """
    bio = bio or ""
    ai_score = _ai_score_from_text(bio)

    ai_repo_urls: List[str] = []
    topic_keywords: List[str] = []

    for r in repos:
        name = _safe_str(r.get("name"))
        desc = _safe_str(r.get("description"))
        topics = r.get("topics") or []
        lang = _safe_str(r.get("language"))

        blob = " ".join([name, desc, lang, " ".join([_safe_str(t) for t in topics])]).lower()
        s = _ai_score_from_text(blob)

        if s >= 3:
            html_url = _safe_str(r.get("html_url"))
            if html_url:
                ai_repo_urls.append(html_url)

        for t in topics:
            tt = _safe_str(t).lower()
            if tt:
                topic_keywords.append(tt)

        ai_score += min(s, 6)

    topic_keywords = sorted(set(topic_keywords))[:50]
    ai_repo_urls = sorted(set(ai_repo_urls))[:25]

    evidence_note = ""
    if ai_repo_urls:
        evidence_note = f"AI repos detected: {len(ai_repo_urls)}"
    elif bio:
        evidence_note = "Bio contains AI indicators"
    else:
        evidence_note = "No determinative AI evidence found"

    return ai_score, evidence_note, ai_repo_urls, topic_keywords


def _default_seed_terms(role: str) -> List[str]:
    override = os.environ.get("AI_TALENT_GH_USER_SEED_TERMS", "").strip()
    if override:
        return [t.strip() for t in override.split(",") if t.strip()]

    # Role is not used as a boolean query. It only influences which broad terms we attempt first.
    r = role.lower()
    base = ["ai", "machine learning", "deep learning", "pytorch", "cuda", "transformer", "llm", "inference", "rag"]

    if "rlhf" in r or "alignment" in r:
        return ["rlhf", "alignment", "reward model", "dpo", "ppo", "ai", "machine learning"] + base
    if "infra" in r or "sre" in r or "platform" in r or "distributed" in r:
        return ["cuda", "triton", "kubernetes", "ray", "inference", "tensorrt", "ai"] + base
    if "scientist" in r or "research" in r or "foundational" in r or "frontier" in r:
        return ["transformer", "llm", "jax", "pytorch", "diffusion", "ai", "machine learning"] + base

    return base


def _search_users_simple(term: str, page: int) -> dict:
    # GitHub users search must be simple. No OR, no parentheses, no in:readme.
    return _get_json(
        f"{GITHUB_API}/search/users",
        params={"q": term, "per_page": 100, "page": page},
    )


@dataclass(frozen=True)
class _Candidate:
    login: str
    html_url: str


def _gather_candidates(role: str, target_min: int, target_max: Optional[int]) -> List[_Candidate]:
    """
    Gather a pool of user candidates via multiple simple seed terms.
    Scenario scaling comes from iterating many terms and pages.
    """
    terms = _default_seed_terms(role)
    seen: set[str] = set()
    candidates: List[_Candidate] = []

    # GitHub search constraint: up to ~1000 results per query term (10 pages * 100).
    # For scenario scale, we use multiple terms.
    for term in terms:
        for page in range(1, 11):
            data = _search_users_simple(term, page)
            items = data.get("items", [])
            if not items:
                break

            for it in items:
                login = _safe_str(it.get("login"))
                html = _safe_str(it.get("html_url"))
                if not login or login in seen:
                    continue
                seen.add(login)
                candidates.append(_Candidate(login=login, html_url=html))

                # If demo max_rows exists, we can stop early once we have a reasonable pool.
                if target_max is not None and len(candidates) >= max(target_min * 3, target_max * 3):
                    return candidates

            if len(items) < 100:
                break

    return candidates


def _enrich_candidate(c: _Candidate, validate_github_io: bool) -> Optional[Dict[str, str]]:
    """
    Enrich a candidate and return a dict of populated fields if relevant, else None.
    Late filter happens here based on enriched evidence.
    """
    user = _get_json(f"{GITHUB_API}/users/{c.login}")
    login = _safe_str(user.get("login"))
    if not login:
        return None

    name = _safe_str(user.get("name"))
    bio = _safe_str(user.get("bio"))
    blog = _normalize_url(_safe_str(user.get("blog")))
    company = _safe_str(user.get("company"))
    location = _safe_str(user.get("location"))
    email = _safe_str(user.get("email"))  # often blank
    followers = _safe_str(user.get("followers"))

    repos = _repo_items(login, max_pages=2)

    ai_score, evidence_note, ai_repo_urls, topic_keywords = _summarize_ai_evidence(bio, repos)

    if ai_score < MIN_AI_SCORE:
        return None

    github_io = ""
    if validate_github_io:
        github_io = _validate_github_io(login)

    # Prefer using validated github.io. If blog is a URL and looks like a personal site, treat as portfolio.
    portfolio_urls: List[str] = []
    if github_io:
        portfolio_urls.append(github_io)
    if blog and _looks_like_url(blog):
        portfolio_urls.append(blog)

    # Light email discovery from bio + blog string only (no scraping content here).
    # Deep scraping belongs in a dedicated enrichment stage.
    emails = _extract_emails(" ".join([bio, blog, company, location]))
    primary_email = email or (emails[0] if emails else "")

    # Build row (canonical will add missing columns later).
    row: Dict[str, str] = {
        "Person_ID": f"GH_{login}",
        "Full_Name": name,
        "First_Name": name.split(" ")[0] if name else "",
        "Last_Name": name.split(" ")[-1] if name and " " in name else "",
        "AI_Role_Type": "",  # set by build_people
        "Primary_Email": primary_email,
        "Primary_Phone": "",
        "Current_Title": "",
        "Current_Company": company.replace("@", "").strip() if company else "",
        "Location_City": "",
        "Location_State": "",
        "Location_Country": "",
        "LinkedIn_Public_URL": "",
        "Resume_URL": "",
        "GitHub_Username": login,
        "GitHub_URL": _safe_str(user.get("html_url")) or c.html_url,
        "GitHub_IO_URL": github_io,
        "Key_GitHub_AI_Repos": "; ".join(ai_repo_urls),
        "Repo_Topics_Keywords": "; ".join(topic_keywords),
        "GitHub_Repo_Evidence_Why": evidence_note,
        "GitHub_Followers": followers,
        "Portfolio_URLs": "; ".join(sorted(set(portfolio_urls))),
        "Personal_Website_URLs": "",
        "Academic_Homepage_URLs": "",
        "Blog_URLs": blog if blog else "",
        "X_URLs": "",
        "YouTube_URLs": "",
        "Open_Source_Impact_Notes": "",
        "Field_Level_Provenance_JSON": "",
        "Row_Validity_Status": "OK",
        "Pipeline_Version": "people_source_github v3.0.0",
    }

    return row


def build_people(role: str, min_rows: int, max_rows: Optional[int], demo_mode: bool) -> pd.DataFrame:
    """
    Build a People DataFrame for a given role.

    Demo:
      - bounded to 25–50 (max_rows must be provided by resolver)
    Scenario:
      - min 25, no max cap (max_rows is None)
      - scales by iterating seed terms and pages, bounded by GitHub search constraints

    Returns:
      pandas.DataFrame with real people rows (may be larger than min_rows in scenario).
    """
    role = (role or "").strip()
    if not role:
        raise ValueError("role must be non-empty")

    if min_rows < 1:
        raise ValueError("min_rows must be >= 1")

    if demo_mode and (max_rows is None or max_rows < min_rows):
        raise RuntimeError("Demo mode requires a bounded max_rows >= min_rows")

    # Demo validates github.io by default. Scenario defaults off for throughput.
    validate_github_io = _env_bool(
        "AI_TALENT_GH_VALIDATE_GITHUB_IO",
        default=True if demo_mode else False
    )

    candidates = _gather_candidates(role=role, target_min=min_rows, target_max=max_rows)

    if not candidates:
        raise RuntimeError("GitHub seeding returned zero candidates. Check connectivity/token and seed terms.")

    rows: List[Dict[str, str]] = []
    seen_person_ids: set[str] = set()

    # Enrich in parallel for throughput and real-world scale.
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as pool:
        futures = {pool.submit(_enrich_candidate, c, validate_github_io): c for c in candidates}

        for fut in as_completed(futures):
            try:
                row = fut.result()
            except Exception as e:
                # Fail fast for token/rate-limit and similar systemic issues.
                raise

            if not row:
                continue

            # Set role after enrichment (keeps sourcing generic, filtering evidence-driven).
            row["AI_Role_Type"] = role

            pid = row.get("Person_ID", "")
            if not pid or pid in seen_person_ids:
                continue

            seen_person_ids.add(pid)
            rows.append(row)

            # Demo cap enforcement.
            if demo_mode and max_rows is not None and len(rows) >= max_rows:
                break

    df = pd.DataFrame(rows)

    # Hard integrity gates.
    if len(df) < min_rows:
        raise RuntimeError(
            f"Only {len(df)} qualifying people found, below required minimum {min_rows}. "
            "This is a sourcing/relevance issue, not a schema issue. "
            "Adjust seed terms or MIN_AI_SCORE if needed."
        )

    # Deterministic ordering: stable sort by GitHub username.
    if "GitHub_Username" in df.columns:
        df = df.sort_values(by=["GitHub_Username"], kind="mergesort").reset_index(drop=True)

    return df
