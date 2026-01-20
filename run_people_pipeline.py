#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
AI Talent Engine | Research-First Sourcer Automation
File: run_people_pipeline.py

Author: © 2026 L. David Mendoza. All rights reserved.
Version: v1.2.0-phase1-flat-output-authoritative-rowcount
Date: 2026-01-06

PURPOSE (LOCKED)
Phase 1 inventory only. Enumerate real GitHub users, hard-fail on empty/under-min results.

OUTPUT CONTRACT (FLAT OUTPUT ONLY)
This script writes ONLY to a FLAT directory. It must not create per-run subfolders.

Outputs (flat, non-authoritative artifacts used by EXECUTION_CORE/run_safe.py):
- <out-dir>/people_master.csv
- <out-dir>/discards.csv
- <out-dir>/people_inventory_status.txt

CRITICAL GUARANTEE
people_master.csv must contain ALL accepted rows (not just hydrated subset).
Optional detail hydration enriches some columns, but NEVER changes rowcount.

VALIDATION (run from repo root)
1) Token:
   echo "$GITHUB_TOKEN" | wc -c

2) Run:
   python3 run_people_pipeline.py --scenario frontier_ai_scientist --out-dir outputs/people

3) Verify:
   wc -l outputs/people/people_master.csv
   head -n 5 outputs/people/people_master.csv

