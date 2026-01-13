#!/usr/bin/env bash
set -euo pipefail

# AI Talent Engine — Real People Quality Pack (Autogen)
# © 2025 L. David Mendoza
# Version: v1.0.0-real-people-quality
#
# Guarantees:
# - Real people only (GitHub identities); no placeholder people
# - Always emits ALL 82 canonical columns in order
# - Always emits Slim 24-column CSV projection after each run
# - GitHub.io emphasized: discover + crawl for public email/phone/resume links
# - Deterministic artifacts + manifest + GPT Slim stage required

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$REPO_ROOT"

mkdir -p tools schemas outputs/manifests outputs/people outputs/leads

write_exec () {
  local path="$1"
  local tmp="${path}.tmp"
  mkdir -p "$(dirname "$path")"
  cat > "$tmp"
  mv "$tmp" "$path"
  chmod 755 "$path"
  echo "[WROTE+X] $path"
}

write_file () {
  local path="$1"
  local tmp="${path}.tmp"
  mkdir -p "$(dirname "$path")"
  cat > "$tmp"
  mv "$tmp" "$path"
  chmod 644 "$path"
  echo "[WROTE] $path"
}

# ------------------------------------------------------------
# 1) Scenario Registry (locked list of role types + GitHub queries)
# ------------------------------------------------------------
write_file "scenario_registry.json" <<'JSON'
{
  "version": "v1.0.0",
  "note": "Authoritative scenario registry. Single source of truth for demo/scenario names and GitHub search seeds.",
  "scenarios": {
    "frontier": {
      "queries": [
        "llm researcher OR transformer OR scaling laws OR diffusion OR multimodal language:python",
        "cuda OR triton OR jax OR xla OR fsdp OR deepspeed researcher:python",
        "mistral OR llama OR qwen OR deepseek OR mixtral OR moe language:python"
      ]
    },
    "foundational_ai": {
      "queries": [
        "foundation model OR pretraining OR self-supervised OR transformer language:python",
        "mixture of experts OR moe OR routing OR sparse transformer language:python"
      ]
    },
    "ai_research_scientist": {
      "queries": [
        "iclr OR neurips OR icml OR acl OR emnlp language:python",
        "language model evaluation OR mmlu OR helm OR hellaswag language:python"
      ]
    },
    "research_scientist_llm": {
      "queries": [
        "instruction tuning OR sft OR preference modeling OR dpo language:python",
        "rlhf OR reward model OR ppo OR dpo language:python"
      ]
    },
    "rlhf_researcher": {
      "queries": [
        "rlhf OR reward modeling OR preference optimization OR dpo OR ppo language:python",
        "alignment OR safety OR red teaming OR eval harness language:python"
      ]
    },
    "alignment_researcher": {
      "queries": [
        "alignment OR interpretability OR mechanistic interpretability language:python",
        "evals OR safety benchmark OR red teaming language:python"
      ]
    },
    "ai_engineer": {
      "queries": [
        "langchain OR llamaindex OR rag OR vector database language:python",
        "vllm OR tgi OR tensorrt-llm OR triton inference language:python"
      ]
    },
    "genai_engineer": {
      "queries": [
        "rag OR retrieval augmented generation OR embeddings language:python",
        "llmops OR prompt routing OR agentic workflows language:python"
      ]
    },
    "machine_learning_engineer": {
      "queries": [
        "pytorch OR tensorflow OR jax language:python",
        "mlops OR model deployment OR feature store language:python"
      ]
    },
    "ml_engineer": {
      "queries": [
        "pytorch OR xgboost OR lightgbm language:python",
        "ml pipelines OR kubeflow OR airflow language:python"
      ]
    },
    "applied_ai_engineer": {
      "queries": [
        "rag OR vector search OR semantic search language:python",
        "production llm OR inference service OR api integration language:python"
      ]
    },
    "ai_performance_engineer": {
      "queries": [
        "tensorrt OR tensorrt-llm OR onnxruntime OR cuda graphs language:cpp",
        "triton OR flashattention OR kernel optimization language:python"
      ]
    },
    "inference_engineer": {
      "queries": [
        "vllm OR tgi OR triton inference OR sglang language:python",
        "quantization OR gptq OR awq OR gguf OR llama.cpp language:python"
      ]
    },
    "llm_inference_engineer": {
      "queries": [
        "paged attention OR kv cache OR speculative decoding language:python",
        "tensor parallel OR pipeline parallel OR inference serving language:python"
      ]
    },
    "model_optimization_engineer": {
      "queries": [
        "quantization OR pruning OR distillation language:python",
        "onnx OR tensorrt OR kernel fusion language:python"
      ]
    },
    "ai_infra": {
      "queries": [
        "kubernetes gpu OR nvidia gpu operator OR cuda language:yaml",
        "ray serve OR distributed serving OR orchestration language:python"
      ]
    },
    "ai_infrastructure_engineer": {
      "queries": [
        "kubernetes OR terraform OR observability gpu language:yaml",
        "distributed systems OR rpc OR service mesh language:go"
      ]
    },
    "ml_infra_engineer": {
      "queries": [
        "mlflow OR kubeflow OR feature store OR model registry language:python",
        "airflow OR dagster OR data pipelines language:python"
      ]
    },
    "platform_engineer_ai": {
      "queries": [
        "platform engineering OR internal developer platform gpu language:go",
        "kubernetes OR helm OR argo cd language:yaml"
      ]
    },
    "gpu_infra_engineer": {
      "queries": [
        "nvidia nccl OR infiniband OR rdma OR gpudirect language:cpp",
        "cuda OR triton OR performance profiling language:python"
      ]
    },
    "distributed_systems_engineer": {
      "queries": [
        "distributed systems OR consensus OR raft OR paxos language:go",
        "high throughput OR low latency OR rpc language:cpp"
      ]
    }
  }
}
JSON

