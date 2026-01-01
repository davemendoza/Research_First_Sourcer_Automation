#!/usr/bin/env python3
"""
AI Talent Engine – People Pipeline (Hardened, Bearer Auth)
© 2025 L. David Mendoza

Version: v1.0.0-people-enum-hardfail
Last Updated: 2026-01-01

Purpose
- Enumerate REAL GitHub users for a given scenario using the GitHub Search API.
- Enforce non-empty upstream people inventory, or hard-fail with explicit reasons.
- Produce a people_master.csv with real GitHub usernames (minimum viable output: >= 25).
- Emit clear console logs: query, pages fetched, counts accepted, discarded, final totals.
- Write discard reasons to outputs/people/discards.csv for auditability.

Non-negotiables enforced here
- REAL DATA ONLY: No synthetic people, no demo stubs.
- HARD FAIL on empty or under-minimum enumeration.
- Explicit logging of query, page counts, API response counts, and rejection reasons.
- Uses Authorization: Bearer <token> from env var GITHUB_TOKEN (required).
"""

from __future__ import annotations

import argparse
import csv
import datetime as dt
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from typing import Dict, Iterable, List, Optional, Set, Tuple


GITHUB_API = "https://api.github.com"
SEARCH_USERS_ENDPOINT = f"{GITHUB_API}/search/users"
USER_ENDPOINT_TMPL = f"{GITHUB_API}/users/{{login}}"


DEFAULT_MIN_PEOPLE = 25
DEFAULT_PER_PAGE = 100
DEFAULT_MAX_PAGES_PER_QUERY = 5
DEFAULT_DETAIL_LOOKUPS = 60  # keep bounded; usernames are the minimum requirement


@dataclass(frozen=True)
class Candidate:
    login: str
    html_url: str
    score: float


@dataclass
class PersonRow:
    GitHub_Username: str
    GitHub_URL: str
    Name: str
    Company: str
    Blog: str
    Location: str
    Email: str
    Bio: str
    Followers: str
    Following: str
    Public_Repos: str
    Created_At: str
    Updated_At: str
    Source_Scenario: str
    Source_Query: str
    Source_Page: str
    Source_Rank: str
    Retrieved_At_UTC: str


def eprint(msg: str) -> None:
    print(msg, file=sys.stderr)


def utc_now_iso() -> str:
    return dt.datetime.utcnow().replace(microsecond=0).isoformat() + "Z"


def safe_mkdir(path: str) -> None:
    os.makedirs(path, exist_ok=True)


def build_headers(token: str) -> Dict[str, str]:
    return {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {token}",
        "User-Agent": "AI-Talent-Engine-People-Pipeline",
        "X-GitHub-Api-Version": "2022-11-28",
    }


