#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EXECUTION_CORE/people_projection_from_anchors.py
============================================================
PEOPLE PROJECTION FROM ANCHORS (DETERMINISTIC, FAIL-CLOSED)

Maintainer: L. David Mendoza © 2026
Version: v1.0.0

Purpose
- Convert anchor-exhaustion output into candidate PERSON rows.
- Extract person-like URLs/handles from existing anchor fields only:
  - GitHub user profiles (github.com/<user>)
  - LinkedIn public profiles (linkedin.com/in/<vanity>)
  - Google Scholar author pages (scholar.google.com/citations?user=...)
  - Semantic Scholar author pages (/author/...)
  - ORCID (orcid.org/<id>)
- Produce a people-projected CSV that downstream passes can enrich.

Non-negotiable rules
- No network calls. No scraping. No guessing.
- Deterministic output: stable sort + stable de-duplication.
- Fail-closed if no candidate people are found (prevents "garbage empty runs").

Contract
- process_csv(input_csv, output_csv) -> None

Validation
python3 -c "from EXECUTION_CORE.people_projection_from_anchors import process_csv; print('ok')"

Git Commands (SSH)
git add EXECUTION_CORE/people_projection_from_anchors.py
git commit -m "Add deterministic people projection pass from anchors (fail-closed, no fabrication)"
git push
"""

from __future__ import annotations

import csv
import json
import re
from pathlib import Path
from typing import Any, Dict, List, Tuple


URL_RE = re.compile(r"https?://[^\s\"'<>]+", re.IGNORECASE)

GITHUB_USER_RE = re.compile(r"https?://(www\.)?github\.com/([^/\s?#]+)(?:[/?#].*)?$", re.IGNORECASE)
GITHUB_REPO_RE = re.compile(r"https?://(www\.)?github\.com/[^/\s?#]+/[^/\s?#]+(?:[/?#].*)?$", re.IGNORECASE)

LINKEDIN_IN_RE = re.compile(r"https?://(www\.)?linkedin\.com/in/([^/?#]+)(?:[/?#].*)?$", re.IGNORECASE)

SCHOLAR_USER_RE = re.compile(r"https?://(www\.)?scholar\.google\.com/citations\?(?:[^#]*&)?user=([^&#]+)", re.IGNORECASE)

SEMANTIC_AUTHOR_RE = re.compile(r"https?://(www\.)?semanticscholar\.org/author/([^/?#]+)", re.IGNORECASE)

ORCID_RE = re.compile(r"https?://(www\.)?orcid\.org/(\d{4}-\d{4}-\d{4}-\d{3}[\dX])", re.IGNORECASE)


def _norm(x: Any) -> str:
    return str(x or "").strip()


def _load_prov(row: Dict[str, str]) -> Dict[str, Any]:
    raw = _norm(row.get("Field_Level_Provenance_JSON"))
    if not raw:
        return {}
    try:
        obj = json.loads(raw)
        return obj if isinstance(obj, dict) else {}
    except Exception:
        return {}


def _save_prov(row: Dict[str, str], prov: Dict[str, Any]) -> None:
    row["Field_Level_Provenance_JSON"] = json.dumps(prov, sort_keys=True)


def _set_prov(prov: Dict[str, Any], field: str, source: str, method: str) -> None:
    prov[field] = {"source": source, "method": method}


def _extract_urls_from_row(row: Dict[str, str]) -> List[str]:
    blob = " ".join(_norm(v) for v in row.values())
    urls = URL_RE.findall(blob)
    # stable de-dupe
    out: List[str] = []
    seen = set()
    for u in urls:
        k = u.strip()
        if not k:
            continue
        lk = k.lower()
        if lk in seen:
            continue
        seen.add(lk)
        out.append(k)
    return out


def _is_github_repo(url: str) -> bool:
    return bool(GITHUB_REPO_RE.match(url or ""))


def _classify_person_url(url: str) -> Tuple[str, str]:
    """
    Returns: (kind, handle_or_id)
    kind in: github, linkedin, scholar, semantic_scholar, orcid, unknown
    """
    u = (url or "").strip()

    m = LINKEDIN_IN_RE.match(u)
    if m:
        return ("linkedin", m.group(2).strip())

    m = ORCID_RE.match(u)
    if m:
        return ("orcid", m.group(2).strip())

    m = SCHOLAR_USER_RE.match(u)
    if m:
        return ("scholar", m.group(2).strip())

    m = SEMANTIC_AUTHOR_RE.match(u)
    if m:
        return ("semantic_scholar", m.group(2).strip())

    m = GITHUB_USER_RE.match(u)
    if m and not _is_github_repo(u):
        handle = m.group(2).strip()
        # ignore obvious non-user endpoints
        if handle.lower() not in {"topics", "orgs", "organizations", "site", "features", "pricing", "about"}:
            return ("github", handle)

    return ("unknown", "")


def _stable_sort_key(rec: Dict[str, str]) -> Tuple[str, str, str]:
    return (
        _norm(rec.get("Seed_Query_Or_Handle")).lower(),
        _norm(rec.get("LinkedIn_Public_URL")).lower(),
        _norm(rec.get("GitHub_URL")).lower(),
    )


def process_csv(input_csv: str | Path, output_csv: str | Path) -> None:
    inp = Path(input_csv)
    outp = Path(output_csv)
    if not inp.exists():
        raise FileNotFoundError(f"people_projection_from_anchors: input CSV not found: {inp}")
    outp.parent.mkdir(parents=True, exist_ok=True)

    with inp.open(newline="", encoding="utf-8") as fin:
        reader = csv.DictReader(fin)
        src_fieldnames = list(reader.fieldnames or [])
        rows: List[Dict[str, str]] = list(reader)

    if not src_fieldnames:
        raise RuntimeError(f"people_projection_from_anchors: input CSV has no header: {inp}")

    out_fieldnames = [
        "Seed_Query_Or_Handle",
        "Source_Person_URL",
        "LinkedIn_Public_URL",
        "GitHub_URL",
        "GitHub_Username",
        "Google_Scholar_URL",
        "Semantic_Scholar_URL",
        "ORCID_URL",
        "Source_Hub_URL",
        "Source_Organization",
        "Field_Level_Provenance_JSON",
    ]

    projected: List[Dict[str, str]] = []
    seen_keys = set()

    for r in rows:
        urls = _extract_urls_from_row(r)
        hub_url = _norm(r.get("URL") or r.get("Seed_Hub_URL") or r.get("Hub_URL") or "")
        org = _norm(r.get("Organization") or r.get("Org") or r.get("Company") or "")

        for u in urls:
            kind, handle = _classify_person_url(u)
            if kind == "unknown":
                continue

            out: Dict[str, str] = {k: "" for k in out_fieldnames}
            prov: Dict[str, Any] = {}

            out["Source_Person_URL"] = u
            out["Source_Hub_URL"] = hub_url
            out["Source_Organization"] = org

            if kind == "github":
                out["GitHub_URL"] = u
                out["GitHub_Username"] = handle
                out["Seed_Query_Or_Handle"] = handle
                _set_prov(prov, "GitHub_URL", "anchors_row_fields", "extract_url")
                _set_prov(prov, "GitHub_Username", "GitHub_URL", "parse_username")
                _set_prov(prov, "Seed_Query_Or_Handle", "GitHub_Username", "assign_handle")

            elif kind == "linkedin":
                out["LinkedIn_Public_URL"] = u
                out["Seed_Query_Or_Handle"] = handle
                _set_prov(prov, "LinkedIn_Public_URL", "anchors_row_fields", "extract_url")
                _set_prov(prov, "Seed_Query_Or_Handle", "LinkedIn_Public_URL", "parse_vanity")

            elif kind == "scholar":
                out["Google_Scholar_URL"] = u
                out["Seed_Query_Or_Handle"] = handle
                _set_prov(prov, "Google_Scholar_URL", "anchors_row_fields", "extract_url")
                _set_prov(prov, "Seed_Query_Or_Handle", "Google_Scholar_URL", "parse_user_id")

            elif kind == "semantic_scholar":
                out["Semantic_Scholar_URL"] = u
                out["Seed_Query_Or_Handle"] = handle
                _set_prov(prov, "Semantic_Scholar_URL", "anchors_row_fields", "extract_url")
                _set_prov(prov, "Seed_Query_Or_Handle", "Semantic_Scholar_URL", "parse_author_id")

            elif kind == "orcid":
                out["ORCID_URL"] = u
                out["Seed_Query_Or_Handle"] = handle
                _set_prov(prov, "ORCID_URL", "anchors_row_fields", "extract_url")
                _set_prov(prov, "Seed_Query_Or_Handle", "ORCID_URL", "parse_orcid")

            _save_prov(out, prov)

            dedupe_key = (
                _norm(out.get("Seed_Query_Or_Handle")).lower(),
                _norm(out.get("Source_Person_URL")).lower(),
            )
            if not dedupe_key[0] and not dedupe_key[1]:
                continue
            if dedupe_key in seen_keys:
                continue
            seen_keys.add(dedupe_key)

            projected.append(out)

    if not projected:
        raise RuntimeError(
            "people_projection_from_anchors: NO candidate people discovered from anchors output.\n"
            f"Input: {inp}\n"
            "This means the anchor exhaustion pass did not surface any person-like URLs.\n"
            "Do not proceed to downstream enrichment on hub-only rows."
        )

    projected = sorted(projected, key=_stable_sort_key)

    with outp.open("w", newline="", encoding="utf-8") as fout:
        writer = csv.DictWriter(fout, fieldnames=out_fieldnames)
        writer.writeheader()
        for rec in projected:
            writer.writerow({k: rec.get(k, "") for k in out_fieldnames})


__all__ = ["process_csv"]