# ------------------------------------------------------------
# 2) Canonical schema loader (82 columns)
# ------------------------------------------------------------
write_exec "tools/schema_loader.py" <<'PY'
#!/usr/bin/env python3
"""
AI Talent Engine — Canonical Schema Loader
© 2025 L. David Mendoza
Version: v1.0.0

Loads locked canonical people schema from:
  schemas/canonical_people_schema_82.json

Fail-closed if missing or malformed.
"""
from __future__ import annotations
import json
import os
from typing import List, Dict, Any

SCHEMA_PATH = os.path.join("schemas", "canonical_people_schema_82.json")

class SchemaError(RuntimeError):
    pass

def load_schema() -> Dict[str, Any]:
    if not os.path.exists(SCHEMA_PATH):
        raise SchemaError(
            f"Canonical schema JSON missing: {SCHEMA_PATH}\n"
            "Action: run:\n"
            "  python3 tools/extract_canonical_schema_82.py"
        )
    with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    if data.get("count") != 82 or "columns" not in data:
        raise SchemaError(f"Canonical schema JSON invalid: expected count=82, got {data.get('count')}")
    cols = data["columns"]
    if not isinstance(cols, list) or len(cols) != 82:
        raise SchemaError("Canonical schema JSON 'columns' must be a list of length 82.")
    names = [c.get("name") for c in cols]
    if any((not isinstance(n, str) or not n.strip()) for n in names):
        raise SchemaError("Canonical schema column names must be non-empty strings.")
    if len(set(names)) != 82:
        raise SchemaError("Canonical schema contains duplicate column names.")
    return data

def canonical_column_names() -> List[str]:
    data = load_schema()
    return [c["name"] for c in data["columns"]]
PY

# ------------------------------------------------------------
# 3) GitHub People Source (real identities; GitHub.io emphasized)
# ------------------------------------------------------------
write_exec "people_source_github.py" <<'PY'
#!/usr/bin/env python3
"""
AI Talent Engine — GitHub People Source (Real Identities)
© 2025 L. David Mendoza
Version: v1.0.0

Rules:
- Requires GITHUB_TOKEN (fail-closed)
- Collects real GitHub users via search
- Enriches with profile fields
- Emphasizes GitHub.io discovery + crawl for publicly posted email/phone/resume links
- No placeholder people, ever
"""

