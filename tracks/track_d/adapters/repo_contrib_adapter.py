# -*- coding: utf-8 -*-
"""
Repo Contributor Adapter — Track D
(c) 2025 L. David Mendoza. All Rights Reserved.

Version: v1.0.0-trackd-hardreset
Date: 2025-12-22

CONTRACT (ENFORCED):
- Seed_Hub_Type: GitHub_Repo_Contributors ONLY
- Parse GitHub repo URLs safely
- Enumerate contributors via GitHub REST API
- Return NON-EMPTY people records or HARD FAIL
- No silent failures, no guessing

Output schema: dicts suitable for CSV serialization.
"""

from __future__ import annotations

import json
import re
import time
import urllib.parse
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

import requests


class RepoContribAdapterError(RuntimeError):
    pass


def utc_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def s(v: Any) -> str:
    if v is None:
        return ""
    try:
        return str(v).strip()
    except Exception:
        return ""


def parse_github_repo(url: str) -> Tuple[str, str, str]:
    raw = s(url)
    if not raw:
        raise RepoContribAdapterError("Empty GitHub repo URL")

    if raw.startswith("git@github.com:"):
        tail = raw[len("git@github.com:") :]
        if tail.endswith(".git"):
            tail = tail[:-4]
        parts = tail.split("/")
        if len(parts) != 2:
            raise RepoContribAdapterError(f"Invalid SSH GitHub repo URL: {raw}")
        owner, repo = parts
        return owner, repo, f"https://github.com/{owner}/{repo}"

    u = urllib.parse.urlparse(raw)
    host = u.netloc.lower().replace("www.", "")
    if host != "github.com":
        raise RepoContribAdapterError(f"Unsupported host: {host}")

    parts = u.path.strip("/").split("/")
    if len(parts) < 2:
        raise RepoContribAdapterError(f"Invalid GitHub repo URL: {raw}")

    owner, repo = parts[0], parts[1]
    if repo.endswith(".git"):
        repo = repo[:-4]

    if not re.match(r"^[A-Za-z0-9][A-Za-z0-9\-]*$", owner):
        raise RepoContribAdapterError(f"Invalid owner: {owner}")
    if not re.match(r"^[A-Za-z0-9][A-Za-z0-9\-\._]*$", repo):
        raise RepoContribAdapterError(f"Invalid repo: {repo}")

    return owner, repo, f"https://github.com/{owner}/{repo}"


class RepoContribAdapter:
    SEED_HUB_TYPE = "GitHub_Repo_Contributors"

    def __init__(
        self,
        github_token: Optional[str] = None,
        per_page: int = 100,
        max_pages: int = 20,
        user_agent: str = "AI-Talent-Engine/TrackD",
    ) -> None:
        self.token = s(github_token)
        self.per_page = per_page
        self.max_pages = max_pages
        self.user_agent = user_agent

    def enumerate_people(self, hub_row: Dict[str, Any]) -> List[Dict[str, Any]]:
        repo_url = ""
        for k in [
            "Repo_URL",
            "Repository_URL",
            "GitHub_Repo_URL",
            "URL",
            "Hub_URL",
            "Seed_Hub_URL",
            "Value",
            "Target_URL",
        ]:
            if s(hub_row.get(k)):
                repo_url = s(hub_row.get(k))
                break

        if not repo_url:
            raise RepoContribAdapterError("Missing GitHub repo URL in hub row")

        owner, repo, canonical = parse_github_repo(repo_url)
        api = f"https://api.github.com/repos/{owner}/{repo}/contributors"

        headers = {
            "Accept": "application/vnd.github+json",
            "User-Agent": self.user_agent,
        }
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"

        people: List[Dict[str, Any]] = []

        with requests.Session() as sess:
            for page in range(1, self.max_pages + 1):
                url = f"{api}?per_page={self.per_page}&page={page}&anon=false"
                r = sess.get(url, headers=headers, timeout=30)

                if r.status_code == 403 and r.headers.get("X-RateLimit-Remaining") == "0":
                    reset = int(r.headers.get("X-RateLimit-Reset", "0"))
                    wait = max(0, reset - int(time.time())) + 2
                    time.sleep(wait)
                    continue

                if r.status_code != 200:
                    raise RepoContribAdapterError(
                        f"GitHub API error {r.status_code} for {url}: {r.text[:200]}"
                    )

                data = r.json()
                if not data:
                    break

                for u in data:
                    login = s(u.get("login"))
                    if not login:
                        continue

                    rec = {
                        "source": "GitHub",
                        "seed_hub_type": self.SEED_HUB_TYPE,
                        "repo_url_input": repo_url,
                        "repo_url_canonical": canonical,
                        "repo_owner": owner,
                        "repo_name": repo,
                        "github_login": login,
                        "github_user_id": s(u.get("id")),
                        "github_profile_url": s(u.get("html_url")),
                        "github_avatar_url": s(u.get("avatar_url")),
                        "github_user_type": s(u.get("type")),
                        "repo_contributions": s(u.get("contributions")),
                        "retrieved_at_utc": utc_iso(),
                        "provenance": json.dumps(
                            {"api": api, "page": page}, ensure_ascii=False
                        ),
                    }
                    people.append(rec)

                if len(data) < self.per_page:
                    break

        if not people:
            raise RepoContribAdapterError(
                f"No contributors returned for repo {canonical}"
            )

        dedup: Dict[Tuple[str, str], Dict[str, Any]] = {}
        for p in people:
            key = (p["github_login"].lower(), p["repo_url_canonical"])
            if key not in dedup:
                dedup[key] = p

        return list(dedup.values())