def http_get_json(url: str, headers: Dict[str, str], timeout: int = 30, retries: int = 4) -> Tuple[dict, Dict[str, str], int]:
    """
    Returns: (json_obj, response_headers, status_code)
    Hard fails on persistent errors with explicit output.
    """
    last_err: Optional[str] = None
    for attempt in range(1, retries + 1):
        req = urllib.request.Request(url, headers=headers, method="GET")
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                status = getattr(resp, "status", 200)
                resp_headers = {k: v for k, v in resp.headers.items()}
                body = resp.read().decode("utf-8", errors="replace")
                try:
                    return json.loads(body), resp_headers, status
                except json.JSONDecodeError:
                    raise RuntimeError(f"Non-JSON response from GitHub. Status={status}. Body(head)= {body[:300]}")
        except urllib.error.HTTPError as he:
            status = getattr(he, "code", 0)
            body = he.read().decode("utf-8", errors="replace") if hasattr(he, "read") else ""
            resp_headers = dict(he.headers.items()) if getattr(he, "headers", None) else {}
            last_err = f"HTTPError {status} for URL: {url}\nBody(head)= {body[:400]}"
            # Auth and forbidden should fail fast with clear messaging.
            if status in (401, 403):
                rate_rem = resp_headers.get("X-RateLimit-Remaining", "")
                rate_reset = resp_headers.get("X-RateLimit-Reset", "")
                hint = ""
                if rate_rem == "0" and rate_reset:
                    try:
                        reset_ts = int(rate_reset)
                        reset_dt = dt.datetime.utcfromtimestamp(reset_ts).replace(microsecond=0).isoformat() + "Z"
                        hint = f"\nRate limit exhausted. Resets at {reset_dt} UTC."
                    except Exception:
                        hint = "\nRate limit exhausted. Reset time present but could not parse."
                raise RuntimeError(
                    "GitHub API authorization or access failure.\n"
                    f"{last_err}\n"
                    "Checks to perform (no token re-creation):\n"
                    "- Confirm env var GITHUB_TOKEN is exported in this shell.\n"
                    "- Confirm Authorization header is 'Bearer <token>' (this script enforces that).\n"
                    "- Confirm token scopes allow 'Search' and 'Users' read access for public data.\n"
                    f"{hint}"
                )
            # Backoff for transient issues.
            sleep_s = min(2 ** attempt, 12)
            time.sleep(sleep_s)
            continue
        except Exception as ex:
            last_err = f"Request failure for URL: {url}\nError: {type(ex).__name__}: {ex}"
            sleep_s = min(2 ** attempt, 12)
            time.sleep(sleep_s)
            continue

    raise RuntimeError(f"GitHub request failed after {retries} attempts.\nLast error:\n{last_err}")


def log_rate_limit(resp_headers: Dict[str, str]) -> None:
    rem = resp_headers.get("X-RateLimit-Remaining", "")
    lim = resp_headers.get("X-RateLimit-Limit", "")
    reset = resp_headers.get("X-RateLimit-Reset", "")
    if rem or lim or reset:
        reset_str = ""
        if reset:
            try:
                reset_ts = int(reset)
                reset_str = dt.datetime.utcfromtimestamp(reset_ts).replace(microsecond=0).isoformat() + "Z"
            except Exception:
                reset_str = reset
        msg = f"RateLimit: remaining={rem} limit={lim}"
        if reset_str:
            msg += f" reset_utc={reset_str}"
        print(msg)


def is_bot_login(login: str) -> bool:
    l = login.lower().strip()
    if l.endswith("[bot]"):
        return True
    if l.endswith("-bot") or l.endswith("_bot") or l.startswith("bot-"):
        return True
    return False


def scenario_queries(scenario: str) -> List[str]:
    """
    Scenario query sets for GitHub Search Users.

    Notes:
    - GitHub user search supports qualifiers like in:bio and in:username.
    - We prefer in:bio to reduce random results.
    - We deliberately include broader fallback tiers to guarantee real results,
      while still remaining aligned to AI and systems work.
    """
    s = (scenario or "").strip().lower()

    # Tier A: scenario-specific.
    if s in ("frontier", "frontier_ai", "frontier-ai", "foundational", "research"):
        tier_a = [
            '"flashattention" in:bio',
            '"tensorRT" in:bio',
            '"triton" in:bio cuda',
            '"jax" in:bio "transformer"',
            '"llm" in:bio "training" cuda',
            '"mixture of experts" in:bio',
            '"fsdp" in:bio "pytorch"',
            '"deepspeed" in:bio "training"',
        ]
    elif s in ("rlhf", "alignment", "safety"):
        tier_a = [
            '"rlhf" in:bio',
            '"dpo" in:bio "llm"',
            '"ppo" in:bio "rlhf"',
            '"reward model" in:bio',
            '"sft" in:bio "llm"',
            '"lora" in:bio "alignment"',
            '"qlora" in:bio "rlhf"',
        ]
    elif s in ("infra", "sre", "platform", "gpu_infra", "gpu-infra"):
        tier_a = [
            '"kubernetes" in:bio gpu',
            '"nvidia" in:bio "k8s"',
            '"nccl" in:bio "distributed"',
            '"slurm" in:bio gpu',
            '"inference" in:bio "tensorrt"',
            '"ray" in:bio "serve"',
            '"gpunet" in:bio',
        ]
    elif s in ("applied", "rag", "agents", "llmops"):
        tier_a = [
            '"rag" in:bio "langchain"',
            '"llamaindex" in:bio rag',
            '"vector database" in:bio',
            '"weaviate" in:bio rag',
            '"pinecone" in:bio rag',
            '"qdrant" in:bio rag',
            '"vllm" in:bio inference',
        ]
    else:
        tier_a = [
            '"llm" in:bio',
            '"genai" in:bio',
            '"machine learning" in:bio "pytorch"',
            '"transformers" in:bio',
            '"inference" in:bio "cuda"',
        ]

    # Tier B: broader but still clearly AI + engineering.
    tier_b = [
        '"pytorch" in:bio "cuda"',
        '"transformer" in:bio "pytorch"',
        '"mlops" in:bio "kubernetes"',
        '"distributed systems" in:bio "gpu"',
        '"llmops" in:bio',
        '"vector db" in:bio',
    ]

    # Tier C: last-resort, still technical, intended to avoid zero-results.
    tier_c = [
        '"machine learning" in:bio',
        '"deep learning" in:bio',
        '"pytorch" in:bio',
        '"kubernetes" in:bio',
    ]

    return tier_a + tier_b + tier_c