from __future__ import annotations

import json
import os
import re
import time
from dataclasses import dataclass
from typing import Dict, List, Optional, Set, Tuple
from urllib.parse import quote

import requests

EMAIL_RE = re.compile(r"[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}", re.IGNORECASE)
PHONE_RE = re.compile(r"(?:(?:\+?1[\s\-\.]?)?\(?\d{3}\)?[\s\-\.]?\d{3}[\s\-\.]?\d{4})")
RESUME_HINT_RE = re.compile(r"(resume|cv|curriculum|vitae)", re.IGNORECASE)
URL_RE = re.compile(r"https?://[^\s\"'<>]+", re.IGNORECASE)

@dataclass(frozen=True)
class GitHubUser:
    login: str
    html_url: str
    name: str = ""
    company: str = ""
    blog: str = ""
    location: str = ""
    bio: str = ""
    email: str = ""

@dataclass
class CrawlSignals:
    github_io_url: str = ""
    public_email: str = ""
    public_phone: str = ""
    resume_link: str = ""

class GitHubSourceError(RuntimeError):
    pass

def _token() -> str:
    t = os.getenv("GITHUB_TOKEN", "").strip()
    if not t:
        raise GitHubSourceError("Missing required env var: GITHUB_TOKEN")
    return t

def _session() -> requests.Session:
    s = requests.Session()
    s.headers.update({
        "Authorization": f"Bearer {_token()}",
        "Accept": "application/vnd.github+json",
        "User-Agent": "AI-Talent-Engine/real-people-source"
    })
    return s

def _sleep_rate(limit_sleep: float = 1.2) -> None:
    time.sleep(limit_sleep)

def search_users(queries: List[str], target_n: int) -> List[str]:
    sess = _session()
    seen: Set[str] = set()
    out: List[str] = []

    for q in queries:
        page = 1
        while page <= 10 and len(out) < target_n:
            url = f"https://api.github.com/search/users?q={quote(q)}&per_page=30&page={page}"
            r = sess.get(url, timeout=30)
            if r.status_code != 200:
                raise GitHubSourceError(f"GitHub search failed ({r.status_code}): {r.text[:400]}")
            data = r.json()
            items = data.get("items", [])
            if not items:
                break
            for it in items:
                login = (it.get("login") or "").strip()
                if not login or login in seen:
                    continue
                seen.add(login)
                out.append(login)
                if len(out) >= target_n:
                    break
            page += 1
            _sleep_rate()
        if len(out) >= target_n:
            break

    return out

def fetch_user(login: str) -> GitHubUser:
    sess = _session()
    url = f"https://api.github.com/users/{quote(login)}"
    r = sess.get(url, timeout=30)
    if r.status_code != 200:
        raise GitHubSourceError(f"GitHub user fetch failed ({r.status_code}) for {login}: {r.text[:200]}")
    d = r.json()
    return GitHubUser(
        login=login,
        html_url=d.get("html_url") or f"https://github.com/{login}",
        name=d.get("name") or "",
        company=d.get("company") or "",
        blog=d.get("blog") or "",
        location=d.get("location") or "",
        bio=d.get("bio") or "",
        email=d.get("email") or "",
    )

def _normalize_url(u: str) -> str:
    u = (u or "").strip()
    if not u:
        return ""
    if u.startswith("http://") or u.startswith("https://"):
        return u
    return "https://" + u

def guess_github_io(login: str) -> str:
    return f"https://{login}.github.io/"

def _fetch_text(url: str) -> str:
    try:
        r = requests.get(url, timeout=20, headers={"User-Agent": "AI-Talent-Engine/github-io-crawler"})
        if r.status_code != 200:
            return ""
        ctype = (r.headers.get("content-type") or "").lower()
        if "text" not in ctype and "html" not in ctype:
            return ""
        return r.text[:300000]
    except Exception:
        return ""

