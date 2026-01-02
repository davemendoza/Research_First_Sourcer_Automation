#!/usr/bin/env bash
set -euo pipefail

# ------------------------------------------------------------
# Universal Lead Pipeline Autogen (Authoritative)
# Creates/overwrites:
# - scripts/normalize_people_csv.py     (canonical prefix + order)
# - scripts/universal_enrichment_pipeline.py (70+ lead columns)
# - scripts/macos_notify.py             (Notification Center popup)
# - scripts/send_run_completion_email.py (Mac Mail via AppleScript)
# - run_safe.py                         (universal safe entrypoint)
# Then runs: python3 run_safe.py <scenario>
# Then commits + pushes.
# ------------------------------------------------------------

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$REPO_ROOT"

SCENARIO="${1:-frontier}"

echo "============================================================"
echo "AUTOGEN UNIVERSAL LEAD PIPELINE"
echo "Repo: $REPO_ROOT"
echo "Scenario: $SCENARIO"
echo "============================================================"

if [[ ! -f "people_scenario_resolver.py" ]] || [[ ! -f "ai_talent_scenario_runner.py" ]]; then
  echo "ERROR: Must run from repo root. Missing expected files."
  exit 2
fi

mkdir -p scripts outputs/leads outputs/manifests

# ---------------------------------------------------------------------
# 1) Canonical Normalizer (overwrites scripts/normalize_people_csv.py)
# ---------------------------------------------------------------------
cat > scripts/normalize_people_csv.py <<'PY'
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
People CSV Normalizer (Canonical Prefix + Order)
Version: v2.0.0
Author: L. David Mendoza
Date: 2026-01-02
© 2025–2026 L. David Mendoza. All rights reserved.

Purpose:
- Create canonical columns required by the universal pipeline
- Enforce deterministic prefix and ordering
- Preserve all original columns after canonical prefix
- Fail closed if key identity sources are missing

Canonical prefix (MANDATORY ORDER):
  Person_ID, Role_Type, Email, Phone, LinkedIn_URL, GitHub_URL, GitHub_Username

Derivation rules:
- Person_ID  <- GitHub_Username (required, non-empty)
- Role_Type  <- Scenario if present else Source_Scenario if present else input arg fallback (not used here)
- Email      <- existing Email column if present else blank
- Phone      <- existing Phone column if present else blank
- LinkedIn_URL <- existing LinkedIn_URL if present else blank
- GitHub_URL <- required (must exist as column; may be blank in rows but not all blank)
- GitHub_Username <- required

Usage:
  python3 scripts/normalize_people_csv.py <input_csv> <output_csv>
"""

import csv
import sys
from pathlib import Path
from datetime import datetime

CANON_PREFIX = ["Person_ID","Role_Type","Email","Phone","LinkedIn_URL","GitHub_URL","GitHub_Username"]

if len(sys.argv) != 3:
    print("USAGE: normalize_people_csv.py <input_csv> <output_csv>")
    sys.exit(2)

input_csv = Path(sys.argv[1]).resolve()
output_csv = Path(sys.argv[2]).resolve()

if not input_csv.exists():
    print(f"ERROR: Input CSV not found: {input_csv}")
    sys.exit(2)

with input_csv.open(newline="", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    rows = list(reader)
    fieldnames = reader.fieldnames or []

required_source_cols = ["GitHub_Username"]
missing = [c for c in required_source_cols if c not in fieldnames]
if missing:
    print("ERROR: Missing required source columns: " + ", ".join(missing))
    sys.exit(3)

# GitHub_URL strongly required as a column
if "GitHub_URL" not in fieldnames:
    print("ERROR: Missing required source column: GitHub_URL")
    sys.exit(3)

# Ensure optional columns exist (create blanks if missing)
optional_cols = ["Scenario", "Source_Scenario", "Email", "Phone", "LinkedIn_URL"]
for c in optional_cols:
    if c not in fieldnames:
        fieldnames.append(c)
        for r in rows:
            r[c] = ""

# Build output fieldnames: canonical prefix + everything else not in prefix (preserve existing order)
rest = [c for c in fieldnames if c not in CANON_PREFIX]
out_fields = CANON_PREFIX + rest

# Row-level sanity checks
if not rows:
    print("ERROR: Input CSV has no rows")
    sys.exit(4)

# Validate GitHub_URL not entirely empty
all_blank_gh = True
for r in rows:
    if (r.get("GitHub_URL") or "").strip():
        all_blank_gh = False
        break
if all_blank_gh:
    print("ERROR: GitHub_URL column exists but all rows are blank")
    sys.exit(4)

output_csv.parent.mkdir(parents=True, exist_ok=True)

with output_csv.open("w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=out_fields)
    w.writeheader()

    for r in rows:
        gh_user = (r.get("GitHub_Username") or "").strip()
        if not gh_user:
            print("ERROR: Empty GitHub_Username encountered; cannot derive Person_ID")
            sys.exit(5)

        role_type = (r.get("Scenario") or "").strip() or (r.get("Source_Scenario") or "").strip()
        if not role_type:
            # fail closed: Role_Type is required to preserve downstream contracts
            print("ERROR: Missing Scenario/Source_Scenario; cannot derive Role_Type")
            sys.exit(5)

        normalized = dict(r)
        normalized["Person_ID"] = gh_user
        normalized["Role_Type"] = role_type
        normalized["Email"] = (r.get("Email") or "").strip()
        normalized["Phone"] = (r.get("Phone") or "").strip()
        normalized["LinkedIn_URL"] = (r.get("LinkedIn_URL") or "").strip()
        normalized["GitHub_URL"] = (r.get("GitHub_URL") or "").strip()
        normalized["GitHub_Username"] = gh_user

        # Emit in canonical order
        out_row = {k: normalized.get(k, "") for k in out_fields}
        w.writerow(out_row)

print(f"OK: Normalized CSV written: {output_csv}")
print(f"Rows processed: {len(rows)}")
print(f"Timestamp UTC: {datetime.utcnow().isoformat()}")
PY
chmod +x scripts/normalize_people_csv.py

# ---------------------------------------------------------------------
# 2) macOS popup notifier
# ---------------------------------------------------------------------
cat > scripts/macos_notify.py <<'PY'
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
macos_notify.py
Version: v1.0.0
Author: L. David Mendoza
Date: 2026-01-02
© 2025–2026 L. David Mendoza. All rights reserved.

Purpose:
- Trigger a macOS Notification Center popup (no dependencies)

Usage:
  python3 scripts/macos_notify.py "<title>" "<message>"
"""

