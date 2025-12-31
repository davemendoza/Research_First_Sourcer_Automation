#!/usr/bin/env bash
set -euo pipefail

STAMP="$(date +"%Y%m%d_%H%M%S")"
BACKUP_DIR="backups/volume_expansion_${STAMP}"
mkdir -p "$BACKUP_DIR"

backup() {
  if [ -f "$1" ]; then
    cp "$1" "$BACKUP_DIR/"
    echo "🗂️  Backed up $1 → $BACKUP_DIR/"
  fi
}

for f in volume_expansion.yaml github_api_ultra.py scenario_matrix_builder_ultra.py people_volume_expander_ultra.py run_volume_expansion_ultra.py; do
  backup "$f"
done

mkdir -p data/scenarios output/people checkpoints logs

###############################################################################
# volume_expansion.yaml
###############################################################################
cat <<'YAML' > volume_expansion.yaml
# AI Talent Engine – Volume Expansion Config
# © 2025 L. David Mendoza
version: v1.0-ultra-volume-expansion

scenario_matrix_input: scenario_control_matrix.xlsx
scenario_matrix_output: data/scenarios/scenario_control_matrix_EXPANDED.xlsx

output_root: output/people
checkpoint_root: checkpoints
log_dir: logs

github:
  api_base: https://api.github.com
  per_page: 100

volume:
  # user search volume per scenario (higher = more people)
  user_search_per_scenario: 800
  user_search_pages_cap: 10

  # repo search volume per scenario (repo-first = big volume)
  repo_search_per_scenario: 120
  repo_search_pages_cap: 6

  # contributors per repo
  contributors_per_repo: 300

  # hard safety caps (prevent runaway)
  max_total_people: 25000
  max_total_repos: 5000

rate_limit:
  min_remaining_search: 2
  min_remaining_core: 50
  backoff_seconds: 20
  jitter_seconds: 7

hygiene:
  dedupe_key: "login"
  require_html_url: true

logging:
  print_every_n_people: 250
  print_every_n_repos: 25
YAML

###############################################################################
# github_api_ultra.py
###############################################################################
cat <<'PY' > github_api_ultra.py
#!/usr/bin/env python3
"""
GitHub API Ultra Helper (Bearer token hardened)
© 2025 L. David Mendoza
"""
from __future__ import annotations

import os, time, random
import requests

TOKEN = os.getenv("GITHUB_TOKEN")
if not TOKEN:
    raise SystemExit("❌ GITHUB_TOKEN not set. Run: export GITHUB_TOKEN=github_pat_xxx")

HEADERS = {
    "Authorization": f"Bearer {TOKEN}",
    "Accept": "application/vnd.github+json",
    "User-Agent": "AI-Talent-Engine-Volume-Expansion"
}

def _sleep(backoff: int, jitter: int) -> None:
    time.sleep(backoff + random.randint(0, max(jitter, 1)))

def rate_limit(api_base: str) -> dict:
    r = requests.get(f"{api_base}/rate_limit", headers=HEADERS, timeout=30)
    r.raise_for_status()
    return r.json()

def guard_rate_limit(api_base: str, min_search: int, min_core: int, backoff: int, jitter: int) -> None:
    rl = rate_limit(api_base)
    core = rl.get("resources", {}).get("core", {})
    search = rl.get("resources", {}).get("search", {})
    core_rem = int(core.get("remaining", 0))
    search_rem = int(search.get("remaining", 0))

    if search_rem <= min_search or core_rem <= min_core:
        _sleep(backoff, jitter)

def get_json(url: str, params: dict | None = None, api_base: str | None = None,
             min_search: int = 2, min_core: int = 50, backoff: int = 20, jitter: int = 7) -> dict | list:
    if api_base:
        guard_rate_limit(api_base, min_search, min_core, backoff, jitter)

    r = requests.get(url, headers=HEADERS, params=params, timeout=45)
    if r.status_code == 401:
        raise RuntimeError("❌ 401 Unauthorized. Token valid? Must use Bearer and correct token.")
    if r.status_code == 403:
        # Often rate limit or abuse protection. Back off and retry once.
        _sleep(backoff, jitter)
        r = requests.get(url, headers=HEADERS, params=params, timeout=45)

    r.raise_for_status()
    return r.json()