def crawl_for_signals(base_url: str) -> CrawlSignals:
    base_url = _normalize_url(base_url)
    if not base_url:
        return CrawlSignals()

    text = _fetch_text(base_url)
    if not text:
        return CrawlSignals(github_io_url=base_url)

    emails = EMAIL_RE.findall(text)
    phones = PHONE_RE.findall(text)
    urls = URL_RE.findall(text)

    resume_link = ""
    for u in urls:
        if RESUME_HINT_RE.search(u):
            resume_link = u
            break

    return CrawlSignals(
        github_io_url=base_url,
        public_email=emails[0] if emails else "",
        public_phone=phones[0] if phones else "",
        resume_link=resume_link
    )

def build_people(scenario: str, queries: List[str], min_n: int, max_n: int) -> Tuple[List[GitHubUser], Dict[str, CrawlSignals]]:
    target = max(min_n, min(max_n, 50))
    logins = search_users(queries, target_n=target)
    if len(logins) < min_n:
        raise GitHubSourceError(
            f"Insufficient real people for scenario '{scenario}'. "
            f"Found {len(logins)}, required at least {min_n}. "
            "Adjust scenario queries or widen search."
        )

    users: List[GitHubUser] = []
    crawls: Dict[str, CrawlSignals] = {}

    for login in logins[:max_n]:
        u = fetch_user(login)
        users.append(u)

        # GitHub.io emphasis:
        io_url = guess_github_io(login)
        io_sig = crawl_for_signals(io_url)

        # Also crawl profile blog if present
        blog_sig = CrawlSignals()
        blog_url = _normalize_url(u.blog)
        if blog_url and blog_url != io_url:
            blog_sig = crawl_for_signals(blog_url)

        # Choose best signals
        best = io_sig
        if (not best.public_email and blog_sig.public_email) or (not best.resume_link and blog_sig.resume_link):
            # Prefer signals that actually contain contact/resume
            best = CrawlSignals(
                github_io_url=io_sig.github_io_url or blog_sig.github_io_url,
                public_email=blog_sig.public_email or io_sig.public_email,
                public_phone=blog_sig.public_phone or io_sig.public_phone,
                resume_link=blog_sig.resume_link or io_sig.resume_link,
            )

        crawls[login] = best
        _sleep_rate(0.9)

    return users, crawls
PY

# ------------------------------------------------------------
# 4) Slim Projector (82 -> Slim 24 columns)
# ------------------------------------------------------------
write_exec "slim_projector.py" <<'PY'
#!/usr/bin/env python3
"""
AI Talent Engine — Slim Projector (82 -> GPT Slim 24)
© 2025 L. David Mendoza
Version: v1.0.0

Produces a slim CSV with these 24 columns (in order):
- Person_ID
- Full_Name
- AI_Role_Type
- Current_Title
- Current_Company
- Determinative_Skill_Areas
- Benchmarks_Worked_On
- Primary_Model_Families
- Explicit_Model_Names
- Production_vs_Research_Indicator
- Training_or_Alignment_Methods
- RLHF_Alignment_Signals
- Systems_or_Retrieval_Architectures
- Inference_or_Deployment_Signals
- Inference_Training_Infra_Signals
- Key_GitHub_AI_Repos
- GitHub_Repo_Evidence_Why
- Downstream_Adoption_Signal
- Publication_Count
- Citation_Count_Raw
- Citation_Velocity_3yr
- Influence_Tier
- Resume_Link
- GitHub_IO_URL

Mapping is best-effort from existing 82 columns; missing fields remain blank.
"""

from __future__ import annotations
import os
import pandas as pd
from typing import Dict, List