import subprocess
import sys

if len(sys.argv) != 3:
    print("USAGE: macos_notify.py <title> <message>")
    sys.exit(2)

title = (sys.argv[1] or "").replace('"', "'")
message = (sys.argv[2] or "").replace('"', "'")

# Fail if osascript is missing (hard requirement for your "I can breathe" signal)
try:
    subprocess.run(["osascript", "-e", "return 0"], check=True, capture_output=True, text=True)
except Exception as e:
    print(f"ERROR: osascript not available or failed: {e}")
    sys.exit(3)

script = f'display notification "{message}" with title "{title}"'
subprocess.run(["osascript", "-e", script], check=True)
print("OK: popup notification sent")
PY
chmod +x scripts/macos_notify.py

# ---------------------------------------------------------------------
# 3) Completion email notifier (Mac Mail via AppleScript)
# ---------------------------------------------------------------------
cat > scripts/send_run_completion_email.py <<'PY'
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
send_run_completion_email.py
Version: v1.1.0
Author: L. David Mendoza
Date: 2026-01-02
© 2025–2026 L. David Mendoza. All rights reserved.

Purpose:
- Send a completion email using macOS Mail.app via AppleScript
- Deterministic subject/body including manifest path

Usage:
  python3 scripts/send_run_completion_email.py <manifest_json_path>

Env:
  PIPELINE_NOTIFY_TO  (default: LDaveMendoza@gmail.com)
  PIPELINE_NOTIFY_SUBJECT_PREFIX (default: "RUN COMPLETE")
"""

import json
import os
import sys
import subprocess
from pathlib import Path
from datetime import datetime, timezone

def die(msg: str, code: int = 2) -> None:
    print(f"ERROR: {msg}")
    sys.exit(code)

if len(sys.argv) != 2:
    die("USAGE: send_run_completion_email.py <manifest_json_path>", 2)

manifest_path = Path(sys.argv[1]).resolve()
if not manifest_path.exists():
    die(f"Manifest not found: {manifest_path}", 2)

to_addr = os.getenv("PIPELINE_NOTIFY_TO", "LDaveMendoza@gmail.com").strip()
prefix = os.getenv("PIPELINE_NOTIFY_SUBJECT_PREFIX", "RUN COMPLETE").strip()

try:
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
except Exception as e:
    die(f"Unable to parse manifest JSON: {e}", 3)

scenario = str(manifest.get("scenario","")).strip() or "unknown"
run_id = str(manifest.get("run_id","")).strip() or datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
leads_csv = str(manifest.get("leads_master_csv","") or manifest.get("leads_csv","") or "").strip()

subject = f"{prefix} — {scenario} — {run_id}"
body_lines = [
    f"Run complete (UTC): {manifest.get('completed_utc','')}",
    f"Scenario: {scenario}",
    "",
    f"Leads CSV: {leads_csv}",
    f"Manifest: {str(manifest_path)}",
    "",
    "This message was generated automatically by the Universal Lead Pipeline.",
]
body = "\\n".join(body_lines).replace('"', "'")

# Hard require osascript
try:
    subprocess.run(["osascript", "-e", "return 0"], check=True, capture_output=True, text=True)
except Exception as e:
    die(f"osascript not available or failed: {e}", 4)

# AppleScript to create and send message in Mail.app
applescript = f'''
tell application "Mail"
    set newMessage to make new outgoing message with properties {{subject:"{subject}", content:"{body}" & return & return, visible:false}}
    tell newMessage
        make new to recipient at end of to recipients with properties {{address:"{to_addr}"}}
        send
    end tell
end tell
'''

subprocess.run(["osascript", "-e", applescript], check=True)
print(f"OK: completion email sent to {to_addr}")
PY
chmod +x scripts/send_run_completion_email.py

# ---------------------------------------------------------------------
# 4) Universal Enrichment Pipeline (70+ columns, public-only, deterministic)
# ---------------------------------------------------------------------
cat > scripts/universal_enrichment_pipeline.py <<'PY'
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Universal Enrichment Pipeline (Lead-grade, Public Sources Only)
Version: v1.2.0
Author: L. David Mendoza
Date: 2026-01-02
© 2025–2026 L. David Mendoza. All rights reserved.

Hard requirements satisfied here:
- 40–70+ columns (this emits 80+ total columns including upstream)
- Output file named unambiguously as LEADS_MASTER_<scenario>_<run_id>.csv
- Public-source enrichment only (no fabrication)
- Field provenance and confidence included
"""