PY

chmod +x github_api_ultra.py

###############################################################################
# scenario_matrix_builder_ultra.py
###############################################################################
cat <<'PY' > scenario_matrix_builder_ultra.py
#!/usr/bin/env python3
"""
Scenario Matrix Builder (Ultra Expansion)
- Takes your scenario_control_matrix.xlsx (11 rows)
- Expands to 100+ high-recall variants
- Outputs: data/scenarios/scenario_control_matrix_EXPANDED.xlsx
© 2025 L. David Mendoza
"""
import pandas as pd
from pathlib import Path
import yaml

EXPAND_MAP = {
    # Foundational / frontier expansions
    "LLM researcher language model": [
        "large language model researcher",
        "language model research engineer",
        "foundation model researcher",
        "transformer researcher",
        "pretraining language model",
        "LLM training",
        "scaling laws transformer",
        "mixture of experts transformer",
        "instruction tuning",
        "tokenizer language model",
    ],
    "pretraining transformer": [
        "transformer pretraining",
        "masked language model",
        "causal language model training",
        "distributed pretraining",
        "data pipeline pretraining",
        "FSDP pretraining",
        "DeepSpeed pretraining",
        "Megatron pretraining",
    ],
    "RLHF reward model": [
        "reinforcement learning from human feedback",
        "reward modeling",
        "preference optimization",
        "DPO alignment",
        "PPO RLHF",
        "SFT RLHF",
        "alignment engineer",
        "policy optimization LLM",
    ],

    # Applied
    "generative ai engineer": [
        "genai engineer",
        "LLM engineer",
        "LLMOps",
        "prompt + LangChain",
        "agentic workflows",
        "tool calling",
        "structured generation",
    ],
    "RAG langchain llamaindex": [
        "retrieval augmented generation",
        "RAG pipeline",
        "LangChain RAG",
        "LlamaIndex RAG",
        "vector database RAG",
        "FAISS retrieval",
        "embedding pipeline",
        "reranking RAG",
        "hybrid search RAG",
    ],
    "healthcare AI machine learning": [
        "medical imaging deep learning",
        "clinical NLP",
        "biomedical machine learning",
        "health ML engineer",
        "healthcare LLM",
        "radiology deep learning",
    ],

    # Infra / performance
    "CUDA inference optimization": [
        "TensorRT LLM",
        "Triton inference",
        "vLLM inference",
        "GPU kernel optimization",
        "FlashAttention",
        "quantization inference",
        "PagedAttention",
        "ONNX runtime GPU",
    ],
    "ML systems distributed training": [
        "distributed training",
        "DeepSpeed ZeRO",
        "FSDP PyTorch",
        "NCCL collective",
        "parameter server",
        "Ray distributed training",
        "Kubernetes ML platform",
        "MLOps platform",
    ],
    "AI platform engineering": [
        "ML platform",
        "LLM platform",
        "inference platform",
        "model serving platform",
        "feature store platform",
        "observability ML",
    ],

    # Broad control expansions
    "AI engineer machine learning": [
        "machine learning engineer",
        "applied machine learning",
        "deep learning engineer",
        "ML engineer PyTorch",
        "ML engineer TensorFlow",
    ],
    "machine learning engineer": [
        "applied ML engineer",
        "production ML engineer",
        "MLOps engineer",
        "model serving engineer",
    ],
}

