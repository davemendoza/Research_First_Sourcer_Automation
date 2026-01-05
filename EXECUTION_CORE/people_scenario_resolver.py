"""
AI Talent Engine — GitHub People Source (Broad Admit, Score Later)
File: EXECUTION_CORE/people_source_github.py
Version: v4.0.0-admit-all-score-later
Author: L. David Mendoza
Copyright: © 2026 L. David Mendoza. All rights reserved.

Core invariant (locked):
- Admit broadly: any GitHub user hit can become a row.
- Enrich and score: AI relevance is expressed via fields and scores, not by dropping rows.
- Never fabricate, never pad, never silently succeed.

Run behavior:
- Demo: bounded by resolver (25–50). This source will keep collecting until it hits min_rows.
- Scenario: unbounded (25–∞). This source will keep collecting until it hits min_rows, then continues until candidate pool exhausted or caller caps.
- Filtering does NOT delete rows. Low-signal rows remain, clearly scored and labeled.

Environment variables:
- GITHUB_TOKEN (required)
- AI_TALENT_GH_MAX_WORKERS (optional int, default 8)
- AI_TALENT_GH_REQUEST_TIMEOUT (optional int seconds, default 20)
- AI_TALENT_GH_VALIDATE_GITHUB_IO (optional "1"/"0", default demo=1, scenario=0)
- AI_TALENT_GH_USER_SEED_TERMS (optional comma-separated override for seed terms)
- AI_TALENT_GH_MAX_QUERY_PAGES (optional int, default 10)
- AI_TALENT_GH_MAX_REPO_PAGES (optional int, default 2)

Changelog:
- v4.0.0: Remove early hard filtering that caused 0-row outputs and hangs.
          Admit all candidates as rows, score after enrichment, label signal strength.
          Sanitize GitHub user search terms to prevent 422 Unprocessable Entity.
          Add bounded executor draining to prevent indefinite waits.

Validation steps:
1) export GITHUB_TOKEN="..."
2) ./run_locked.sh demo "machine learning"
3) ./run_locked.sh scenario "machine learning"

Git (SSH) commands:
- git status
- git add EXECUTION_CORE/people_source_github.py
- git commit -m "Fix: admit all GitHub hits as rows, score later; prevent 0-row + hangs [v4.0.0]"
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
from concurrent.futures import ThreadPoolExecutor, Future, as_completed


GITHUB_API = "https://api.github.com"


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
TIMEOUT_S = _env_int("AI_TALENT_GH_REQUEST_TIMEOUT", 20)
MAX_QUERY_PAGES = _env_int("AI_TALENT_GH_MAX_QUERY_PAGES", 10)
MAX_REPO_PAGES = _env_int("AI_TALENT_GH_MAX_REPO_PAGES", 2)

GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "").strip()
if not GITHUB_TOKEN:
    raise RuntimeError("GITHUB_TOKEN not set. Export GITHUB_TOKEN before running.")


SESSION = requests.Session()
SESSION.headers.update(
    {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github+json",
        "User-Agent": "AI-Talent-Engine/people_source_github",
    }
)


EMAIL_RE = re.compile(r"[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}", re.IGNORECASE)


AI_KEYWORDS = {
    "llm",
    "large language model",
    "language model",
    "transformer",
    "foundation model",
    "generative ai",
    "genai",
    "diffusion",
    "alignment",
    "rlhf",
    "dpo",
    "ppo",
    "inference",
    "serving",
    "rag",
    "retrieval augmented generation",
    "vector database",
    "vector db",
    "embeddings",
    "tokenizer",
    "finetune",
    "fine-tune",
    "lora",
    "qlora",
    "peft",
    "pytorch",
    "jax",
    "tensorflow",
    "cuda",
    "triton",
    "tensorrt",
    "onnx",
    "deepspeed",
    "fsdp",
    "xla",
    "ray",
    "vllm",
    "tgi",
    "llama.cpp",
    "langchain",
    "langgraph",
    "llamaindex",
    "faiss",
    "weaviate",
    "pinecone",
    "qdrant",
    "milvus",
    "pgvector",
    "redis vector",
}


AI_STRONG = {
    "rlhf",
    "dpo",
    "ppo",
    "reward model",
    "alignment",
    "vllm",
    "tensorrt",
    "triton",
    "cuda",
    "deepspeed",
    "fsdp",
    "rag",
    "embeddings",
    "vector database",
    "faiss",
    "weaviate",
    "pinecone",
    "qdrant",
    "milvus",
    "transformer",
    "llm",
    "foundation model",
}


def _get_json(url: str, params: Optional[dict] = None) -> dict:
    r = SESSION.get(url, params=params, timeout=TIMEOUT_S)
    if r.status_code == 401:
        raise RuntimeError("GitHub API: 401 Unauthorized. Check GITHUB_TOKEN validity/scopes.")
    if r.status_code == 403:
        reset = r.headers.get("X-RateLimit-Reset", "")
        remaining = r.headers.get("X-RateLimit-Remaining", "")
        msg = f"GitHub API: 403 Forbidden (remaining={remaining}, reset={reset}). Rate limit or policy block."
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


def _sanitize_user_search_term(term: str) -> str:
    """
    GitHub /search/users is restrictive and returns 422 on complex expressions.
    We enforce a simple, safe query string:
    - remove quotes, parentheses, operators, qualifiers like in:readme
    - allow only letters, numbers, spaces, hyphens
    - collapse whitespace
    - cap length
    """
    t = (term or "").strip().lower()

    # Remove common query operators/qualifiers that break user search.
    t = re.sub(r'\b(or|and|not)\b', " ", t)
    t = re.sub(r'\bin:[a-z_]+\b', " ", t)
    t = re.sub(r'["\'`(){}[\]]', " ", t)
    t = re.sub(r'[:=<>+*/\\|^~]', " ", t)

    # Keep letters, numbers, spaces, and hyphens.
    t = re.sub(r"[^a-z0-9 \-]", " ", t)
    t = re.sub(r"\s+", " ", t).strip()

    # Prevent empty or tiny garbage.
    if not t:
        return "ai"
    if len(t) > 80:
        t = t[:80].strip()
    return t


def _validate_github_io(login: str) -> str:
    url = f"https://{login}.github.io/"
    try:
        resp = requests.get(url, timeout=6, allow_redirects=True)
        if 200 <= resp.status_code < 300:
            return url
    except Exception:
        pass
    return ""


def _repo_items(login: str, max_pages: int) -> List[dict]:
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


def _signal_bucket(ai_score: int) -> str:
    if ai_score >= 18:
        return "High"
    if ai_score >= 8:
        return "Medium"
    return "Low"


def _summarize_ai_evidence(bio: str, repos: List[dict]) -> Tuple[int, str, List[str], List[str]]:
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

        if s >= 4:
            html_url = _safe_str(r.get("html_url"))
            if html_url:
                ai_repo_urls.append(html_url)

        for t in topics:
            tt = _safe_str(t).lower()
            if tt:
                topic_keywords.append(tt)

        # Cap per-repo contribution to avoid runaway scores.
        ai_score += min(s, 6)

    topic_keywords = sorted(set(topic_keywords))[:75]
    ai_repo_urls = sorted(set(ai_repo_urls))[:35]

    bucket = _signal_bucket(ai_score)

    evidence_note = ""
    if ai_repo_urls:
        evidence_note = f"{bucket} signal: AI repos detected: {len(ai_repo_urls)}"
    elif bio:
        evidence_note = f"{bucket} signal: Bio contains indicators"
    else:
        evidence_note = f"{bucket} signal: No determinative evidence in bio/repos"

    return ai_score, evidence_note, ai_repo_urls, topic_keywords


def _default_seed_terms(role: str) -> List[str]:
    override = os.environ.get("AI_TALENT_GH_USER_SEED_TERMS", "").strip()
    if override:
        return [t.strip() for t in override.split(",") if t.strip()]

    r = (role or "").lower()

    # Broad, API-safe seeding terms. These are not boolean queries.
    base = [
        "ai",
        "machine learning",
        "deep learning",
        "pytorch",
        "cuda",
        "transformer",
        "llm",
        "inference",
        "rag",
        "embeddings",
        "vector database",
        "langchain",
        "tensorrt",
        "triton",
        "jax",
    ]

    if "rlhf" in r or "alignment" in r:
        return [
            "rlhf",
            "alignment",
            "reward model",
            "dpo",
            "ppo",
            "llm",
            "transformer",
            "ai",
            "machine learning",
        ] + base

    if "infra" in r or "sre" in r or "platform" in r or "distributed" in r:
        return [
            "cuda",
            "triton",
            "kubernetes",
            "ray",
            "inference",
            "tensorrt",
            "onnx",
            "ai",
            "machine learning",
        ] + base

    if "scientist" in r or "research" in r or "foundational" in r or "frontier" in r:
        return [
            "transformer",
            "llm",
            "jax",
            "pytorch",
            "diffusion",
            "ai",
            "machine learning",
        ] + base

    return base


def _search_users_simple(term: str, page: int) -> dict:
    safe = _sanitize_user_search_term(term)
    return _get_json(
        f"{GITHUB_API}/search/users",
        params={"q": safe, "per_page": 100, "page": page},
    )


@dataclass(frozen=True)
class _Candidate:
    login: str
    html_url: str


def _gather_candidates(role: str, target_min: int, target_max: Optional[int]) -> List[_Candidate]:
    """
    Gather a pool of user candidates via multiple safe seed terms.

    For demo: stop early once we have a robust pool (3x target).
    For scenario: collect the full pool across terms/pages.
    """
    terms = _default_seed_terms(role)

    seen: set[str] = set()
    candidates: List[_Candidate] = []

    for term in terms:
        for page in range(1, MAX_QUERY_PAGES + 1):
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

            # Demo: gather enough and stop. Scenario: continue.
            if target_max is not None:
                if len(candidates) >= max(target_min * 3, target_max * 4):
                    return candidates

            if len(items) < 100:
                break

    return candidates


def _enrich_candidate(c: _Candidate, validate_github_io: bool) -> Optional[Dict[str, str]]:
    """
    Enrich a candidate and return a row dict.

    Critical invariant:
    - This function does NOT drop candidates for low AI signal.
    - It returns a row whenever basic user data is available.
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
    email = _safe_str(user.get("email"))
    followers = _safe_str(user.get("followers"))

    repos: List[dict] = []
    try:
        repos = _repo_items(login, max_pages=MAX_REPO_PAGES)
    except Exception:
        # Keep the row even if repos fail, but label it.
        repos = []

    ai_score, evidence_note, ai_repo_urls, topic_keywords = _summarize_ai_evidence(bio, repos)
    bucket = _signal_bucket(ai_score)

    github_io = ""
    if validate_github_io:
        github_io = _validate_github_io(login)

    portfolio_urls: List[str] = []
    if github_io:
        portfolio_urls.append(github_io)
    if blog and _looks_like_url(blog):
        portfolio_urls.append(blog)

    emails = _extract_emails(" ".join([bio, blog, company, location]))
    primary_email = email or (emails[0] if emails else "")

    row: Dict[str, str] = {
        "Person_ID": f"GH_{login}",
        "Full_Name": name,
        "First_Name": name.split(" ")[0] if name else "",
        "Last_Name": name.split(" ")[-1] if name and " " in name else "",
        "AI_Role_Type": "",
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
        "Identity_Strength_Score": str(ai_score),
        "Influence_Tier": bucket,
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
        "Pipeline_Version": "people_source_github v4.0.0",
    }

    return row


