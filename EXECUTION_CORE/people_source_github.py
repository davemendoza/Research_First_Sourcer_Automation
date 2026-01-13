#!/usr/bin/env python3
"""
people_source_github.py
---------------------------------------
Purpose:
Harvest public GitHub profile evidence safely and deterministically.

Scope (public, evidence-only):
• GitHub_Username
• GitHub_URL
• GitHub_IO_URL (if present)
• Personal_Website_URLs (profile blog / website)

Rules:
• NEVER overwrite populated fields
• NEVER infer names
• NEVER scrape private data
• GitHub API only
"""

import csv
import sys
import requests

REQUEST_HEADERS = {"User-Agent": "Mozilla/5.0"}
TIMEOUT = 10


def non_empty(v):
    return bool(v and str(v).strip())


def github_api_from_url(url: str):
    if not url.startswith("https://github.com/"):
        return ""
    return url.rstrip("/").replace(
        "https://github.com/", "https://api.github.com/users/"
    )


def add_pipe(existing: str, new: str):
    if not new:
        return existing
    existing_set = set(x.strip() for x in existing.split("|") if x.strip())
    if new in existing_set:
        return existing
    existing_set.add(new)
    return "|".join(sorted(existing_set))


def process_csv(input_csv: str, output_csv: str):
    with open(input_csv, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames
        rows = list(reader)

    for row in rows:
        gh_url = (row.get("GitHub_URL") or "").strip()
        if not gh_url:
            continue

        api = github_api_from_url(gh_url)
        if not api:
            continue

        try:
            r = requests.get(api, timeout=TIMEOUT, headers=REQUEST_HEADERS)
            if r.status_code != 200:
                continue
            data = r.json()
        except Exception:
            continue

        # Username
        if not non_empty(row.get("GitHub_Username")):
            login = data.get("login")
            if login:
                row["GitHub_Username"] = login

        # GitHub Pages
        blog = (data.get("blog") or "").strip()
        if blog and "github.io" in blog.lower():
            if not non_empty(row.get("GitHub_IO_URL")):
                row["GitHub_IO_URL"] = blog
        elif blog:
            existing = row.get("Personal_Website_URLs") or ""
            row["Personal_Website_URLs"] = add_pipe(existing, blog)

    with open(output_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print(
            "Usage: people_source_github.py <input_csv> <output_csv>",
            file=sys.stderr,
        )
        sys.exit(1)

    process_csv(sys.argv[1], sys.argv[2])