def build_search_url(q: str, per_page: int, page: int) -> str:
    params = {"q": q, "per_page": str(per_page), "page": str(page)}
    return SEARCH_USERS_ENDPOINT + "?" + urllib.parse.urlencode(params)


def build_user_url(login: str) -> str:
    return USER_ENDPOINT_TMPL.format(login=urllib.parse.quote(login))


def enumerate_candidates(
    token: str,
    scenario: str,
    min_people: int,
    per_page: int,
    max_pages_per_query: int,
    hard_cap_total: int,
) -> Tuple[List[Tuple[Candidate, str, int, int]], List[Tuple[str, str]]]:
    """
    Returns:
    - accepted: list of (Candidate, source_query, source_page, source_rank)
    - discards: list of (login_or_marker, reason)
    """
    headers = build_headers(token)
    queries = scenario_queries(scenario)

    accepted: List[Tuple[Candidate, str, int, int]] = []
    discards: List[Tuple[str, str]] = []
    seen: Set[str] = set()

    pages_fetched = 0
    total_items_seen = 0

    print(f"Scenario: {scenario}")
    print(f"Min required people: {min_people}")
    print(f"Queries planned: {len(queries)}")
    print("")

    for qi, q in enumerate(queries, start=1):
        if len(accepted) >= hard_cap_total:
            discards.append(("_PIPELINE", f"Hard cap reached ({hard_cap_total}). Stopping further queries."))
            break

        print(f"[QUERY {qi}/{len(queries)}] {q}")
        query_total_for_q = 0
        accepted_for_q = 0
        discarded_for_q = 0

        for page in range(1, max_pages_per_query + 1):
            url = build_search_url(q, per_page=per_page, page=page)
            payload, resp_headers, status = http_get_json(url, headers=headers)
            log_rate_limit(resp_headers)

            pages_fetched += 1
            items = payload.get("items", []) or []
            total_count = int(payload.get("total_count", 0) or 0)
            query_total_for_q += len(items)
            total_items_seen += len(items)

            print(f"  Page {page}/{max_pages_per_query}: status={status} total_count={total_count} items={len(items)} url={url}")

            if not items:
                print("  No items returned on this page. Ending pagination for this query.")
                break

            for rank, it in enumerate(items, start=1):
                login = (it.get("login") or "").strip()
                html_url = (it.get("html_url") or "").strip()
                score = float(it.get("score") or 0.0)

                if not login:
                    discards.append(("_ITEM", f"Missing login in result item. query='{q}' page={page} rank={rank}"))
                    discarded_for_q += 1
                    continue

                if login in seen:
                    discards.append((login, f"Duplicate across queries. query='{q}' page={page} rank={rank}"))
                    discarded_for_q += 1
                    continue

                if is_bot_login(login):
                    discards.append((login, f"Bot-like username filtered. query='{q}' page={page} rank={rank}"))
                    discarded_for_q += 1
                    seen.add(login)
                    continue

                cand = Candidate(login=login, html_url=html_url, score=score)
                accepted.append((cand, q, page, rank))
                accepted_for_q += 1
                seen.add(login)

                if len(accepted) >= hard_cap_total:
                    discards.append(("_PIPELINE", f"Hard cap reached ({hard_cap_total}). Stopping further enumeration."))
                    break

            if len(accepted) >= hard_cap_total:
                break

            # If we have reached the minimum, we still continue a bit to buffer results,
            # but do not waste pages excessively. This is a permanent rule: do not silently stop at 0.
            if len(accepted) >= min_people and page >= 2:
                print("  Minimum reached and at least 2 pages fetched for this query. Moving to next query.")
                break

        print(f"  Query summary: items_seen={query_total_for_q} accepted={accepted_for_q} discarded={discarded_for_q}")
        print("")

        # If we already meet minimum, we can stop after completing the current query set
        # to keep runtime reasonable, while still ensuring non-empty upstream.
        if len(accepted) >= min_people:
            print(f"Minimum people threshold met ({len(accepted)} >= {min_people}). Stopping further queries.")
            break

    print("Enumeration summary:")
    print(f"  Pages fetched: {pages_fetched}")
    print(f"  Total items seen: {total_items_seen}")
    print(f"  Unique accepted: {len(accepted)}")
    print(f"  Unique discarded reasons logged: {len(discards)}")
    print("")

    # HARD FAIL if under minimum.
    if len(accepted) < min_people:
        reason = (
            f"Hard failure: GitHub Search produced insufficient people for scenario '{scenario}'.\n"
            f"Accepted {len(accepted)} but require at least {min_people}.\n"
            "This is not allowed to proceed because downstream scenario/demo CSVs would be empty.\n"
            "\nMost likely causes:\n"
            "- Query set too restrictive for the moment.\n"
            "- Temporary GitHub search instability.\n"
            "- Rate limit reduction or soft throttling.\n"
            "\nWhat this script already did:\n"
            "- Ran scenario-specific queries, then broader AI+engineering fallbacks.\n"
            "- Deduped results across queries.\n"
            "- Filtered bot-like accounts.\n"
            "\nNext step to diagnose (without touching token creation):\n"
            "- Re-run with --max-pages-per-query 10 and --hard-cap-total 250.\n"
            "- Optionally try --scenario applied or infra to confirm search behavior.\n"
        )
        raise RuntimeError(reason)

    return accepted, discards