def main():
    cfg = yaml.safe_load(open("volume_expansion.yaml"))
    inp = cfg["scenario_matrix_input"]
    out = cfg["scenario_matrix_output"]

    base = pd.read_excel(inp)

    required = {"scenario", "seed_type", "seed_value", "tier", "category"}
    missing = required - set(base.columns)
    if missing:
        raise SystemExit(f"❌ Scenario matrix missing columns: {missing}")

    rows = []
    for _, r in base.iterrows():
        seed = str(r["seed_value"]).strip()
        rows.append(r.to_dict())

        # Expand if we have a mapping. If not, still add a few generic expansions.
        variants = EXPAND_MAP.get(seed, [])
        if not variants:
            variants = [
                seed,
                f"{seed} engineer",
                f"{seed} research",
                f"{seed} open source",
            ]

        for i, v in enumerate(variants, start=1):
            rr = r.to_dict()
            rr["scenario"] = f"{r['scenario']}_EXP_{i:02d}"
            rr["seed_type"] = "github_search"
            rr["seed_value"] = v
            rows.append(rr)

    expanded = pd.DataFrame(rows).drop_duplicates(subset=["seed_value", "tier", "category"]).reset_index(drop=True)

    Path(out).parent.mkdir(parents=True, exist_ok=True)
    expanded.to_excel(out, index=False)

    # Also overwrite the root scenario_control_matrix.xlsx so the rest of your tooling stays aligned
    expanded.to_excel("scenario_control_matrix.xlsx", index=False)

    print("✅ Scenario expansion complete")
    print(f"Base rows: {len(base)}")
    print(f"Expanded rows: {len(expanded)}")
    print(f"Wrote: {out}")
    print("Synced: scenario_control_matrix.xlsx (root)")
if __name__ == "__main__":
    main()
PY

chmod +x scenario_matrix_builder_ultra.py

###############################################################################
# people_volume_expander_ultra.py
###############################################################################
cat <<'PY' > people_volume_expander_ultra.py
#!/usr/bin/env python3
"""
People Volume Expander (User search + Repo-first + Contributors)
© 2025 L. David Mendoza

Outputs:
- people_master.csv (expanded)
- provenance columns: discovered_via, source_query, source_repo
- checkpointed progress (resume-safe)
"""
import os, json, hashlib
from datetime import datetime, timezone
from pathlib import Path
import pandas as pd
import yaml

from github_api_ultra import get_json