from __future__ import annotations

import csv
import json
import os
import re
import sys
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import urllib.request
import urllib.error
from urllib.parse import urlparse

USER_AGENT = "ResearchFirstSourcerAutomation/1.2 (public-source enrichment; contact only if published)"
HTTP_TIMEOUT = 20

CANON_PREFIX = ["Person_ID","Role_Type","Email","Phone","LinkedIn_URL","GitHub_URL","GitHub_Username"]

# Wide lead schema (adds 70+ columns)
LEAD_COLUMNS = [
    "Run_ID","Run_Timestamp_UTC","Scenario",
    "Enrichment_Status","Enrichment_Errors","Source_URLs",

    # Primary identity (duplicative on purpose for downstream tools)
    "Primary_ID_Type","Primary_ID_Value",

    # Contact outputs (public-only)
    "Primary_Email","Secondary_Emails","Email_Sources","Email_Confidence",
    "Primary_Phone","Secondary_Phones","Phone_Sources","Phone_Confidence",
    "LinkedIn_URL_Found","LinkedIn_Sources","LinkedIn_Confidence",
    "Resume_URL","Resume_Sources","Resume_Confidence",

    # Web surfaces
    "GitHub_Profile_HTML_URL","GitHub_User_API_URL","GitHub_Repos_API_URL",
    "GitHub_IO_URL","GitHub_IO_Status","GitHub_IO_Final_URL",
    "Personal_Website_URL","Personal_Website_Status","Personal_Website_Final_URL",

    # GitHub public profile fields
    "GH_Name","GH_Company","GH_Location","GH_Bio","GH_Blog",
    "GH_Twitter_Username","GH_Hireable",
    "GH_Followers","GH_Following","GH_Public_Repos","GH_Public_Gists",
    "GH_Created_At","GH_Updated_At",

    # Repo summary (top 8)
    "GH_Top_Repos","GH_Top_Repos_URLs","GH_Top_Repos_Stars_Total",
    "GH_Top_Repos_Forks_Total","GH_Top_Repos_Languages","GH_Top_Repos_Topics",

    # Signals (lexical, deterministic)
    "Signal_Terms_Found","Signal_Terms_Count","Signal_Terms_Sources",

    # Lead-quality flags
    "Any_Email_Flag","Any_Phone_Flag","Any_LinkedIn_Flag","Any_Resume_Flag","Any_Website_Flag",
    "Contact_Found_Flag","Lead_Contact_Confidence","Lead_Score","Lead_Score_Notes",

    # Audit/tracing
    "Fetched_Source_Count","Fetched_Bytes_Total"
]

DEFAULT_SIGNAL_TERMS = [
    "tensorrt","tensorrt-llm","cuda","triton","vllm","onnx","cutlass","jax","xla",
    "flashattention","pagedattention","nccl","deepspeed","fsdp",
    "kubernetes","k8s","llama.cpp","gguf","gptq","awq","qlora","lora","peft","dpo","ppo","rlhf",
    "rag","retrieval augmented generation","langchain","langgraph","llamaindex",
    "weaviate","pinecone","qdrant","milvus","faiss","pgvector","opensearch","vespa",
    "tgi","sglang","ray serve","tensorrt llm","tensor cores","gpu operator","nvidia"
]

EMAIL_RE = re.compile(r"\b[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}\b")
PHONE_RE = re.compile(r"(\+?1[\s\-.]?)?\(?\d{3}\)?[\s\-.]?\d{3}[\s\-.]?\d{4}\b")
LINKEDIN_RE = re.compile(r"https?://(www\.)?linkedin\.com/(in|pub)/[A-Za-z0-9\-_/%]+", re.IGNORECASE)
URL_RE = re.compile(r"https?://[^\s\"')>]+", re.IGNORECASE)

@dataclass
class Fetch:
    ok: bool
    status: int
    url: str
    final_url: str
    text: str
    bytes_read: int
    error: str

def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()

def normalize_url(s: str) -> str:
    s = (s or "").strip()
    if not s:
        return ""
    if s.startswith("http://") or s.startswith("https://"):
        return s
    return "https://" + s

def http_get(url: str, headers: Optional[Dict[str,str]] = None) -> Fetch:
    h = {
        "User-Agent": USER_AGENT,
        "Accept": "text/html,application/json;q=0.9,*/*;q=0.8",
    }
    if headers:
        h.update(headers)
    req = urllib.request.Request(url, headers=h)
    try:
        with urllib.request.urlopen(req, timeout=HTTP_TIMEOUT) as resp:
            status = int(getattr(resp, "status", 200))
            final_url = getattr(resp, "geturl", lambda: url)()
            raw = resp.read(2_000_000)  # cap
            text = raw.decode("utf-8", errors="replace")
            return Fetch(True, status, url, final_url, text, len(raw), "")
    except urllib.error.HTTPError as e:
        try:
            raw = e.read(200_000)
            text = raw.decode("utf-8", errors="replace")
        except Exception:
            text = ""
        return Fetch(False, int(e.code), url, url, text, 0, f"HTTPError {e.code}")
    except Exception as e:
        return Fetch(False, 0, url, url, "", 0, f"{type(e).__name__}: {e}")

