#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EXECUTION_CORE/public_identity_contact_pass.py
============================================================
BEST-IN-CLASS (EVIDENCE-ONLY) IDENTITY + CONTACT PASS

Maintainer: L. David Mendoza © 2026
Version: v2.1.1 (EOF sanitation, no logic change)

Purpose
- Deterministic, strict non-overwrite enrichment (no network):
  - Full_Name / First_Name / Last_Name (conservative derivation only)
  - Primary_Email / Primary_Phone (extract only if already present in row text)
  - Field_Level_Provenance_JSON (per-field provenance)

Rules
- Deterministic
- Strict non-overwrite
- Evidence-only extraction (regex against existing row text)
- No scraping, no network, no guessing
"""

from __future__ import annotations

import json
import re
from typing import Dict, List, Any, Tuple

EMAIL_DIRECT_RE = re.compile(r"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}")
EMAIL_DEOB_RE = re.compile(
    r"([a-zA-Z0-9._%+\-]+)\s*(?:@|\(at\)|\sat\s)\s*([a-zA-Z0-9.\-]+)\s*(?:\.|\(dot\)|\sdot\s)\s*([a-zA-Z]{2,})",
    re.IGNORECASE,
)
PHONE_RE = re.compile(r"(\+?1[\s\-\.]?)?\(?\d{3}\)?[\s\-\.]?\d{3}[\s\-\.]?\d{4}")
LINKEDIN_VANITY_RE = re.compile(r"linkedin\.com/in/([^/?#]+)", re.IGNORECASE)


def _norm(x: Any) -> str:
    return str(x or "").strip()


def _nonempty(x: Any) -> bool:
    return _norm(x) != ""


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


def _parse_linkedin_vanity(url: str) -> str:
    m = LINKEDIN_VANITY_RE.search(url or "")
    return m.group(1).strip() if m else ""


def _name_from_vanity(vanity: str) -> Tuple[str, str]:
    v = (vanity or "").replace("-", " ").replace("_", " ").strip()
    parts = [p for p in v.split() if p]
    if len(parts) >= 2:
        return parts[0].title(), parts[-1].title()
    if len(parts) == 1:
        return parts[0].title(), ""
    return "", ""


def _extract_emails(text: str) -> List[str]:
    out: List[str] = []
    for m in EMAIL_DEOB_RE.finditer(text or ""):
        out.append(f"{m.group(1)}@{m.group(2)}.{m.group(3)}")
    out.extend(EMAIL_DIRECT_RE.findall(text or ""))
    return sorted(set([e.strip() for e in out if e.strip()]), key=str.lower)


def _extract_phones(text: str) -> List[str]:
    out = [m.group(0).strip() for m in PHONE_RE.finditer(text or "")]
    return sorted(set([p for p in out if p]), key=str.lower)


def enrich_rows_public_identity_contact(rows: List[Dict[str, str]]) -> List[Dict[str, str]]:
    for row in rows:
        prov = _load_prov(row)

        li = _norm(row.get("LinkedIn_Public_URL") or row.get("LinkedIn_URL") or row.get("LinkedIn"))
        vanity = _parse_linkedin_vanity(li)

        if vanity and not _nonempty(row.get("Seed_Query_Or_Handle")):
            row["Seed_Query_Or_Handle"] = vanity
            _set_prov(prov, "Seed_Query_Or_Handle", "LinkedIn_Public_URL", "parse_vanity")

        if not _nonempty(row.get("Full_Name")) and vanity:
            fn, ln = _name_from_vanity(vanity)
            full = (fn + " " + ln).strip()
            if full:
                row["Full_Name"] = full
                _set_prov(prov, "Full_Name", "LinkedIn_Public_URL", "derive_from_vanity")

        full2 = _norm(row.get("Full_Name"))
        if full2:
            parts = [p for p in full2.split() if p]
            if parts and not _nonempty(row.get("First_Name")):
                row["First_Name"] = parts[0]
                _set_prov(prov, "First_Name", "Full_Name", "split_first")
            if len(parts) >= 2 and not _nonempty(row.get("Last_Name")):
                row["Last_Name"] = parts[-1]
                _set_prov(prov, "Last_Name", "Full_Name", "split_last")

        blob = " ".join(_norm(row.get(k)) for k in row.keys())
        emails = _extract_emails(blob)
        phones = _extract_phones(blob)

        if emails and not _nonempty(row.get("Primary_Email")):
            row["Primary_Email"] = emails[0]
            _set_prov(prov, "Primary_Email", "row_text_fields", "regex_extract_email")

        if phones and not _nonempty(row.get("Primary_Phone")):
            row["Primary_Phone"] = phones[0]
            _set_prov(prov, "Primary_Phone", "row_text_fields", "regex_extract_phone")

        _save_prov(row, prov)

    return rows


__all__ = ["enrich_rows_public_identity_contact"]