def hydrate_user_details(
    token: str,
    accepted: List[Tuple[Candidate, str, int, int]],
    scenario: str,
    max_detail_lookups: int,
) -> List[PersonRow]:
    headers = build_headers(token)
    rows: List[PersonRow] = []
    retrieved_at = utc_now_iso()

    print(f"Detail hydration: up to {max_detail_lookups} user profile lookups (bounded).")

    for idx, (cand, src_q, src_page, src_rank) in enumerate(accepted, start=1):
        if idx > max_detail_lookups:
            # Still write minimal row without profile details for remainder.
            rows.append(
                PersonRow(
                    GitHub_Username=cand.login,
                    GitHub_URL=cand.html_url,
                    Name="",
                    Company="",
                    Blog="",
                    Location="",
                    Email="",
                    Bio="",
                    Followers="",
                    Following="",
                    Public_Repos="",
                    Created_At="",
                    Updated_At="",
                    Source_Scenario=scenario,
                    Source_Query=src_q,
                    Source_Page=str(src_page),
                    Source_Rank=str(src_rank),
                    Retrieved_At_UTC=retrieved_at,
                )
            )
            continue

        url = build_user_url(cand.login)
        payload, resp_headers, status = http_get_json(url, headers=headers)
        log_rate_limit(resp_headers)

        if status != 200:
            rows.append(
                PersonRow(
                    GitHub_Username=cand.login,
                    GitHub_URL=cand.html_url,
                    Name="",
                    Company="",
                    Blog="",
                    Location="",
                    Email="",
                    Bio="",
                    Followers="",
                    Following="",
                    Public_Repos="",
                    Created_At="",
                    Updated_At="",
                    Source_Scenario=scenario,
                    Source_Query=src_q,
                    Source_Page=str(src_page),
                    Source_Rank=str(src_rank),
                    Retrieved_At_UTC=retrieved_at,
                )
            )
            continue

        rows.append(
            PersonRow(
                GitHub_Username=cand.login,
                GitHub_URL=(payload.get("html_url") or cand.html_url or "").strip(),
                Name=(payload.get("name") or "").strip(),
                Company=(payload.get("company") or "").strip(),
                Blog=(payload.get("blog") or "").strip(),
                Location=(payload.get("location") or "").strip(),
                Email=(payload.get("email") or "").strip(),
                Bio=(payload.get("bio") or "").strip(),
                Followers=str(payload.get("followers") or "").strip(),
                Following=str(payload.get("following") or "").strip(),
                Public_Repos=str(payload.get("public_repos") or "").strip(),
                Created_At=(payload.get("created_at") or "").strip(),
                Updated_At=(payload.get("updated_at") or "").strip(),
                Source_Scenario=scenario,
                Source_Query=src_q,
                Source_Page=str(src_page),
                Source_Rank=str(src_rank),
                Retrieved_At_UTC=retrieved_at,
            )
        )

        if idx % 10 == 0:
            print(f"  Hydrated {idx}/{min(len(accepted), max_detail_lookups)} profiles...")

    print(f"Detail hydration complete. Rows: {len(rows)}")
    return rows