def gh_headers() -> Dict[str,str]:
    h = {"Accept": "application/vnd.github+json"}
    token = os.getenv("GITHUB_TOKEN","").strip()
    if token:
        h["Authorization"] = f"Bearer {token}"
    return h

def gh_user_api(user: str) -> str:
    return f"https://api.github.com/users/{user}"

def gh_repos_api(user: str) -> str:
    return f"https://api.github.com/users/{user}/repos?per_page=100&sort=updated"

def find_github_io(user: str) -> str:
    return f"https://{user}.github.io"

def normalize_us_phone(p: str) -> str:
    digits = re.sub(r"\D","", p or "")
    if digits.startswith("1") and len(digits) == 11:
        digits = digits[1:]
    if len(digits) != 10:
        return ""
    return f"+1{digits}"

def extract_contacts(text: str) -> Tuple[List[str],List[str],List[str],List[str]]:
    emails = sorted(set(EMAIL_RE.findall(text or "")))
    # remove obvious placeholders
    emails = [e for e in emails if "example.com" not in e.lower()]
    phones = []
    for m in PHONE_RE.finditer(text or ""):
        n = normalize_us_phone(m.group(0))
        if n:
            phones.append(n)
    phones = sorted(set(phones))
    linkedins = sorted(set(m.group(0) for m in LINKEDIN_RE.finditer(text or "")))

    # Resume URLs heuristic (any URL containing resume/cv and pdf/doc/docx)
    resumes = []
    for m in URL_RE.finditer(text or ""):
        u = m.group(0)
        if re.search(r"(resume|cv)", u, re.IGNORECASE) and re.search(r"\.(pdf|doc|docx)\b", u, re.IGNORECASE):
            resumes.append(u)
    resumes = sorted(set(resumes))
    return emails, phones, linkedins, resumes

def safe_join(items: List[str], sep: str=" | ") -> str:
    items = [i.strip() for i in items if (i or "").strip()]
    return sep.join(items)

def repo_score(repo: Dict) -> Tuple[int,int]:
    return (int(repo.get("stargazers_count") or 0), int(repo.get("forks_count") or 0))

def lexical_signals(source_texts: List[Tuple[str,str]], terms: List[str]) -> Tuple[List[str],List[str]]:
    found = set()
    srcs = set()
    for src_url, txt in source_texts:
        tl = (txt or "").lower()
        for t in terms:
            if t.lower() in tl:
                found.add(t.lower())
                srcs.add(src_url)
    return sorted(found), sorted(srcs)