def sha(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()[:16]

def load_cfg():
    return yaml.safe_load(open("volume_expansion.yaml"))

def checkpoint_path(root: str, name: str) -> Path:
    Path(root).mkdir(parents=True, exist_ok=True)
    return Path(root) / name

def save_jsonl(path: Path, records: list[dict]) -> None:
    with path.open("a", encoding="utf-8") as f:
        for r in records:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

def read_jsonl(path: Path) -> list[dict]:
    if not path.exists():
        return []
    out = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                out.append(json.loads(line))
    return out

def search_users(api_base: str, query: str, per_page: int, pages_cap: int) -> list[dict]:
    items = []
    for page in range(1, pages_cap + 1):
        url = f"{api_base}/search/users"
        params = {"q": query, "per_page": per_page, "page": page}
        data = get_json(url, params=params, api_base=api_base)
        batch = data.get("items", [])
        if not batch:
            break
        items.extend(batch)
    return items

def search_repos(api_base: str, query: str, per_page: int, pages_cap: int) -> list[dict]:
    items = []
    for page in range(1, pages_cap + 1):
        url = f"{api_base}/search/repositories"
        params = {"q": query, "per_page": per_page, "page": page, "sort": "stars"}
        data = get_json(url, params=params, api_base=api_base)
        batch = data.get("items", [])
        if not batch:
            break
        items.extend(batch)
    return items

def repo_contributors(api_base: str, full_name: str, per_page: int, pages_cap: int) -> list[dict]:
    # full_name = owner/repo
    items = []
    for page in range(1, pages_cap + 1):
        url = f"{api_base}/repos/{full_name}/contributors"
        params = {"per_page": per_page, "page": page}
        batch = get_json(url, params=params, api_base=api_base)
        if not isinstance(batch, list) or not batch:
            break
        items.extend(batch)
    return items

def main():
    cfg = load_cfg()
    api_base = cfg["github"]["api_base"]
    per_page = int(cfg["github"]["per_page"])

    vol = cfg["volume"]
    rl = cfg["rate_limit"]
    logcfg = cfg["logging"]

    out_root = Path(cfg["output_root"])
    ck_root = Path(cfg["checkpoint_root"])
    out_root.mkdir(parents=True, exist_ok=True)
    ck_root.mkdir(parents=True, exist_ok=True)

    ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    run_dir = out_root / f"VOL_{ts}"
    run_dir.mkdir(parents=True, exist_ok=True)

    scenario_xlsx = cfg["scenario_matrix_input"]
    scenarios = pd.read_excel(scenario_xlsx)

    required = {"scenario", "seed_value", "tier", "category"}
    missing = required - set(scenarios.columns)
    if missing:
        raise SystemExit(f"❌ Scenario matrix missing columns: {missing}")

    # Resume-safe checkpoints
    people_ck = checkpoint_path(str(ck_root), "people.jsonl")
    repos_ck = checkpoint_path(str(ck_root), "repos.jsonl")

    seen_people = {r.get("login"): r for r in read_jsonl(people_ck) if r.get("login")}
    seen_repos = {r.get("full_name"): r for r in read_jsonl(repos_ck) if r.get("full_name")}

    total_people_limit = int(vol["max_total_people"])
    total_repo_limit = int(vol["max_total_repos"])

    print("🚀 Volume Expansion Starting")
    print(f"Scenarios: {len(scenarios)}")
    print(f"Resume people: {len(seen_people)}")
    print(f"Resume repos: {len(seen_repos)}")
    print(f"Run dir: {run_dir}")

    people_added = 0
    repos_added = 0

    for i, s in scenarios.iterrows():
        scenario = str(s["scenario"])
        q = str(s["seed_value"]).strip()
        tier = str(s["tier"])
        category = str(s["category"])

        # USER SEARCH (scaled)
        user_q = q
        user_items = search_users(api_base, user_q, per_page, int(vol["user_search_pages_cap"]))
        user_items = user_items[: int(vol["user_search_per_scenario"])]

        new_people_records = []
        for u in user_items:
            login = u.get("login")
            if not login:
                continue
            if login in seen_people:
                continue
            rec = {
                "login": login,
                "html_url": u.get("html_url"),
                "scenario": scenario,
                "tier": tier,
                "category": category,
                "discovered_via": "github_user_search",
                "source_query": user_q,
                "source_repo": "",
                "discovered_at_utc": datetime.now(timezone.utc).isoformat(),
            }
            seen_people[login] = rec
            new_people_records.append(rec)

        if new_people_records:
            save_jsonl(people_ck, new_people_records)
            people_added += len(new_people_records)
            if len(seen_people) % int(logcfg["print_every_n_people"]) == 0:
                print(f"👤 People so far: {len(seen_people)} (+{people_added} new this run)")

        if len(seen_people) >= total_people_limit:
            print("🛑 Hit max_total_people cap. Stopping.")
            break

        # REPO SEARCH + CONTRIBUTORS (the big lever)
        repo_q = q
        repo_items = search_repos(api_base, repo_q, per_page, int(vol["repo_search_pages_cap"]))
        repo_items = repo_items[: int(vol["repo_search_per_scenario"])]

        new_repo_records = []
        for ritem in repo_items:
            full_name = ritem.get("full_name")  # owner/repo
            if not full_name:
                continue
            if full_name in seen_repos:
                continue
            rr = {
                "full_name": full_name,
                "html_url": ritem.get("html_url"),
                "stars": ritem.get("stargazers_count", 0),
                "scenario": scenario,
                "tier": tier,
                "category": category,
                "source_query": repo_q,
                "added_at_utc": datetime.now(timezone.utc).isoformat(),
            }
            seen_repos[full_name] = rr
            new_repo_records.append(rr)

        if new_repo_records:
            save_jsonl(repos_ck, new_repo_records)
            repos_added += len(new_repo_records)
            if len(seen_repos) % int(logcfg["print_every_n_repos"]) == 0:
                print(f"📦 Repos so far: {len(seen_repos)} (+{repos_added} new this run)")

        if len(seen_repos) >= total_repo_limit:
            print("🛑 Hit max_total_repos cap. Stopping repo discovery.")
            break

        # Contributor enumeration per repo
        for rr in repo_items:
            full_name = rr.get("full_name")
            if not full_name:
                continue

            # contributors pagination cap derived from requested count
            contrib_pages = max(1, int(vol["contributors_per_repo"]) // per_page + 1)
            contributors = repo_contributors(api_base, full_name, per_page, contrib_pages)
            contributors = contributors[: int(vol["contributors_per_repo"])]

            new_people = []
            for c in contributors:
                login = c.get("login")
                if not login:
                    continue
                if login in seen_people:
                    continue
                rec = {
                    "login": login,
                    "html_url": c.get("html_url"),
                    "scenario": scenario,
                    "tier": tier,
                    "category": category,
                    "discovered_via": "github_repo_contributor",
                    "source_query": repo_q,
                    "source_repo": full_name,
                    "discovered_at_utc": datetime.now(timezone.utc).isoformat(),
                }
                seen_people[login] = rec
                new_people.append(rec)

            if new_people:
                save_jsonl(people_ck, new_people)
                people_added += len(new_people)
                if len(seen_people) % int(logcfg["print_every_n_people"]) == 0:
                    print(f"👤 People so far: {len(seen_people)} (+{people_added} new this run)")

            if len(seen_people) >= total_people_limit:
                print("🛑 Hit max_total_people cap during contributors. Stopping.")
                break

        if len(seen_people) >= total_people_limit:
            break

    # Write expanded people_master
    people_df = pd.DataFrame(list(seen_people.values()))
    people_df = people_df.drop_duplicates(subset=[cfg["hygiene"]["dedupe_key"]]).reset_index(drop=True)
    out_csv = run_dir / "people_master.csv"
    out_xlsx = run_dir / "people_master.xlsx"
    people_df.to_csv(out_csv, index=False)
    people_df.to_excel(out_xlsx, index=False)

    # Write repo inventory (useful for audits)
    repos_df = pd.DataFrame(list(seen_repos.values())).drop_duplicates(subset=["full_name"]).reset_index(drop=True)
    repos_df.to_csv(run_dir / "repos_inventory.csv", index=False)

    print("\n✅ VOLUME EXPANSION COMPLETE")
    print(f"Unique people: {len(people_df)}")
    print(f"Unique repos:   {len(repos_df)}")
    print(f"Output: {out_csv}")
    print(f"Folder: {run_dir}")
if __name__ == "__main__":
    main()
PY

chmod +x people_volume_expander_ultra.py

###############################################################################
# run_volume_expansion_ultra.py
###############################################################################
cat <<'PY' > run_volume_expansion_ultra.py
#!/usr/bin/env python3
"""
Run Volume Expansion (Scenario expansion + People expansion)
© 2025 L. David Mendoza
"""
import subprocess, sys

def run(cmd):
    print(f"▶️  {' '.join(cmd)}")
    r = subprocess.run(cmd)
    if r.returncode != 0:
        sys.exit(r.returncode)

def main():
    run(["python3", "scenario_matrix_builder_ultra.py"])
    run(["python3", "people_volume_expander_ultra.py"])
    print("\n✅ Volume expansion run complete.")
    print("Next:")
    print("  python3 people_enrichment.py   (will enrich latest output/people/VOL_* / people_master.csv)")
    print("  python3 frontier_scientist_radar.py (after enrichment)")
if __name__ == "__main__":
    main()
PY

chmod +x run_volume_expansion_ultra.py

echo ""
echo "✅ ULTRA VOLUME EXPANSION AUTOGEN COMPLETE"
echo "Run:"
echo "  python3 run_volume_expansion_ultra.py"