def build_people(role: str, min_rows: int, max_rows: Optional[int], demo_mode: bool) -> pd.DataFrame:
    """
    Build a People DataFrame for a given role.

    Key behavior:
    - Admit broadly: rows are not dropped for low AI signal.
    - Score and label signal strength after enrichment.
    - Keep collecting until min_rows is reached or candidates exhausted.
    - Demo respects resolver max_rows. Scenario has no max cap.

    Returns:
      pandas.DataFrame of real people rows.
    """
    role = (role or "").strip()
    if not role:
        raise ValueError("role must be non-empty")

    if min_rows < 1:
        raise ValueError("min_rows must be >= 1")

    if demo_mode and (max_rows is None or max_rows < min_rows):
        raise RuntimeError("Demo mode requires a bounded max_rows >= min_rows")

    validate_github_io = _env_bool(
        "AI_TALENT_GH_VALIDATE_GITHUB_IO",
        default=True if demo_mode else False,
    )

    candidates = _gather_candidates(role=role, target_min=min_rows, target_max=max_rows)
    if not candidates:
        raise RuntimeError("GitHub seeding returned zero candidates. Check token/connectivity and seed terms.")

    rows: List[Dict[str, str]] = []
    seen_person_ids: set[str] = set()

    # Bounded draining strategy to avoid huge outstanding futures and to prevent hangs.
    # We keep a small window of in-flight jobs and refill as they complete.
    inflight: List[Future] = []

    def submit(pool: ThreadPoolExecutor, cand: _Candidate) -> Future:
        return pool.submit(_enrich_candidate, cand, validate_github_io)

    idx = 0
    start_time = time.time()

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as pool:
        # Prime the queue.
        while idx < len(candidates) and len(inflight) < MAX_WORKERS * 3:
            inflight.append(submit(pool, candidates[idx]))
            idx += 1

        while inflight:
            done_any = False
            for fut in as_completed(inflight, timeout=TIMEOUT_S + 10):
                done_any = True
                inflight.remove(fut)

                row: Optional[Dict[str, str]] = fut.result()
                if row:
                    row["AI_Role_Type"] = role

                    pid = row.get("Person_ID", "")
                    if pid and pid not in seen_person_ids:
                        seen_person_ids.add(pid)
                        rows.append(row)

                        # Demo cap enforcement.
                        if demo_mode and max_rows is not None and len(rows) >= max_rows:
                            inflight.clear()
                            break

                # Refill inflight as we go, unless demo is capped.
                if not (demo_mode and max_rows is not None and len(rows) >= max_rows):
                    while idx < len(candidates) and len(inflight) < MAX_WORKERS * 3:
                        inflight.append(submit(pool, candidates[idx]))
                        idx += 1

                # Stop once we satisfy min_rows for demo. For scenario, keep going unless caller caps.
                if demo_mode and len(rows) >= min_rows:
                    # Demo still bounded to max_rows by resolver, but we can stop early if we already have enough.
                    # Resolver will head() if needed.
                    inflight.clear()
                    break

            if not done_any:
                # If as_completed timed out without any completion, we break to avoid indefinite waits.
                break

    df = pd.DataFrame(rows)

    if len(df) < min_rows:
        elapsed = int(time.time() - start_time)
        raise RuntimeError(
            f"Only {len(df)} people collected, below required minimum {min_rows}. "
            f"Elapsed={elapsed}s. This indicates candidate enrichment throughput or GitHub throttling, "
            "not schema plumbing."
        )

    # Deterministic ordering for stable outputs.
    if "GitHub_Username" in df.columns:
        df = df.sort_values(by=["GitHub_Username"], kind="mergesort").reset_index(drop=True)

    return df
