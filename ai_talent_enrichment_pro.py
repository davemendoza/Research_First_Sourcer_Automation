#!/usr/bin/env python3
import os, yaml, pandas as pd, requests, time, concurrent.futures, datetime, numpy as np
from sklearn.preprocessing import MinMaxScaler

# ---------- Load Config ----------
with open("config.yaml", "r") as f:
    cfg = yaml.safe_load(f)

DATA_DIR = cfg["data_dir"]
OUT_DIR = cfg["output_dir"]
SCRAPE = cfg["data_sources"]
SET = cfg["scrape_settings"]
AUTH = cfg.get("auth", {})
HEADERS = {"User-Agent": SET["user_agent"]}

# ---------- Token Management ----------
if AUTH.get("github_token") or os.getenv("GITHUB_TOKEN"):
    HEADERS["Authorization"] = f"token {AUTH.get('github_token') or os.getenv('GITHUB_TOKEN')}"
HF_TOKEN = AUTH.get("huggingface_token") or os.getenv("HF_TOKEN")
SEMANTIC_TOKEN = AUTH.get("semantic_token") or os.getenv("SEMANTIC_TOKEN")

os.makedirs(OUT_DIR, exist_ok=True)
print("🚀 AI Talent Engine PRO – Enrichment + Weighted Ranking")

# ---------- Fetchers ----------
def fetch_github(user):
    try:
        url = f"https://api.github.com/users/{user}"
        r = requests.get(url, headers=HEADERS, timeout=SET["timeout_seconds"])
        if r.status_code == 200:
            d = r.json()
            return {
                "github_url": d.get("html_url"),
                "github_followers": d.get("followers",0),
                "github_repos": d.get("public_repos",0),
                "github_bio": d.get("bio","")
            }
    except Exception as e:
        print(f"⚠️ GitHub fetch error for {user}: {e}")
    return {}

def fetch_huggingface(user):
    try:
        url = f"https://huggingface.co/api/users/{user}"
        headers = HEADERS.copy()
        if HF_TOKEN:
            headers["Authorization"] = f"Bearer {HF_TOKEN}"
        r = requests.get(url, headers=headers, timeout=SET["timeout_seconds"])
        if r.status_code == 200:
            d = r.json()
            return {
                "huggingface_url": f"https://huggingface.co/{user}",
                "huggingface_models": len(d.get("models",[])),
                "huggingface_likes": d.get("likes",0)
            }
    except Exception as e:
        print(f"⚠️ HF fetch error for {user}: {e}")
    return {}

def fetch_scholar(name):
    return {"scholar_url": f"https://scholar.google.com/scholar?q={name.replace(' ','+')}"}

def fetch_semantic(name):
    try:
        url = f"https://api.semanticscholar.org/graph/v1/author/search?query={name}&limit=1&fields=name,paperCount,citationCount,url"
        headers = {"User-Agent": SET["user_agent"]}
        if SEMANTIC_TOKEN:
            headers["x-api-key"] = SEMANTIC_TOKEN
        r = requests.get(url, headers=headers, timeout=SET["timeout_seconds"])
        if r.status_code == 200:
            j = r.json()
            if j.get("data"):
                a = j["data"][0]
                return {
                    "semantic_url": a.get("url"),
                    "semantic_papers": a.get("paperCount",0),
                    "semantic_citations": a.get("citationCount",0)
                }
    except Exception as e:
        print(f"⚠️ Semantic Scholar error: {e}")
    return {}

# ---------- Enrichment Worker ----------
def enrich_row(row):
    name = row.get("full_name","")
    user = name.split()[0].lower() if name else None
    result = {}

    if SCRAPE["github"] and user:
        result.update(fetch_github(user))
    if SCRAPE["huggingface"] and user:
        result.update(fetch_huggingface(user))
    if SCRAPE["scholar"] and name:
        result.update(fetch_scholar(name))
    if SCRAPE["semantic"] and name:
        result.update(fetch_semantic(name))

    row.update(result)
    row["evidence_urls"] = "; ".join([v for v in result.values() if isinstance(v,str) and v.startswith("http")])
    time.sleep(SET["delay_seconds"])
    return row

# ---------- Load & Enrich ----------
files = sorted([f for f in os.listdir(DATA_DIR) if f.endswith(".csv")])
if not files:
    raise FileNotFoundError(f"No CSV found in {DATA_DIR}")
SRC = os.path.join(DATA_DIR, files[-1])
df = pd.read_csv(SRC)
print(f"📂 Enriching dataset: {SRC} ({len(df)} rows)")

results=[]
with concurrent.futures.ThreadPoolExecutor(max_workers=SET["max_threads"]) as ex:
    for row in ex.map(enrich_row, df.to_dict("records")):
        results.append(row)

df_enriched = pd.DataFrame(results)

# ---------- Compute Citation Score ----------
if "semantic_citations" in df_enriched.columns:
    df_enriched["citation_score"] = np.log1p(df_enriched["semantic_citations"].fillna(0))
else:
    df_enriched["citation_score"] = 0

# ---------- Weighted Scoring ----------
weights = cfg["scoring_weights"]
for col in weights.keys():
    if col not in df_enriched.columns:
        df_enriched[col] = 0
scaler = MinMaxScaler()
scaled = scaler.fit_transform(df_enriched[list(weights.keys())])
df_scaled = pd.DataFrame(scaled, columns=list(weights.keys()))
df_enriched["final_signal_score"] = np.sum([df_scaled[c]*w for c,w in weights.items()], axis=0)

df_enriched = df_enriched.sort_values("final_signal_score", ascending=False).reset_index(drop=True)
df_enriched.insert(0,"rank",np.arange(1,len(df_enriched)+1))

# ---------- Export ----------
ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
outfile = os.path.join(OUT_DIR, f"final_talent_ranked_pro_{ts}.csv")
df_enriched.to_csv(outfile, index=False)

print(f"✅ Enrichment + Ranking complete → {outfile}")
print(f"🔗 Added GitHub, HuggingFace, Scholar & Semantic fields")
print(f"🧠 Ranked {len(df_enriched)} candidates")