def write_csv(path: str, rows: List[PersonRow]) -> None:
    safe_mkdir(os.path.dirname(path))
    fieldnames = list(PersonRow.__annotations__.keys())
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for r in rows:
            w.writerow(r.__dict__)


def write_discards(path: str, discards: List[Tuple[str, str]]) -> None:
    safe_mkdir(os.path.dirname(path))
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["Login_or_Marker", "Reason"])
        for login, reason in discards:
            w.writerow([login, reason])


def atomic_write_text(path: str, content: str) -> None:
    safe_mkdir(os.path.dirname(path))
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        f.write(content)
    os.replace(tmp, path)


def main() -> int:
    p = argparse.ArgumentParser(
        description="AI Talent Engine: Enumerate real GitHub users (hard-fail on empty/under-min results)."
    )
    p.add_argument("--scenario", required=True, help="Scenario name (frontier, rlhf, infra, applied, etc.)")
    p.add_argument("--min-people", type=int, default=DEFAULT_MIN_PEOPLE, help="Hard minimum required people count.")
    p.add_argument("--per-page", type=int, default=DEFAULT_PER_PAGE, help="GitHub search per_page (max 100).")
    p.add_argument("--max-pages-per-query", type=int, default=DEFAULT_MAX_PAGES_PER_QUERY, help="Max pages per query.")
    p.add_argument("--hard-cap-total", type=int, default=200, help="Hard cap on total accepted people.")
    p.add_argument("--detail-lookups", type=int, default=DEFAULT_DETAIL_LOOKUPS, help="Max profile detail lookups.")
    p.add_argument("--out-dir", default="outputs/people", help="Output directory for people artifacts.")
    args = p.parse_args()

    token = os.environ.get("GITHUB_TOKEN", "").strip()
    if not token:
        eprint("Hard failure: env var GITHUB_TOKEN is not set. Export it and re-run.")
        return 2

    if args.per_page < 1 or args.per_page > 100:
        eprint("Hard failure: --per-page must be between 1 and 100.")
        return 2

    out_dir = args.out_dir
    safe_mkdir(out_dir)

    # Enforce: cannot silently proceed with empty enumeration.
    try:
        accepted, discards = enumerate_candidates(
            token=token,
            scenario=args.scenario,
            min_people=args.min_people,
            per_page=args.per_page,
            max_pages_per_query=args.max_pages_per_query,
            hard_cap_total=args.hard_cap_total,
        )
    except Exception as ex:
        eprint(str(ex))
        # Still write discards for visibility if possible.
        try:
            write_discards(os.path.join(out_dir, "discards.csv"), [])
        except Exception:
            pass
        return 1

    # Hydrate details (bounded). Usernames are already real and sufficient for downstream.
    rows = hydrate_user_details(
        token=token,
        accepted=accepted,
        scenario=args.scenario,
        max_detail_lookups=args.detail_lookups,
    )

    # Write outputs.
    master_csv = os.path.join(out_dir, "people_master.csv")
    discards_csv = os.path.join(out_dir, "discards.csv")
    status_txt = os.path.join(out_dir, "people_inventory_status.txt")

    write_csv(master_csv, rows)
    write_discards(discards_csv, discards)

    # HARD VERIFY written CSV is non-empty and meets minimum.
    actual = 0
    try:
        with open(master_csv, "r", encoding="utf-8") as f:
            actual = sum(1 for _ in f) - 1  # minus header
    except Exception:
        actual = 0

    if actual < args.min_people:
        eprint(
            "Hard failure after write: people_master.csv does not meet minimum.\n"
            f"Rows written: {actual}. Required: {args.min_people}.\n"
            "This indicates an unexpected write failure or corruption and must be fixed before downstream runs."
        )
        return 1

    status = (
        "AI Talent Engine – People Inventory Status\n"
        f"Scenario: {args.scenario}\n"
        f"People_Count: {actual}\n"
        f"Generated_At_UTC: {utc_now_iso()}\n"
        f"People_Master_CSV: {os.path.abspath(master_csv)}\n"
        f"Discards_CSV: {os.path.abspath(discards_csv)}\n"
        "Status: OK\n"
    )
    atomic_write_text(status_txt, status)

    print("")
    print("SUCCESS: Upstream people inventory is non-empty and meets minimum.")
    print(f"people_master.csv: {os.path.abspath(master_csv)}")
    print(f"discards.csv:      {os.path.abspath(discards_csv)}")
    print(f"status file:       {os.path.abspath(status_txt)}")
    print(f"Final people count: {actual}")
    print("")
    print("Proof of enumeration (first 10 usernames):")
    for i, r in enumerate(rows[:10], start=1):
        print(f"  {i}. {r.GitHub_Username}")

    return 0


if __name__ == "__main__":
    sys.exit(main())


"""
Changelog
- v1.0.0-people-enum-hardfail (2026-01-01)
  - Rewritten from scratch to eliminate silent empty CSV creation.
  - Enforces hard minimum people count and fails loudly if GitHub Search returns zero or under-min.
  - Logs query, pages fetched, API response counts, accepted/discarded totals.
  - Writes discards.csv with rejection reasons for auditability.
  - Produces people_master.csv containing real GitHub usernames with bounded profile hydration.

Validation Steps (run from repo root)
1) Ensure token is exported:
   echo "$GITHUB_TOKEN" | wc -c

2) Run enumeration:
   python3 run_people_pipeline.py --scenario frontier

3) Verify non-empty output:
   wc -l outputs/people/people_master.csv
   head -n 5 outputs/people/people_master.csv

4) Verify usernames exist:
   cut -d, -f1 outputs/people/people_master.csv | head

Git Commands (SSH preferred)
git status
git add run_people_pipeline.py
git commit -m "Fix: hard-fail people enumeration; prevent empty people_master.csv"
git push
"""