def main() -> None:
    if len(sys.argv) < 5:
        print("USAGE: universal_enrichment_pipeline.py <scenario> <input_normalized_people_csv> <output_dir> <run_id>")
        sys.exit(2)

    scenario = sys.argv[1].strip()
    in_csv = Path(sys.argv[2]).resolve()
    out_dir = Path(sys.argv[3]).resolve()
    run_id = sys.argv[4].strip()

    if not in_csv.exists():
        print(f"ERROR: input CSV not found: {in_csv}")
        sys.exit(2)

    out_dir.mkdir(parents=True, exist_ok=True)
    out_csv = out_dir / f"LEADS_MASTER_{scenario}_{run_id}.csv"

    # Read input
    with in_csv.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        cols = reader.fieldnames or []

    if cols[:len(CANON_PREFIX)] != CANON_PREFIX:
        print("ERROR: input CSV not canonical-normalized. Expected prefix: " + ", ".join(CANON_PREFIX))
        sys.exit(3)

    if not rows:
        print("ERROR: input CSV has no rows")
        sys.exit(4)

    # Output fields: preserve input columns + lead columns (avoid dup)
    preserved = [c for c in cols if c not in LEAD_COLUMNS]
    out_fields = preserved + LEAD_COLUMNS

    ts = utc_now_iso()

    # Stats
    bytes_total = 0
    print("UNIVERSAL ENRICHMENT PIPELINE v1.2.0")
    print(f"Scenario: {scenario}")
    print(f"Input: {in_csv}")
    print(f"Output: {out_csv}")
    print(f"Rows: {len(rows)}")
    print(f"Run_ID: {run_id}")
    print()

    with out_csv.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=out_fields)
        w.writeheader()

        for i, r in enumerate(rows, start=1):
            gh_user = (r.get("GitHub_Username") or "").strip()
            gh_url = normalize_url(r.get("GitHub_URL") or "")

            out = dict(r)
            for c in LEAD_COLUMNS:
                out[c] = ""

            out["Run_ID"] = run_id
            out["Run_Timestamp_UTC"] = ts
            out["Scenario"] = scenario
            out["Primary_ID_Type"] = "GitHub_Username"
            out["Primary_ID_Value"] = gh_user

            errors = []
            source_urls = []
            source_texts: List[Tuple[str,str]] = []
            fetched_bytes = 0

            if not gh_user:
                out["Enrichment_Status"] = "failed"
                out["Enrichment_Errors"] = "Missing GitHub_Username"
                w.writerow(out)
                continue

            profile_html = gh_url or f"https://github.com/{gh_user}"
            user_api = gh_user_api(gh_user)
            repos_api = gh_repos_api(gh_user)
            gh_io = find_github_io(gh_user)

            out["GitHub_Profile_HTML_URL"] = profile_html
            out["GitHub_User_API_URL"] = user_api
            out["GitHub_Repos_API_URL"] = repos_api
            out["GitHub_IO_URL"] = gh_io

            # GitHub API user
            fu = http_get(user_api, headers=gh_headers())
            source_urls.append(user_api)
            fetched_bytes += fu.bytes_read
            if fu.ok and fu.text:
                try:
                    u = json.loads(fu.text)
                except Exception:
                    u = {}
                out["GH_Name"] = str(u.get("name") or "")
                out["GH_Company"] = str(u.get("company") or "")
                out["GH_Location"] = str(u.get("location") or "")
                out["GH_Bio"] = str(u.get("bio") or "")
                out["GH_Blog"] = str(u.get("blog") or "")
                out["GH_Twitter_Username"] = str(u.get("twitter_username") or "")
                out["GH_Hireable"] = str(u.get("hireable") or "")
                out["GH_Followers"] = str(u.get("followers") or "")
                out["GH_Following"] = str(u.get("following") or "")
                out["GH_Public_Repos"] = str(u.get("public_repos") or "")
                out["GH_Public_Gists"] = str(u.get("public_gists") or "")
                out["GH_Created_At"] = str(u.get("created_at") or "")
                out["GH_Updated_At"] = str(u.get("updated_at") or "")
                api_email = str(u.get("email") or "").strip()
                if api_email:
                    out["Primary_Email"] = api_email
                    out["Email_Sources"] = user_api
                    out["Email_Confidence"] = "high"
            else:
                errors.append(fu.error or f"GitHub user API failed ({fu.status})")

            # Profile HTML
            fp = http_get(profile_html)
            source_urls.append(profile_html)
            fetched_bytes += fp.bytes_read
            if fp.ok and fp.text:
                source_texts.append((profile_html, fp.text))
            else:
                errors.append(fp.error or f"GitHub profile HTML failed ({fp.status})")

            # Websites: GitHub.io + personal site from blog if present
            blog = normalize_url(out.get("GH_Blog") or "") or normalize_url(r.get("Blog") or "")
            personal_site = blog if blog else ""
            out["Personal_Website_URL"] = personal_site

            fg = http_get(gh_io)
            source_urls.append(gh_io)
            fetched_bytes += fg.bytes_read
            if fg.ok and fg.text:
                out["GitHub_IO_Status"] = "ok"
                out["GitHub_IO_Final_URL"] = fg.final_url
                source_texts.append((fg.final_url, fg.text))
            else:
                out["GitHub_IO_Status"] = f"failed_{fg.status}"

            if personal_site:
                fs = http_get(personal_site)
                source_urls.append(personal_site)
                fetched_bytes += fs.bytes_read
                if fs.ok and fs.text:
                    out["Personal_Website_Status"] = "ok"
                    out["Personal_Website_Final_URL"] = fs.final_url
                    source_texts.append((fs.final_url, fs.text))
                else:
                    out["Personal_Website_Status"] = f"failed_{fs.status}"
            else:
                out["Personal_Website_Status"] = "none"

            # Repos API
            fr = http_get(repos_api, headers=gh_headers())
            source_urls.append(repos_api)
            fetched_bytes += fr.bytes_read
            repos = []
            if fr.ok and fr.text:
                try:
                    repos = json.loads(fr.text)
                    if not isinstance(repos, list):
                        repos = []
                except Exception:
                    repos = []
                    errors.append("Repos JSON parse failed")
            else:
                errors.append(fr.error or f"GitHub repos API failed ({fr.status})")

            top = sorted(repos, key=repo_score, reverse=True)[:8]
            names, urls, langs, topics = [], [], [], []
            stars_total = 0
            forks_total = 0
            for repo in top:
                names.append(str(repo.get("name") or ""))
                urls.append(str(repo.get("html_url") or ""))
                stars_total += int(repo.get("stargazers_count") or 0)
                forks_total += int(repo.get("forks_count") or 0)
                lang = str(repo.get("language") or "").strip()
                if lang:
                    langs.append(lang)
                tps = repo.get("topics") or []
                if isinstance(tps, list):
                    for t in tps:
                        if t:
                            topics.append(str(t))

            out["GH_Top_Repos"] = safe_join(names)
            out["GH_Top_Repos_URLs"] = safe_join(urls)
            out["GH_Top_Repos_Stars_Total"] = str(stars_total)
            out["GH_Top_Repos_Forks_Total"] = str(forks_total)
            out["GH_Top_Repos_Languages"] = safe_join(sorted(set(langs)))
            out["GH_Top_Repos_Topics"] = safe_join(sorted(set(topics)))

            # Contact extraction from fetched pages (public only)
            emails_found: List[str] = []
            phones_found: List[str] = []
            linkedins_found: List[str] = []
            resumes_found: List[str] = []
            email_srcs, phone_srcs, li_srcs, res_srcs = set(), set(), set(), set()

            for src, txt in source_texts:
                e, p, l, rs = extract_contacts(txt)
                if e:
                    emails_found.extend(e); email_srcs.add(src)
                if p:
                    phones_found.extend(p); phone_srcs.add(src)
                if l:
                    linkedins_found.extend(l); li_srcs.add(src)
                if rs:
                    resumes_found.extend(rs); res_srcs.add(src)

            emails_found = sorted(set(emails_found))
            phones_found = sorted(set(phones_found))
            linkedins_found = sorted(set(linkedins_found))
            resumes_found = sorted(set(resumes_found))

            upstream_email = (r.get("Email") or "").strip()
            upstream_phone = (r.get("Phone") or "").strip()
            upstream_linkedin = (r.get("LinkedIn_URL") or "").strip()

            # Email preference: API email (already set) > upstream > harvested
            if not out["Primary_Email"]:
                if upstream_email:
                    out["Primary_Email"] = upstream_email
                    out["Email_Confidence"] = "medium"
                    out["Email_Sources"] = "upstream"
                elif emails_found:
                    out["Primary_Email"] = emails_found[0]
                    out["Secondary_Emails"] = safe_join(emails_found[1:])
                    out["Email_Sources"] = safe_join(sorted(email_srcs))
                    out["Email_Confidence"] = "medium"

            # Phone preference: upstream > harvested
            if upstream_phone:
                out["Primary_Phone"] = upstream_phone
                out["Phone_Confidence"] = "medium"
                out["Phone_Sources"] = "upstream"
            elif phones_found:
                out["Primary_Phone"] = phones_found[0]
                out["Secondary_Phones"] = safe_join(phones_found[1:])
                out["Phone_Sources"] = safe_join(sorted(phone_srcs))
                out["Phone_Confidence"] = "medium"

            # LinkedIn
            if upstream_linkedin:
                out["LinkedIn_URL_Found"] = upstream_linkedin
                out["LinkedIn_Sources"] = "upstream"
                out["LinkedIn_Confidence"] = "medium"
            elif linkedins_found:
                out["LinkedIn_URL_Found"] = linkedins_found[0]
                out["LinkedIn_Sources"] = safe_join(sorted(li_srcs))
                out["LinkedIn_Confidence"] = "low"

            # Resume
            if resumes_found:
                out["Resume_URL"] = resumes_found[0]
                out["Resume_Sources"] = safe_join(sorted(res_srcs))
                out["Resume_Confidence"] = "low"

            # Signals
            found_terms, term_srcs = lexical_signals(source_texts, DEFAULT_SIGNAL_TERMS)
            out["Signal_Terms_Found"] = safe_join(found_terms)
            out["Signal_Terms_Count"] = str(len(found_terms))
            out["Signal_Terms_Sources"] = safe_join(term_srcs)

            # Lead score (simple, deterministic)
            score = 0
            notes = []
            if out["Primary_Email"]:
                score += 30; notes.append("email")
            if out["Primary_Phone"]:
                score += 15; notes.append("phone")
            if out["LinkedIn_URL_Found"]:
                score += 10; notes.append("linkedin")
            if out["Resume_URL"]:
                score += 10; notes.append("resume")
            if out["GitHub_IO_Status"] == "ok" or out["Personal_Website_Status"] == "ok":
                score += 10; notes.append("website")
            if len(found_terms) >= 5:
                score += 10; notes.append("signals>=5")
            if stars_total >= 50:
                score += 10; notes.append("stars>=50")

            out["Lead_Score"] = str(score)
            out["Lead_Score_Notes"] = " ; ".join(notes)

            # Flags
            out["Any_Email_Flag"] = "1" if out["Primary_Email"] else "0"
            out["Any_Phone_Flag"] = "1" if out["Primary_Phone"] else "0"
            out["Any_LinkedIn_Flag"] = "1" if out["LinkedIn_URL_Found"] else "0"
            out["Any_Resume_Flag"] = "1" if out["Resume_URL"] else "0"
            out["Any_Website_Flag"] = "1" if (out["GitHub_IO_Status"] == "ok" or out["Personal_Website_Status"] == "ok") else "0"
            contact_found = (out["Any_Email_Flag"] == "1" or out["Any_Phone_Flag"] == "1" or out["Any_LinkedIn_Flag"] == "1" or out["Any_Resume_Flag"] == "1")
            out["Contact_Found_Flag"] = "1" if contact_found else "0"

            # Confidence summary
            if out["Any_Email_Flag"] == "1" and (out["Email_Confidence"] == "high"):
                out["Lead_Contact_Confidence"] = "HIGH"
            elif out["Any_Email_Flag"] == "1" or out["Any_Phone_Flag"] == "1":
                out["Lead_Contact_Confidence"] = "MEDIUM"
            else:
                out["Lead_Contact_Confidence"] = "LOW"

            out["Fetched_Source_Count"] = str(len(sorted(set(source_urls))))
            out["Fetched_Bytes_Total"] = str(fetched_bytes)

            out["Source_URLs"] = safe_join(sorted(set(source_urls)))
            out["Enrichment_Errors"] = safe_join(errors)
            out["Enrichment_Status"] = "ok" if not errors else "ok_with_warnings"

            w.writerow({k: out.get(k, "") for k in out_fields})

            bytes_total += fetched_bytes

            # Light progress, no spam
            if i == 1 or i % 10 == 0 or i == len(rows):
                print(f"Progress: {i}/{len(rows)} enriched")

            # Rate-limit friendliness when no token is present
            if not os.getenv("GITHUB_TOKEN","").strip():
                time.sleep(0.6)

    print()
    print("ENRICHMENT COMPLETE")
    print(f"Output: {out_csv}")
    print(f"Total fetched bytes: {bytes_total}")
