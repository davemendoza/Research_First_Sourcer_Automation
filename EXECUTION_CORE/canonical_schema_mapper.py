# ============================================================
#  Research_First_Sourcer_Automation
#  File: EXECUTION_CORE/canonical_schema_mapper.py
#
#  Purpose:
#    Canonical schema mapper aligned to the 81-column Sample.xlsx gold standard.
#    Converts upstream stage rows into deterministic, schema-stable output.
#
#  Contract:
#    run(input_csv: str, output_csv: str) -> None
#
#  Version: v4.0.0-sample81-mapper
#  Author: Dave Mendoza
#  Copyright:
#    © 2025–2026 L. David Mendoza. All rights reserved.
#
#  Changelog:
#    - v4.0.0-sample81-mapper (2026-01-22):
#        * Hard-lock 81-column schema aligned to Sample.xlsx.
#        * Deterministic mapping from Stage 1 GitHub person rows.
#        * Field-level provenance JSON emitted per row.
#        * Empty-safe: header-only input => header-only output.
#
#  Validation:
#    python3 -m py_compile EXECUTION_CORE/canonical_schema_mapper.py
#
#  Git:
#    git add EXECUTION_CORE/canonical_schema_mapper.py
#    git commit -m "Canonical mapper: lock Sample81 schema (v4.0.0)"
#    git push
# ============================================================

from __future__ import annotations

import csv
import json
import os
import re
from typing import Dict, List, Tuple

PIPELINE_VERSION = "v4.0.0-sample81-mapper"

# Locked to Sample.xlsx columns (81)
CANONICAL_COLUMNS = ["Talent_Rank_Percentile", "Full_Name", "First_Name", "Last_Name", "AI_Role_Type", "Primary_Email", "Primary_Phone", "Current_Title", "Current_Company", "Location_City", "Location_State", "Location_Country", "LinkedIn_Public_URL", "Resume_URL", "Determinative_Skill_Areas", "Benchmarks_Worked_On", "Primary_Model_Families", "Production_vs_Research_Indicator", "GitHub_Repo_Evidence_Why", "Repo_Topics_Keywords", "Repo_Evidence_URLs", "Repo_Evidence_Count", "GitHub_Username", "GitHub_Profile_URL", "GitHub_IO_URLs", "GitHub_Org_URLs", "HuggingFace_Profile_URL", "Papers_Profile_URLs", "Google_Scholar_URL", "Semantic_Scholar_URL", "OpenAlex_URL", "ORCID_URL", "Patents_URLs", "ArXiv_URLs", "NeurIPS_URLs", "ICLR_URLs", "ICML_URLs", "ACL_URLs", "IEEE_URLs", "ACM_URLs", "DBLP_URLs", "ResearchGate_URLs", "SSRN_URLs", "Medium_URLs", "Substack_URLs", "StackOverflow_URLs", "Kaggle_URLs", "YouTube_Channel_URLs", "Twitter_X_URL", "Publications_Count_Raw", "Citation_Count_Raw", "Normalized_Citation_Count", "Citations_per_Year", "Citation_Velocity_3yr", "Citation_Velocity_5yr", "Citation_Provenance", "Open_Source_Repos_Count", "OSS_Contribution_Signals", "Awards_Signals", "Conference_Talks_Signals", "Hiring_Recommendation", "Strengths", "Weaknesses", "Determinant_Tier", "Evidence_Tier_Ledger_JSON", "Graph_Evidence_JSON", "CV_URL", "Portfolio_URLs", "Personal_Website_URLs", "Academic_Homepage_URLs", "Blog_URLs", "Slides_URLs", "Videos_URLs", "X_URLs", "YouTube_URLs", "GPT_Slim_Input_Eligible", "GPT_Slim_Rationale", "Field_Level_Provenance_JSON", "Row_Validity_Status", "Pipeline_Version", "Output_File_Path"]

LOCATION_RE = re.compile(r"^\s*(?P<city>[^,]+)\s*(?:,\s*(?P<state>[^,]+)\s*)?(?:,\s*(?P<country>[^,]+)\s*)?$")

def run(input_csv: str, output_csv: str) -> None:
    rows = _read_rows(input_csv)
    if not rows:
        _write_header_only(output_csv)
        return

    out_rows: List[Dict[str, str]] = []
    for r in rows:
        mapped, prov = _map_row(r)
        mapped["Field_Level_Provenance_JSON"] = json.dumps(prov, ensure_ascii=False, sort_keys=True)
        mapped["Row_Validity_Status"] = "OK"
        mapped["Pipeline_Version"] = PIPELINE_VERSION
        mapped["Output_File_Path"] = os.path.abspath(output_csv)
        out_rows.append(mapped)

    _write_rows(output_csv, out_rows)

