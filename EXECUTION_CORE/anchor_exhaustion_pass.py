#!/usr/bin/env python3
"""
anchor_exhaustion_pass.py
---------------------------------------
Purpose:
Exhaustively collect high-value anchor URLs already discovered upstream
and normalize them into canonical URL columns.

Scope:
• GitHub Pages
• Personal websites
• Blogs
• CV / Resume links

Rules:
• NEVER overwrite populated fields
• NEVER fabricate URLs
• Pipe-delimited storage only
• No scraping beyond already-known anchors
"""

import csv
import sys
from urllib.parse import urlparse


CANONICAL_URL_COLUMNS = {
    "GitHub_IO_URL": [],
    "Personal_Website_URLs": [],
    "Blog_URLs": [],
    "CV_URLs": [],
}


def normalize_url(url: str) -> str:
    url = url.strip()
    if not url:
        return ""
    if not url.startswith("http"):
        return ""
    parsed = urlparse(url)
    if not parsed.netloc:
        return ""
    return url


def add_unique(existing: str, new_url: str) -> str:
    if not new_url:
        return existing
    existing_set = set(u.strip() for u in existing.split("|") if u.strip())
    if new_url in existing_set:
        return existing
    existing_set.add(new_url)
    return "|".join(sorted(existing_set))


def classify_anchor(url: str):
    u = url.lower()
    if "github.io" in u:
        return "GitHub_IO_URL"
    if any(x in u for x in ("medium.com", "substack.com", "blog")):
        return "Blog_URLs"
    if any(x in u for x in ("cv", "resume")):
        return "CV_URLs"
    return "Personal_Website_URLs"


def process_csv(input_csv: str, output_csv: str):
    with open(input_csv, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames
        rows = list(reader)

    for row in rows:
        anchors = []
        for col in CANONICAL_URL_COLUMNS:
            anchors.extend(
                u.strip()
                for u in (row.get(col) or "").split("|")
                if u.strip()
            )

        for raw_url in anchors:
            url = normalize_url(raw_url)
            if not url:
                continue
            target_col = classify_anchor(url)
            if not row.get(target_col):
                row[target_col] = url
            else:
                row[target_col] = add_unique(row[target_col], url)

    with open(output_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print(
            "Usage: anchor_exhaustion_pass.py <input_csv> <output_csv>",
            file=sys.stderr,
        )
        sys.exit(1)

    process_csv(sys.argv[1], sys.argv[2])