SLIM_COLS: List[str] = [
    "Person_ID",
    "Full_Name",
    "AI_Role_Type",
    "Current_Title",
    "Current_Company",
    "Determinative_Skill_Areas",
    "Benchmarks_Worked_On",
    "Primary_Model_Families",
    "Explicit_Model_Names",
    "Production_vs_Research_Indicator",
    "Training_or_Alignment_Methods",
    "RLHF_Alignment_Signals",
    "Systems_or_Retrieval_Architectures",
    "Inference_or_Deployment_Signals",
    "Inference_Training_Infra_Signals",
    "Key_GitHub_AI_Repos",
    "GitHub_Repo_Evidence_Why",
    "Downstream_Adoption_Signal",
    "Publication_Count",
    "Citation_Count_Raw",
    "Citation_Velocity_3yr",
    "Influence_Tier",
    "Resume_Link",
    "GitHub_IO_URL"
]

# Best-effort mapping keys from the 82 schema.
# If your 82 schema uses different names, projector will still emit blanks (acceptable).
CANDIDATE_MAP: Dict[str, List[str]] = {
    "Person_ID": ["Person_ID"],
    "Full_Name": ["Full_Name", "Name", "FullName"],
    "AI_Role_Type": ["Role_Type", "AI_Role_Type"],
    "Current_Title": ["Current_Title", "Title"],
    "Current_Company": ["Current_Company", "Company"],
    "Resume_Link": ["Resume_Link", "Resume_URL", "CV_URL"],
    "GitHub_IO_URL": ["GitHub_IO_URL", "Github.io", "Github_IO", "GitHubIO"],
    "Key_GitHub_AI_Repos": ["Key_GitHub_AI_Repos", "GitHub_Repos", "Github_Repos"],
}

def _pick(row: pd.Series, candidates: List[str]) -> str:
    for c in candidates:
        if c in row.index:
            v = row.get(c)
            if pd.notna(v):
                s = str(v).strip()
                if s:
                    return s
    return ""

def project_slim(df: pd.DataFrame) -> pd.DataFrame:
    out = []
    for _, row in df.iterrows():
        slim_row = {c: "" for c in SLIM_COLS}
        for slim_col, candidates in CANDIDATE_MAP.items():
            slim_row[slim_col] = _pick(row, candidates)
        out.append(slim_row)
    return pd.DataFrame(out, columns=SLIM_COLS)

def write_slim(in_csv: str, out_csv: str) -> None:
    df = pd.read_csv(in_csv)
    slim = project_slim(df)
    os.makedirs(os.path.dirname(out_csv), exist_ok=True)
    slim.to_csv(out_csv, index=False)
PY

# ------------------------------------------------------------
# 5) GPT Slim stage (mandatory; consumes Slim CSV)
# ------------------------------------------------------------
write_exec "tools/gpt_slim_stage.py" <<'PY'
#!/usr/bin/env python3
"""
AI Talent Engine — GPT Slim Stage (Mandatory)
© 2025 L. David Mendoza
Version: v1.1.0-slim-csv

Produces:
- outputs/leads/run_<run_id>/gpt_slim_request.json
- outputs/leads/run_<run_id>/gpt_slim_result.json

Fail-closed if runner missing or output missing.
"""

from __future__ import annotations
import json
import os
import subprocess
from typing import Dict, Any

def write_json(path: str, obj: Dict[str, Any]) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2, sort_keys=True)

def run_gpt_slim(run_dir: str, scenario: str, leads_csv: str, slim_csv: str, schema_json: str) -> Dict[str, str]:
    req = os.path.join(run_dir, "gpt_slim_request.json")
    out = os.path.join(run_dir, "gpt_slim_result.json")

    request_obj = {
        "scenario": scenario,
        "leads_csv": leads_csv,
        "slim_csv": slim_csv,
        "canonical_schema_json": schema_json,
        "required": True
    }
    write_json(req, request_obj)

    runner = "gpt_slim_runner.py"
    if not os.path.exists(runner):
        raise RuntimeError(
            "GPT Slim runner missing at repo root: gpt_slim_runner.py\n"
            "This stage is mandatory."
        )

    cmd = ["python3", runner, "--request", req, "--out", out]
    p = subprocess.run(cmd, capture_output=True, text=True)
    if p.returncode != 0:
        raise RuntimeError("GPT Slim runner failed:\n" + p.stdout + "\n" + p.stderr)

    if not os.path.exists(out):
        raise RuntimeError("GPT Slim output missing after successful runner execution: " + out)

    return {"request": req, "result": out}
