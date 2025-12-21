#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
AI Talent Engine — Track C (Public Discovery Wiring)
Version: v1.1.1
© 2025 L. David Mendoza

PUBLIC-ONLY. PROVENANCE-FIRST. PYTHON-ONLY.
"""

import argparse
import csv
import datetime as dt
import hashlib
import json
import os
import re
import sys
import time
from typing import Dict, List, Set

import requests

# -----------------------------
# Constants
# -----------------------------

USER_AGENT = "AI-Talent-Engine/TrackC (public-only)"
TIMEOUT = 20
MAX_BYTES = 2_000_000

EMAIL_RE = re.compile(r"[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}", re.I)
PHONE_RE = re.compile(r"\+?\d[\d\s().-]{7,}\d")

# -----------------------------
# Helpers
# -----------------------------

def utc_now() -> str:
    return dt.datetime.utcnow().isoformat() + "Z"

def sha1(text: str) -> str:
    return hashlib.sha1(text.encode("utf-8")).hexdigest()

def is_blank(val) -> bool:
    return val is None or str(val).strip() == ""

def normalize_url(u: str) -> str:
    if not u:
        return ""
    u = u.strip()
    if not u.startswith("http"):
        u = "https://" + u
    return u.rstrip("/")

# -----------------------------
# HTTP
# -----------------------------

def fetch(url: str) -> str:
    try:
        r = requests.get(
            url,
            headers={"User-Agent": USER_AGENT},
            timeout=TIMEOUT,
            stream=True,
        )
        data = b""
        for chunk in r.iter_content(8192):
            data += chunk
            if len(data) >= MAX_BYTES:
                break
        return data.decode("utf-8", errors="ignore")
    except Exception:
        return ""

# -----------------------------
# Discovery
# -----------------------------

def extract_emails(text: str) -> List[str]:
    return list(dict.fromkeys(EMAIL_RE.findall(text)))

def extract_phones(text: str) -> List[str]:
    return list(dict.fromkeys(PHONE_RE.findall(text)))

# -----------------------------
# CSV
# -----------------------------

def read_csv(path: str):
    with open(path, newline="", encoding="utf-8-sig") as f:
        r = csv.DictReader(f)
        return list(r), r.fieldnames

def write_csv(path: str, rows: List[Dict], headers: List[str]):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=headers)
        w.writeheader()
        for row in rows:
            w.writerow(row)

# -----------------------------
# Main
# -----------------------------

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True)
    ap.add_argument("--output", required=True)
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--max-rows", type=int, default=0)
    args = ap.parse_args()

    rows, headers = read_csv(args.input)
    max_rows = args.max_rows or len(rows)

    run_id = sha1(args.input + utc_now())[:10]
    run_dir = f"outputs/run_{run_id}_trackC"
    os.makedirs(run_dir, exist_ok=True)

    log_path = f"{run_dir}/track_c_log.txt"
    audit_path = f"{run_dir}/track_c_audit.jsonl"

    log_lines = []
    audit = []

    for i, row in enumerate(rows[:max_rows]):
        html = ""
        emails: List[str] = []
        phones: List[str] = []

        url = normalize_url(row.get("GitHub_URL", ""))
        if url and not args.dry_run:
            html = fetch(url)
            emails = extract_emails(html)
            phones = extract_phones(html)

        if "Public_Email" in row and is_blank(row.get("Public_Email")) and emails:
            row["Public_Email"] = emails[0]

        if "Public_Phone" in row and is_blank(row.get("Public_Phone")) and phones:
            row["Public_Phone"] = phones[0]

        audit.append({
            "row": i,
            "url": url,
            "emails": emails,
            "phones": phones,
            "utc": utc_now(),
        })

        log_lines.append(f"[{i+1}] processed")

    write_csv(args.output, rows, headers)

    with open(log_path, "w") as f:
        f.write("\n".join(log_lines))

    with open(audit_path, "w") as f:
        for a in audit:
            f.write(json.dumps(a) + "\n")

    print("DONE")
    print(f"- Output CSV: {args.output}")
    print(f"- Log: {log_path}")
    print(f"- Audit: {audit_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
