# -*- coding: utf-8 -*-
"""
anchor_exhaustion_pass.py
------------------------------------------------------------
IMPORT-ONLY MODULE (CALLABLE UTILITY)

Maintainer: L. David Mendoza © 2026
Version: v1.2.1 (EOF-CONTAMINATION FIX, LOCKED)

Purpose
- Normalize and exhaust anchor URLs already present in the dataset into
  canonical URL fields so downstream passes (identity/contact/name resolution)
  are not starved.

Scope (canonical URL targets)
- GitHub_IO_URL (single)
- Personal_Website_URLs (pipe-delimited)
- Portfolio_URLs (pipe-delimited)
- Blog_URLs (pipe-delimited)
- CV_URLs (pipe-delimited)

Non-Negotiables
- Evidence-only: uses only URLs already present in rows (no network calls).
- Strict non-overwrite: never overwrites populated canonical fields.
- Deterministic: stable dedupe + stable ordering.
- No subprocess calls.
- No writes outside returned rows (when used via process_csv).

Changelog
- v1.2.1: Remove stray heredoc token ("EOF") causing NameError; keep all logic
  deterministic and non-overwriting.

Validation Steps (local)
1) Syntax check:
   python3 -m py_compile EXECUTION_CORE/anchor_exhaustion_pass.py

2) Quick functional smoke:
   python3 -c "from EXECUTION_CORE.anchor_exhaustion_pass import classify_anchor, add_unique; \
print(classify_anchor('https://foo.github.io')); \
print(add_unique('', 'https://example.com')); \
print(add_unique('https://a.com', 'https://A.com'))"

Git Commands
git add EXECUTION_CORE/anchor_exhaustion_pass.py
git commit -m "Fix: remove EOF contamination from anchor_exhaustion_pass; restore valid import-only module"
git push
"""

from __future__ import annotations

import csv
from typing import Dict, List, Tuple

# Canonical output columns (targets)
CANONICAL_URL_COLUMNS: Tuple[str, ...] = (
    "GitHub_IO_URL",
    "Personal_Website_URLs",
    "Portfolio_URLs",
    "Blog_URLs",
    "CV_URLs",
)

# Fields to scan for anchors (sources). Includes common legacy variants.
ANCHOR_SOURCE_FIELDS: Tuple[str, ...] = (
    "GitHub_URL",
    "GitHub_Username",
    "GitHub_IO_URL",
    "Personal_Website_URLs",
    "Portfolio_URLs",
    "Blog_URLs",
    "CV_URLs",
    "Resume_URLs",
    "CV_URL",
    "Resume_URL",
    "Personal_Site_URL",
    "Website",
    "Blog",
    "Portfolio",
    "Links",
    "Link",
    "URL",
    "URLs",
)


def _non_empty(v: object) -> bool:
    return v is not None and str(v).strip() != ""


def _split_pipe(v: str) -> List[str]:
    parts: List[str] = []
    for p in str(v).split("|"):
        s = p.strip()
        if s:
            parts.append(s)
    return parts


def _is_http_url(u: str) -> bool:
    s = (u or "").strip().lower()
    return s.startswith("http://") or s.startswith("https://")


def _is_mailto(u: str) -> bool:
    return (u or "").strip().lower().startswith("mailto:")


def add_unique(existing: str, url: str) -> str:
    """
    Pipe-delimited append with case-insensitive dedupe and deterministic ordering.
    """
    url = (url or "").strip()
    if not url:
        return existing or ""

    existing_parts = [p.strip() for p in (existing or "").split("|") if p.strip()]
    seen = {p.lower() for p in existing_parts}
    if url.lower() in seen:
        return existing or ""

    existing_parts.append(url)
    existing_parts = sorted(existing_parts, key=lambda x: x.lower())
    return "|".join(existing_parts)


def _is_github_io(u: str) -> bool:
    return "github.io" in (u or "").lower()


def _is_probably_blog(u: str) -> bool:
    s = (u or "").lower()
    return any(
        k in s
        for k in (
            "/blog",
            "medium.com",
            "substack.com",
            "dev.to",
            "hashnode.com",
            "wordpress",
            "blogspot",
        )
    )


def _is_probably_portfolio(u: str) -> bool:
    s = (u or "").lower()
    return any(
        k in s
        for k in (
            "portfolio",
            "/projects",
            "/work",
            "/case",
            "showcase",
            "personal-site",
        )
    )


def _is_probably_cv(u: str) -> bool:
    s = (u or "").lower()
    # conservative: treat obvious resume/cv URLs or PDFs as CV links
    if s.endswith(".pdf"):
        return True
    return any(
        k in s
        for k in (
            "resume",
            "cv",
            "curriculum",
            "résumé",
            "lebenslauf",
            "履歴書",
            "简历",
        )
    )


def classify_anchor(url: str) -> str:
    """
    Determine which canonical URL column a URL belongs to.
    Default is Personal_Website_URLs.
    """
    u = (url or "").strip()
    if not u:
        return "Personal_Website_URLs"

    if _is_github_io(u):
        return "GitHub_IO_URL"
    if _is_probably_cv(u):
        return "CV_URLs"
    if _is_probably_blog(u):
        return "Blog_URLs"
    if _is_probably_portfolio(u):
        return "Portfolio_URLs"
    return "Personal_Website_URLs"


def ensure_columns(fieldnames: List[str]) -> List[str]:
    """
    Ensure canonical URL columns exist (append if missing).
    """
    out = list(fieldnames or [])
    for c in CANONICAL_URL_COLUMNS:
        if c not in out:
            out.append(c)
    return out


def exhaust_anchors_in_rows(rows: List[Dict[str, str]]) -> List[Dict[str, str]]:
    """
    In-place safe enrichment of rows. Strict non-overwrite for GitHub_IO_URL.
    Other canonical URL targets are pipe-delimited appends with dedupe.
    """
    for row in rows:
        anchors: List[str] = []

        for src in ANCHOR_SOURCE_FIELDS:
            v = row.get(src, "")
            if not _non_empty(v):
                continue
            for u in _split_pipe(v):
                if _is_mailto(u):
                    continue
                if _is_http_url(u):
                    anchors.append(u)

        # Deterministic iteration order
        anchors = sorted(set(anchors), key=lambda x: x.lower())

        for u in anchors:
            target = classify_anchor(u)

            # Strict non-overwrite for single-valued GitHub_IO_URL
            if target == "GitHub_IO_URL":
                if not _non_empty(row.get("GitHub_IO_URL", "")):
                    row["GitHub_IO_URL"] = u
                continue

            # Pipe-delimited targets: append with dedupe
            row[target] = add_unique(row.get(target, ""), u)

    return rows


def process_csv(input_csv: str, output_csv: str) -> None:
    """
    CSV entrypoint used by run_safe.py.
    Reads input_csv, enriches rows, writes output_csv with canonical URL columns ensured.
    """
    with open(input_csv, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        fieldnames = ensure_columns(list(reader.fieldnames or []))
        rows = list(reader)

    rows = exhaust_anchors_in_rows(rows)

    with open(output_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for r in rows:
            writer.writerow({k: r.get(k, "") for k in fieldnames})