PY

# ------------------------------------------------------------
# 6) Manifest writer
# ------------------------------------------------------------
write_exec "tools/manifest.py" <<'PY'
#!/usr/bin/env python3
"""
AI Talent Engine — Run Manifest Writer
© 2025 L. David Mendoza
Version: v1.0.0
"""
from __future__ import annotations
import hashlib
import json
import os
from datetime import datetime, timezone
from typing import Dict, Any

def _sha256_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()

def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")

def write_manifest(manifest_path: str, payload: Dict[str, Any]) -> None:
    os.makedirs(os.path.dirname(manifest_path), exist_ok=True)
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, sort_keys=True)

def build_manifest(run_id: str, scenario: str, mode: str, artifacts: Dict[str, str]) -> Dict[str, Any]:
    hashed = {}
    for k, p in artifacts.items():
        if p and os.path.exists(p):
            hashed[k] = {"path": p, "sha256": _sha256_file(p)}
        else:
            hashed[k] = {"path": p, "sha256": None}
    return {
        "run_id": run_id,
        "scenario": scenario,
        "mode": mode,
        "created_utc": utc_now(),
        "artifacts": hashed
    }
PY

# ------------------------------------------------------------
# 7) People scenario resolver (REAL people; 82 columns guaranteed)
# ------------------------------------------------------------
write_exec "people_scenario_resolver.py" <<'PY'
#!/usr/bin/env python3
"""
AI Talent Engine — People Scenario Resolver (Real People, Schema-First)
© 2025 L. David Mendoza
Version: v1.0.0-real-people

Guarantees:
- Real GitHub identities only; no placeholder people
- Always emits ALL 82 canonical columns in correct order
- GitHub.io emphasized for public email/phone/resume link extraction
"""

from __future__ import annotations

import json
import os
import uuid
from typing import Dict, List, Tuple

import pandas as pd

from tools.schema_loader import canonical_column_names
from people_source_github import build_people, GitHubUser, CrawlSignals

CANON_COLS = canonical_column_names()
REGISTRY_PATH = "scenario_registry.json"

def _new_run_id() -> str:
    return uuid.uuid4().hex[:12]

def _load_registry() -> Dict[str, Dict]:
    if not os.path.exists(REGISTRY_PATH):
        raise RuntimeError(f"Missing scenario registry: {REGISTRY_PATH}")
    with open(REGISTRY_PATH, "r", encoding="utf-8") as f:
        d = json.load(f)
    return d.get("scenarios", {})

def _set_if_exists(row: Dict[str, str], col: str, val: str) -> None:
    if col in row and val is not None:
        row[col] = str(val).strip()

def _apply_identity(row: Dict[str, str], scenario: str, idx: int, u: GitHubUser, c: CrawlSignals) -> Dict[str, str]:
    # Fill only if the 82 schema has the column.
    _set_if_exists(row, "Person_ID", f"{scenario}_{idx:04d}")
    _set_if_exists(row, "Role_Type", scenario)

    # Common identity columns (best-effort; only fill if present)
    _set_if_exists(row, "Full_Name", u.name or u.login)
    _set_if_exists(row, "GitHub_Username", u.login)
    _set_if_exists(row, "GitHub_URL", u.html_url)

    # Public contact signals (GitHub profile email if public, then github.io/blog crawl)
    email = u.email or c.public_email
    phone = c.public_phone
    resume = c.resume_link
    ghio = c.github_io_url

    _set_if_exists(row, "Email", email)
    _set_if_exists(row, "Phone", phone)
    _set_if_exists(row, "Resume_Link", resume)
    _set_if_exists(row, "GitHub_IO_URL", ghio)

    _set_if_exists(row, "Current_Company", u.company)
    _set_if_exists(row, "Location", u.location)
    _set_if_exists(row, "Website", u.blog)
    _set_if_exists(row, "Bio", u.bio)

    return row

