#!/usr/bin/env python3
"""
name_resolution_pass.py
---------------------------------------
Purpose:
Resolve real human names using evidence-only sources.

Precedence (first hit wins, never overwrite):
1. CV_URLs
2. Personal_Website_URLs
3. GitHub profile "name" field (NOT username)

Writes ONLY:
- Full_Name
- First_Name
- Last_Name

Never fabricates. Never infers from usernames.
"""

import csv
import re
import requests
from bs4 import BeautifulSoup

REQUEST_HEADERS = {"User-Agent": "Mozilla/5.0"}
TIMEOUT = 10

NAME_CLEAN_RE = re.compile(r'[\|\-–—•·\(\)\[\]{}<>]|cv|resume', re.I)


def clean_name(text: str) -> str:
    if not text:
        return ""
    t = NAME_CLEAN_RE.sub(" ", text)
    t = re.sub(r"\s+", " ", t).strip()
    if len(t.split()) < 2 or len(t) > 80:
        return ""
    return t


def split_name(full: str):
    parts = full.split()
    if len(parts) < 2:
        return "", ""
    return parts[0], " ".join(parts[1:])


def extract_name_from_page(url: str) -> str:
    try:
        r = requests.get(url, timeout=TIMEOUT, headers=REQUEST_HEADERS)
        if r.status_code != 200 or not r.text:
            return ""
        soup = BeautifulSoup(r.text, "html.parser")

        h1 = soup.find("h1")
        if h1:
            name = clean_name(h1.get_text(strip=True))
            if name:
                return name

        title = soup.find("title")
        if title:
            name = clean_name(title.get_text(strip=True))
            if name:
                return name
    except Exception:
        pass
    return ""


def extract_name_from_github(url: str) -> str:
    try:
        api_url = url.rstrip("/").replace(
            "https://github.com/", "https://api.github.com/users/"
        )
        r = requests.get(api_url, timeout=TIMEOUT, headers=REQUEST_HEADERS)
        if r.status_code != 200:
            return ""
        data = r.json()
        return clean_name(data.get("name") or "")
    except Exception:
        return ""


def process_csv(input_csv: str, output_csv: str):
    with open(input_csv, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames
        rows = list(reader)

    for row in rows:
        if row.get("Full_Name"):
            continue

        # 1. CV URLs
        for u in (row.get("CV_URLs") or "").split("|"):
            name = extract_name_from_page(u.strip())
            if name:
                fn, ln = split_name(name)
                row["Full_Name"] = name
                row["First_Name"] = fn
                row["Last_Name"] = ln
                break

        if row.get("Full_Name"):
            continue

        # 2. Personal sites
        for u in (row.get("Personal_Website_URLs") or "").split("|"):
            name = extract_name_from_page(u.strip())
            if name:
                fn, ln = split_name(name)
                row["Full_Name"] = name
                row["First_Name"] = fn
                row["Last_Name"] = ln
                break

        if row.get("Full_Name"):
            continue

        # 3. GitHub profile name
        gh = (row.get("GitHub_URL") or "").strip()
        if gh:
            name = extract_name_from_github(gh)
            if name:
                fn, ln = split_name(name)
                row["Full_Name"] = name
                row["First_Name"] = fn
                row["Last_Name"] = ln

    with open(output_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


if __name__ == "__main__":
    import sys

    if len(sys.argv) != 3:
        print("Usage: name_resolution_pass.py <input_csv> <output_csv>")
        sys.exit(1)

    process_csv(sys.argv[1], sys.argv[2])