GIT (SSH)
git status
git add run_people_pipeline.py
git commit -m "Fix: Phase 1 enforce flat out-dir; guarantee people_master rowcount; Excel-safe CSV"
git push
"""

import argparse
import csv
import os
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Dict, List, Tuple

import urllib.request
import json


DEFAULT_MIN_PEOPLE = 25
DEFAULT_PER_PAGE = 100
DEFAULT_MAX_PAGES_PER_QUERY = 5
DEFAULT_DETAIL_LOOKUPS = 1


def eprint(msg: str) -> None:
    print(msg, file=sys.stderr, flush=True)


def safe_mkdir(p: str) -> None:
    if not p:
        return
    os.makedirs(p, exist_ok=True)


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def http_get_json(url: str, headers: Dict[str, str]) -> Tuple[Dict, Dict[str, str], int]:
    req = urllib.request.Request(url, headers=headers, method="GET")
    with urllib.request.urlopen(req, timeout=60) as resp:
        data = resp.read()
        status = getattr(resp, "status", 200)
        resp_headers = dict(resp.headers.items())
    payload = json.loads(data.decode("utf-8", errors="replace"))
    return payload, resp_headers, int(status)


def log_rate_limit(headers: Dict[str, str]) -> None:
    remaining = headers.get("X-RateLimit-Remaining", "")
    limit = headers.get("X-RateLimit-Limit", "")
    reset = headers.get("X-RateLimit-Reset", "")
    reset_utc = ""
    try:
        if reset:
            reset_utc = (
                datetime.fromtimestamp(int(reset), timezone.utc)
                .replace(microsecond=0)
                .isoformat()
                .replace("+00:00", "Z")
            )
    except Exception:
        reset_utc = ""
    if remaining or limit:
        print(f"RateLimit: remaining={remaining} limit={limit} reset_utc={reset_utc}")


def is_bot_login(login: str) -> bool:
    s = (login or "").lower()
    return (
        s.endswith("[bot]")
        or s.endswith("-bot")
        or s.endswith("_bot")
        or s.startswith("dependabot")
        or s.startswith("renovate")
    )


def build_search_url(q: str, per_page: int, page: int) -> str:
    from urllib.parse import quote
    return f"https://api.github.com/search/users?q={quote(q)}&per_page={per_page}&page={page}"


def build_user_url(login: str) -> str:
    return f"https://api.github.com/users/{login}"


def scenario_queries(scenario: str) -> List[str]:
    s = scenario.strip().lower()
    base = [
        'llm in:bio',
        'transformer in:bio',
        'rag in:bio',
        'rlhf in:bio',
        'cuda in:bio',
        'triton in:bio',
        'pytorch in:bio',
        'jax in:bio',
        'inference in:bio',
        'vllm in:bio',
        'tensorrt in:bio',
        'langchain in:bio',
        'llamaindex in:bio',
        'vector database in:bio',
        'mixture of experts in:bio',
    ]
    if "infra" in s:
        base.extend(['kubernetes in:bio', 'sre in:bio', 'distributed systems in:bio'])
    if "rlhf" in s:
        base.extend(['dpo in:bio', 'ppo in:bio', 'reward model in:bio'])
    if "frontier" in s or "scientist" in s:
        base.extend(['neurips in:bio', 'iclr in:bio', 'icml in:bio'])
    return base


@dataclass
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


def enumerate_candidates(
    token: str,
    scenario: str,
    min_people: int,
    per_page: int,
    max_pages_per_query: int,
    hard_cap_total: int,
) -> Tuple[List[Tuple[Candidate, str, int, int]], List[Tuple[str, str]]]:
    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {token}",
        "User-Agent": "AI-Talent-Engine-Phase1",
    }

    queries = scenario_queries(scenario)
    print(f"Scenario: {scenario}")
    print(f"Queries planned: {len(queries)}")
    print("")

    accepted: List[Tuple[Candidate, str, int, int]] = []
    discards: List[Tuple[str, str]] = []
    seen = set()
    pages_fetched = 0
    total_items_seen = 0

    for qi, q in enumerate(queries, start=1):
        print(f"[QUERY {qi}/{len(queries)}] \"{q}\"")
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

            if len(accepted) >= min_people and page >= 2:
                print("  Minimum reached and at least 2 pages fetched for this query. Moving to next query.")
                break

        print(f"  Query summary: items_seen={query_total_for_q} accepted={accepted_for_q} discarded={discarded_for_q}")
        print("")

        if len(accepted) >= min_people:
            print(f"Minimum people threshold met ({len(accepted)} >= {min_people}). Stopping further queries.")
            break

    print("Enumeration summary:")
    print(f"  Pages fetched: {pages_fetched}")
    print(f"  Total items seen: {total_items_seen}")
    print(f"  Unique accepted: {len(accepted)}")
    print(f"  Unique discarded reasons logged: {len(discards)}")
    print("")

    if len(accepted) < min_people:
        reason = (
            f"Hard failure: GitHub Search produced insufficient people for scenario '{scenario}'.\n"
            f"Accepted {len(accepted)} but require at least {min_people}.\n"
            "This is not allowed to proceed because downstream CSVs would be empty."
        )
        raise RuntimeError(reason)

    return accepted, discards


def hydrate_user_details_in_place(
    token: str,
    rows: List[PersonRow],
    max_detail_lookups: int,
) -> None:
    """
    Optional detail hydration for the first N rows only.
    CRITICAL: Never changes rowcount.
    """
    if max_detail_lookups <= 0:
        return

    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {token}",
        "User-Agent": "AI-Talent-Engine-Phase1",
    }

    n = min(len(rows), max_detail_lookups)
    for idx in range(n):
        login = rows[idx].GitHub_Username
        url = build_user_url(login)
        payload, resp_headers, status = http_get_json(url, headers=headers)
        log_rate_limit(resp_headers)

        if status != 200:
            continue

        rows[idx].GitHub_URL = (payload.get("html_url") or rows[idx].GitHub_URL or "").strip()
        rows[idx].Name = (payload.get("name") or "").strip()
        rows[idx].Company = (payload.get("company") or "").strip()
        rows[idx].Blog = (payload.get("blog") or "").strip()
        rows[idx].Location = (payload.get("location") or "").strip()
        rows[idx].Email = (payload.get("email") or "").strip()
        rows[idx].Bio = (payload.get("bio") or "").strip()
        rows[idx].Followers = str(payload.get("followers") or "").strip()
        rows[idx].Following = str(payload.get("following") or "").strip()
        rows[idx].Public_Repos = str(payload.get("public_repos") or "").strip()
        rows[idx].Created_At = (payload.get("created_at") or "").strip()
        rows[idx].Updated_At = (payload.get("updated_at") or "").strip()

        if (idx + 1) % 10 == 0:
            print(f"  Hydrated {idx+1}/{n} profiles...")


def write_csv_excel_safe(path: str, rows: List[PersonRow]) -> None:
    safe_mkdir(os.path.dirname(path))
    fieldnames = list(PersonRow.__annotations__.keys())
    with open(path, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames, quoting=csv.QUOTE_MINIMAL)
        w.writeheader()
        for r in rows:
            w.writerow(r.__dict__)


def write_discards_excel_safe(path: str, discards: List[Tuple[str, str]]) -> None:
    safe_mkdir(os.path.dirname(path))
    with open(path, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f, quoting=csv.QUOTE_MINIMAL)
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
    p.add_argument("--detail-lookups", type=int, default=DEFAULT_DETAIL_LOOKUPS, help="Hydrate details for first N rows only (0 disables).")
    p.add_argument("--out-dir", default="outputs/people", help="Flat output directory for people artifacts.")
    args = p.parse_args()

    token = os.environ.get("GITHUB_TOKEN", "").strip()
    if not token:
        eprint("Hard failure: env var GITHUB_TOKEN is not set. Export it and re-run.")
        return 2

    if args.per_page < 1 or args.per_page > 100:
        eprint("Hard failure: --per-page must be between 1 and 100.")
        return 2

    out_dir = (args.out_dir or "").strip()
    if not out_dir:
        eprint("Hard failure: --out-dir cannot be empty.")
        return 2
    if out_dir.lower().endswith(".csv"):
        eprint("Hard failure: --out-dir must be a directory, not a CSV filename.")
        return 2

    safe_mkdir(out_dir)

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
        try:
            write_discards_excel_safe(os.path.join(out_dir, "discards.csv"), [])
        except Exception:
            pass
        return 1

    retrieved_at = utc_now_iso()

    # Build ALL rows first (rowcount guarantee).
    rows: List[PersonRow] = []
    for cand, src_q, src_page, src_rank in accepted:
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
                Source_Scenario=args.scenario,
                Source_Query=src_q,
                Source_Page=str(src_page),
                Source_Rank=str(src_rank),
                Retrieved_At_UTC=retrieved_at,
            )
        )

    # Optional detail hydration in-place (never changes rowcount).
    print(f"Detail hydration target: first {max(0, int(args.detail_lookups))} rows (0 disables)")
    hydrate_user_details_in_place(token=token, rows=rows, max_detail_lookups=int(args.detail_lookups))
    print(f"Detail hydration complete. Rows: {len(rows)}")

    master_csv = os.path.join(out_dir, "people_master.csv")
    discards_csv = os.path.join(out_dir, "discards.csv")
    status_txt = os.path.join(out_dir, "people_inventory_status.txt")

    write_csv_excel_safe(master_csv, rows)
    write_discards_excel_safe(discards_csv, discards)

    actual = 0
    try:
        with open(master_csv, "r", encoding="utf-8", errors="replace") as f:
            actual = sum(1 for _ in f) - 1
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
        "AI Talent Engine | People Inventory Status\n"
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