def generate_people_for_scenario(scenario: str, mode: str, min_rows: int, max_rows: int) -> pd.DataFrame:
    scenarios = _load_registry()
    if scenario not in scenarios:
        raise RuntimeError(f"Unknown scenario '{scenario}'. Add it to scenario_registry.json")
    queries = scenarios[scenario].get("queries") or []
    if not queries:
        raise RuntimeError(f"Scenario '{scenario}' has no queries in scenario_registry.json")

    if mode == "demo":
        min_n = max(25, min_rows)
        max_n = min(50, max_rows)
    else:
        min_n = max(25, min_rows)
        max_n = max_rows

    users, crawls = build_people(scenario=scenario, queries=queries, min_n=min_n, max_n=max_n)

    rows: List[Dict[str, str]] = []
    for i, u in enumerate(users, start=1):
        row = {c: "" for c in CANON_COLS}
        c = crawls.get(u.login) or CrawlSignals()
        row = _apply_identity(row, scenario, i, u, c)
        rows.append(row)

    df = pd.DataFrame(rows, columns=CANON_COLS)

    if list(df.columns) != CANON_COLS:
        raise RuntimeError("Schema violation: people dataframe columns differ from canonical 82 spine.")
    if len(df) < min_n:
        raise RuntimeError(f"Demo/scenario bounds violated: got {len(df)}, required at least {min_n}")
    if mode == "demo" and len(df) > 50:
        raise RuntimeError(f"Demo max violated: got {len(df)}, max 50")

    return df

def write_people_master(df: pd.DataFrame, out_path: str) -> None:
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    df.to_csv(out_path, index=False)

def run_people(scenario: str, mode: str, outdir: str, min_rows: int, max_rows: int) -> str:
    df = generate_people_for_scenario(scenario=scenario, mode=mode, min_rows=min_rows, max_rows=max_rows)
    out_path = os.path.join(outdir, "people_master.csv")
    write_people_master(df, out_path)
    return out_path
PY

# ------------------------------------------------------------
# 8) run_safe.py (single canonical pipeline; emits full + slim; mandatory GPT Slim)
# ------------------------------------------------------------
write_exec "run_safe.py" <<'PY'
#!/usr/bin/env python3
"""
AI Talent Engine — Safe Runner (Canonical, Real People, Single Path)
© 2025 L. David Mendoza
Version: v1.1.0-real-people

Pipeline:
- Preflight guard must pass
- Canonical schema (82) must exist
- Resolver pulls real people (GitHub) with GitHub.io emphasis
- Writes:
  - outputs/people/people_master.csv
  - outputs/leads/run_<run_id>/LEADS_MASTER_<scenario>_<run_id>.csv
  - outputs/leads/run_<run_id>/LEADS_SLIM_<scenario>_<run_id>.csv
  - outputs/leads/run_<run_id>/gpt_slim_request.json
  - outputs/leads/run_<run_id>/gpt_slim_result.json
  - outputs/manifests/run_manifest_<scenario>_<run_id>.json
"""

from __future__ import annotations

import argparse
import os
import shutil
import uuid
from datetime import datetime, timezone

from tools.schema_loader import load_schema
from tools.manifest import build_manifest, write_manifest
from tools.gpt_slim_stage import run_gpt_slim
from people_scenario_resolver import run_people
from slim_projector import write_slim

def utc_stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")

def new_run_id() -> str:
    return f"{utc_stamp()}_{uuid.uuid4().hex[:8]}"