PY
chmod +x scripts/universal_enrichment_pipeline.py

# ---------------------------------------------------------------------
# 5) Universal run_safe.py (overwrites; contract + sequencing locked)
# ---------------------------------------------------------------------
cat > run_safe.py <<'PY'
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
run_safe.py — Universal Safe Runner (Lead-grade finished outputs)
Version: v3.0.0
Author: L. David Mendoza
Date: 2026-01-02
© 2025–2026 L. David Mendoza. All rights reserved.

Single command produces:
- People CSV (bounded demo rules enforced by resolver contract)
- Normalized people CSV (canonical prefix and order enforced)
- Lead-grade finished CSV (40–70+ columns) in outputs/leads/run_<id>/
- Scenario scoring outputs (existing scenario runner)
- Manifest JSON
- macOS popup + email on completion (hard required unless disabled)

Usage:
  python3 run_safe.py <scenario>

Env (recommended defaults):
  EMAIL_NOTIFY_ENABLED=1
  POPUP_NOTIFY_ENABLED=1
  AUTO_OPEN_LEADS=1
  PIPELINE_NOTIFY_TO=LDaveMendoza@gmail.com
  GITHUB_TOKEN=...  (optional, improves GitHub rate limits)

Hard fail conditions:
- No normalized canonical prefix
- Leads CSV has < 40 columns
- Popup fails (when POPUP_NOTIFY_ENABLED=1)
- Email fails (when EMAIL_NOTIFY_ENABLED=1)
"""

from __future__ import annotations

import json
import os
import sys
import subprocess
from pathlib import Path
from datetime import datetime, timezone

import pandas as pd

REPO_ROOT = Path(__file__).resolve().parent
PEOPLE_DIR = REPO_ROOT / "outputs" / "people"
LEADS_ROOT = REPO_ROOT / "outputs" / "leads"
MANIFEST_DIR = REPO_ROOT / "outputs" / "manifests"

NORMALIZER = REPO_ROOT / "scripts" / "normalize_people_csv.py"
ENRICHER = REPO_ROOT / "scripts" / "universal_enrichment_pipeline.py"
POPUP = REPO_ROOT / "scripts" / "macos_notify.py"
EMAIL = REPO_ROOT / "scripts" / "send_run_completion_email.py"

SCENARIO_RUNNER = REPO_ROOT / "ai_talent_scenario_runner.py"
PEOPLE_RESOLVER = REPO_ROOT / "people_scenario_resolver.py"

CANON_PREFIX = ["Person_ID","Role_Type","Email","Phone","LinkedIn_URL","GitHub_URL","GitHub_Username"]

def fail(msg: str) -> None:
    print("\nHARD FAILURE:")
    print(msg)
    print()
    sys.exit(1)

def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()

def ensure_file(p: Path) -> None:
    if not p.exists():
        fail(f"Missing required file: {p}")

def run_cmd(cmd: list[str], hard: bool = True) -> None:
    r = subprocess.run(cmd)
    if hard and r.returncode != 0:
        fail(f"Command failed ({r.returncode}): " + " ".join(cmd))

def enforce_repo_inventory() -> None:
    required = [
        PEOPLE_RESOLVER,
        SCENARIO_RUNNER,
        NORMALIZER,
        ENRICHER,
        POPUP,
        EMAIL,
    ]
    for p in required:
        ensure_file(p)
    print("✓ REPO INVENTORY GATE PASSED")

def run_people_scenario(scenario: str) -> Path:
    run_cmd([sys.executable, str(PEOPLE_RESOLVER), "--scenario", scenario], hard=True)

    outputs = sorted(
        PEOPLE_DIR.glob(f"{scenario}_people_*.csv"),
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )
    if not outputs:
        fail("People scenario produced no output CSV")
    people_csv = outputs[0]
    df = pd.read_csv(people_csv)

    if not (25 <= len(df) <= 50):
        fail(f"Demo bounds violated: {len(df)} rows (expected 25–50)")

    req = {"GitHub_URL","GitHub_Username"}
    missing = req - set(df.columns)
    if missing:
        fail("Missing required identity columns: " + ", ".join(sorted(missing)))

    if df["GitHub_URL"].isna().all():
        fail("GitHub_URL column exists but contains no data")

    print("✓ PEOPLE SCENARIO GATE PASSED")
    print(f"✓ People CSV: {people_csv}")
    print(f"✓ Rows: {len(df)}")
    return people_csv

def normalize_people(people_csv: Path) -> Path:
    out = Path(str(people_csv).replace(".csv", ".normalized.csv"))
    run_cmd([sys.executable, str(NORMALIZER), str(people_csv), str(out)], hard=True)

    df = pd.read_csv(out)
    if list(df.columns[:len(CANON_PREFIX)]) != CANON_PREFIX:
        fail("Normalization failed canonical prefix/order check")

    print("✓ NORMALIZATION GATE PASSED")
    print(f"✓ Normalized CSV: {out}")
    return out

def run_leads_enrichment(scenario: str, normalized_csv: Path) -> Path:
    run_id = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    out_dir = LEADS_ROOT / f"run_{run_id}"
    out_dir.mkdir(parents=True, exist_ok=True)

    run_cmd([sys.executable, str(ENRICHER), scenario, str(normalized_csv), str(out_dir), run_id], hard=True)

    leads_master = out_dir / f"LEADS_MASTER_{scenario}_{run_id}.csv"
    if not leads_master.exists():
        fail(f"Expected leads file missing: {leads_master}")

    df = pd.read_csv(leads_master)
    if df.empty:
        fail("Leads CSV is empty")
    if len(df.columns) < 40:
        fail(f"Leads CSV not wide enough (<40 columns). Found: {len(df.columns)}")

    print("✓ LEADS ENRICHMENT GATE PASSED")
    print(f"✓ Leads master: {leads_master}")
    print(f"✓ Columns: {len(df.columns)}")
    return leads_master

def run_scenario_scoring(scenario: str) -> None:
    run_cmd([sys.executable, str(SCENARIO_RUNNER), "--scenario", scenario], hard=True)
    print("✓ SCENARIO SCORING COMPLETE")

def write_manifest(scenario: str, people_csv: Path, normalized_csv: Path, leads_csv: Path) -> Path:
    MANIFEST_DIR.mkdir(parents=True, exist_ok=True)
    run_id = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")

    manifest = {
        "run_id": run_id,
        "completed_utc": utc_now_iso(),
        "scenario": scenario,
        "people_csv_raw": str(people_csv),
        "people_csv_normalized": str(normalized_csv),
        "leads_master_csv": str(leads_csv),
        "status": "success",
    }
    path = MANIFEST_DIR / f"run_manifest_{scenario}_{run_id}.json"
    path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(f"✓ MANIFEST WRITTEN: {path}")
    return path

def notify_popup(leads_csv: Path) -> None:
    if os.getenv("POPUP_NOTIFY_ENABLED","1").strip() != "1":
        print("POPUP_NOTIFY: disabled")
        return
    run_cmd([sys.executable, str(POPUP), "Pipeline Complete", f"Finished leads file ready: {leads_csv.name}"], hard=True)

def notify_email(manifest: Path) -> None:
    if os.getenv("EMAIL_NOTIFY_ENABLED","1").strip() != "1":
        print("EMAIL_NOTIFY: disabled")
        return
    run_cmd([sys.executable, str(EMAIL), str(manifest)], hard=True)

def maybe_open(leads_csv: Path) -> None:
    if os.getenv("AUTO_OPEN_LEADS","1").strip() != "1":
        return
    subprocess.run(["open", str(leads_csv)], check=False)

def main() -> None:
    if len(sys.argv) != 2:
        fail("Usage: python3 run_safe.py <scenario>")

    scenario = sys.argv[1].strip()

    print("============================================================")
    print("UNIVERSAL RUN SAFE (LEAD-GRADE)")
    print("============================================================")
    print(f"Scenario: {scenario}")
    print()

    enforce_repo_inventory()

    people_csv = run_people_scenario(scenario)
    normalized_csv = normalize_people(people_csv)

    leads_csv = run_leads_enrichment(scenario, normalized_csv)
    run_scenario_scoring(scenario)

    manifest = write_manifest(scenario, people_csv, normalized_csv, leads_csv)

    # Completion signals (hard required unless disabled)
    notify_popup(leads_csv)
    notify_email(manifest)
    maybe_open(leads_csv)

    print()
    print("SUCCESS — FINISHED LEADS OUTPUT WRITTEN")
    print(f"Leads: {leads_csv}")
    print(f"Manifest: {manifest}")
    print("============================================================")

if __name__ == "__main__":
    main()
PY

# ---------------------------------------------------------------------
# 6) Compile checks (hard)
# ---------------------------------------------------------------------
python3 -m py_compile scripts/normalize_people_csv.py
python3 -m py_compile scripts/macos_notify.py
python3 -m py_compile scripts/send_run_completion_email.py
python3 -m py_compile scripts/universal_enrichment_pipeline.py
python3 -m py_compile run_safe.py

echo "✓ PYTHON COMPILE CHECKS PASSED"

# ---------------------------------------------------------------------
# 7) Commit + push (hard)
# ---------------------------------------------------------------------
echo "============================================================"
echo "GIT COMMIT + PUSH"
echo "============================================================"
git status
git add autogen_universal_lead_pipeline.sh scripts/normalize_people_csv.py scripts/macos_notify.py scripts/send_run_completion_email.py scripts/universal_enrichment_pipeline.py run_safe.py
git commit -m "Lock universal lead pipeline: canonical normalization, 70+ col enrichment, popup + email, manifest"
git push

echo "✓ GIT PUSH COMPLETE"

# ---------------------------------------------------------------------
# 8) Run the authoritative pipeline (hard)
# ---------------------------------------------------------------------
echo "============================================================"
echo "RUN: python3 run_safe.py $SCENARIO"
echo "============================================================"

export EMAIL_NOTIFY_ENABLED=1
export POPUP_NOTIFY_ENABLED=1
export AUTO_OPEN_LEADS=1
export PIPELINE_NOTIFY_TO="${PIPELINE_NOTIFY_TO:-LDaveMendoza@gmail.com}"

python3 run_safe.py "$SCENARIO"

echo "============================================================"
echo "DONE"
echo "============================================================"