def _map_row(r: Dict[str, str]) -> Tuple[Dict[str, str], Dict[str, Dict[str, str]]]:
    prov: Dict[str, Dict[str, str]] = {}
    out = {c: "" for c in CANONICAL_COLUMNS}

    gh_user = (r.get("GitHub_Username") or "").strip()
    gh_profile = (r.get("GitHub_URL") or "").strip()
    name_raw = (r.get("Name_Raw") or "").strip()
    company_raw = (r.get("Company_Raw") or "").strip()
    blog = (r.get("Blog_URL") or "").strip()
    email = (r.get("Email_Public") or "").strip()
    loc_raw = (r.get("Location_Raw") or "").strip()
    source_repo_url = (r.get("Source_Repo_URL") or r.get("Evidence_URL") or "").strip()
    role_hint = (r.get("Primary_Role_Hint") or "").strip()
    title_hint = (r.get("Title_Hint") or "").strip()

    full_name, first_name, last_name = _derive_name(name_raw, gh_user)
    city, state, country = _parse_location(loc_raw)

    # Identity
    out["Full_Name"] = full_name
    out["First_Name"] = first_name
    out["Last_Name"] = last_name
    out["GitHub_Username"] = gh_user
    out["GitHub_Profile_URL"] = gh_profile
    out["Blog_URLs"] = blog

    _prov_set(prov, "Full_Name", "github_profile", gh_profile)
    _prov_set(prov, "GitHub_Profile_URL", "github_profile", gh_profile)
    if blog:
        _prov_set(prov, "Blog_URLs", "github_profile", gh_profile)

    # Contact (public only)
    out["Primary_Email"] = email
    if email:
        _prov_set(prov, "Primary_Email", "github_profile_public_email", gh_profile)

    # Current company / title hints (upstream may be empty until enrichment)
    out["Current_Company"] = company_raw
    if company_raw:
        _prov_set(prov, "Current_Company", "github_profile_company", gh_profile)

    out["Current_Title"] = title_hint
    if title_hint:
        _prov_set(prov, "Current_Title", "upstream_hint", "pipeline")

    # Location
    out["Location_City"] = city
    out["Location_State"] = state
    out["Location_Country"] = country
    if loc_raw:
        _prov_set(prov, "Location_City", "github_profile_location", gh_profile)

    # Role
    out["AI_Role_Type"] = role_hint
    if role_hint:
        _prov_set(prov, "AI_Role_Type", "upstream_role_hint", "pipeline")

    # Repo evidence
    out["Repo_Evidence_URLs"] = source_repo_url
    out["Repo_Evidence_Count"] = "1" if source_repo_url else "0"
    out["GitHub_Repo_Evidence_Why"] = "Contributor discovered from repo evidence; repo URL anchored for downstream review." if source_repo_url else ""
    if source_repo_url:
        _prov_set(prov, "Repo_Evidence_URLs", "github_repo", source_repo_url)
        _prov_set(prov, "GitHub_Repo_Evidence_Why", "pipeline_rule", "stage1")

    # Default deterministic placeholders (not guesses)
    out["Talent_Rank_Percentile"] = ""
    out["Determinative_Skill_Areas"] = ""
    out["Benchmarks_Worked_On"] = ""
    out["Primary_Model_Families"] = ""
    out["Production_vs_Research_Indicator"] = ""
    out["Repo_Topics_Keywords"] = ""
    out["Open_Source_Repos_Count"] = ""
    out["OSS_Contribution_Signals"] = ""
    out["Awards_Signals"] = ""
    out["Conference_Talks_Signals"] = ""
    out["Hiring_Recommendation"] = ""
    out["Strengths"] = ""
    out["Weaknesses"] = ""
    out["Determinant_Tier"] = ""
    out["Evidence_Tier_Ledger_JSON"] = ""
    out["Graph_Evidence_JSON"] = ""
    out["GPT_Slim_Input_Eligible"] = "TRUE" if gh_user else "FALSE"
    out["GPT_Slim_Rationale"] = "Has GitHub identity and repo evidence anchor." if gh_user else "Missing GitHub identity."

    # Academic and citation fields are filled by long_running_enrichment_pass and citation_velocity_calculator
    return out, prov

def _derive_name(name_raw: str, gh_user: str) -> Tuple[str, str, str]:
    if name_raw:
        parts = [p for p in name_raw.strip().split() if p]
        if len(parts) == 1:
            return parts[0], parts[0], ""
        return name_raw.strip(), parts[0], parts[-1]
    if gh_user:
        # Deterministic fallback: username as full name, no fake parsing
        return gh_user, gh_user, ""
    return "", "", ""

def _parse_location(loc_raw: str) -> Tuple[str, str, str]:
    if not loc_raw:
        return "", "", ""
    m = LOCATION_RE.match(loc_raw)
    if not m:
        return loc_raw.strip(), "", ""
    city = (m.group("city") or "").strip()
    state = (m.group("state") or "").strip()
    country = (m.group("country") or "").strip()
    return city, state, country

def _prov_set(prov: Dict[str, Dict[str, str]], field: str, source_type: str, source: str) -> None:
    prov[field] = {"source_type": source_type, "source": source}

def _read_rows(path: str) -> List[Dict[str, str]]:
    if not path or not os.path.exists(path):
        return []
    with open(path, "r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        if not reader.fieldnames:
            return []
        out: List[Dict[str, str]] = []
        for row in reader:
            if row and any((v or "").strip() for v in row.values()):
                out.append({k: (v if v is not None else "") for k, v in row.items()})
        return out

def _write_header_only(path: str) -> None:
    _write_rows(path, [])

def _write_rows(path: str, rows: List[Dict[str, str]]) -> None:
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=CANONICAL_COLUMNS, extrasaction="ignore")
        writer.writeheader()
        for r in rows:
            clean = {c: ("" if r.get(c) is None else str(r.get(c, ""))) for c in CANONICAL_COLUMNS}
            writer.writerow(clean)