def ensure_preflight_ok() -> None:
    if not os.path.exists("./preflight_duplicate_guard.py"):
        raise RuntimeError("Missing preflight guard: preflight_duplicate_guard.py")
    rc = os.system("./preflight_duplicate_guard.py")
    if rc != 0:
        raise RuntimeError("Preflight guard failed. Fix duplicates before running.")

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("scenario")
    ap.add_argument("--mode", choices=["demo", "real"], default="demo")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    ensure_preflight_ok()
    schema = load_schema()

    run_id = new_run_id()
    scenario = args.scenario
    mode = args.mode

    people_dir = os.path.join("outputs", "people")
    leads_dir = os.path.join("outputs", "leads", f"run_{run_id}")
    manifest_path = os.path.join("outputs", "manifests", f"run_manifest_{scenario}_{run_id}.json")

    os.makedirs(people_dir, exist_ok=True)
    os.makedirs(leads_dir, exist_ok=True)

    if args.dry_run:
        print("DRY-RUN OK")
        print("scenario:", scenario)
        print("mode:", mode)
        print("run_id:", run_id)
        print("canonical_schema_count:", schema.get("count"))
        return 0

    people_master = run_people(
        scenario=scenario,
        mode=mode,
        outdir=people_dir,
        min_rows=25,
        max_rows=50 if mode == "demo" else 5000
    )

    leads_master = os.path.join(leads_dir, f"LEADS_MASTER_{scenario}_{run_id}.csv")
    shutil.copyfile(people_master, leads_master)

    leads_slim = os.path.join(leads_dir, f"LEADS_SLIM_{scenario}_{run_id}.csv")
    write_slim(leads_master, leads_slim)

    slim = run_gpt_slim(
        run_dir=leads_dir,
        scenario=scenario,
        leads_csv=leads_master,
        slim_csv=leads_slim,
        schema_json=os.path.join("schemas", "canonical_people_schema_82.json")
    )

    manifest = build_manifest(
        run_id=run_id,
        scenario=scenario,
        mode=mode,
        artifacts={
            "people_master_csv": people_master,
            "leads_master_csv": leads_master,
            "leads_slim_csv": leads_slim,
            "gpt_slim_request_json": slim["request"],
            "gpt_slim_result_json": slim["result"],
            "canonical_schema_json": os.path.join("schemas", "canonical_people_schema_82.json"),
            "scenario_registry_json": "scenario_registry.json"
        }
    )
    write_manifest(manifest_path, manifest)

    print("✅ RUN OK")
    print("people_master:", people_master)
    print("leads_master:", leads_master)
    print("leads_slim:", leads_slim)
    print("manifest:", manifest_path)
    print("gpt_slim_result:", slim["result"])
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
PY

# ------------------------------------------------------------
# 9) start launcher (child-proof)
# ------------------------------------------------------------
write_exec "start" <<'SH'
#!/usr/bin/env bash
set -euo pipefail
cd /Users/davemendoza/Desktop/Research_First_Sourcer_Automation

echo "🚀 AI Talent Engine ready"
echo "Examples:"
echo "  run demo frontier"
echo "  run demo ai_engineer"
echo "  run real rlhf_researcher"
echo "  confirm last"

function run() {
  local mode="$1"
  local scenario="$2"

  if [[ "$mode" == "demo" ]]; then
    python3 run_safe.py "$scenario" --mode demo
  elif [[ "$mode" == "real" ]]; then
    python3 run_safe.py "$scenario" --mode real
  else
    echo "Unknown mode: $mode"
    return 2
  fi
}

function confirm() {
  local last
  last="$(ls -t outputs/leads/run_*/gpt_slim_result.json 2>/dev/null | head -n 1 || true)"
  if [[ -z "$last" ]]; then
    echo "No GPT Slim results found."
    return 1
  fi
  echo "Last GPT Slim result:"
  echo "  $last"
}

export -f run
export -f confirm

echo "Type: run demo frontier"
SH

echo "============================================"
echo "Real People Quality Pack generated."
echo "Next commands (copy/paste):"
echo "  chmod +x autogen_real_people_quality_pack.sh"
echo "  bash autogen_real_people_quality_pack.sh"
echo "  python3 run_safe.py frontier --mode demo"
echo "============================================"
