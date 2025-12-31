#!/usr/bin/env python3
import os, yaml, pandas as pd, requests, time, concurrent.futures, datetime

# --- Load Config ---
with open("config.yaml", "r") as f:
    cfg = yaml.safe_load(f)

DATA_DIR = cfg["data_dir"]
OUT_DIR = cfg["output_dir"]
SCRAPE = cfg["data_sources"]
SET = cfg["scrape_settings"]
AUTH = cfg.get("auth", {})
HEADERS = {"User-Agent": SET["user_agent"]}

# --- Token setup ---
if AUTH.get("github_token") or os.getenv("GITHUB_TOKEN"):
    HEADERS["Authorization"] = f"token {AUTH.get('github_token') or os.getenv('GITHUB_TOKEN')}"
if AUTH.get("huggingface_token") or os.getenv("HF_TOKEN"):
    HF_TOKEN = AUTH.get("huggingface_token") or os.getenv("HF_TOKEN")
else:
    HF_TOKEN = None

os.makedirs(OUT_DIR, exist_ok=True)

print("🔐 Running AI Talent Engine PRO Enrichment (Authenticated APIs)")

# --- GitHub Fetcher ---
def fetch_github(user):
    try:
        url = f"https://api.github.com/users/{user}"
        r = requests.get(url, headers=HEADERS, timeout=SET["timeout_seconds"])
        if r.status_code == 200:
            d = r.json()
            return {
                "github_url": d.get("html_url"),
                "github_followers": d.get("followers"),
                "github_repos": d.get("public_repos"),
                "github_bio": d.get("bio")
            }
    except Exception as e:
        print(f"⚠️ GitHub error for {user}: {e}")
    return {}

# --- Hugging Face Fetcher ---
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
                "huggingface_models": len(d.get("models", [])),
                "huggingface_likes": d.get("likes", 0)
            }
    except Exception as e:
        print(f"⚠️ HuggingFace error for {user}: {e}")
    return {}

# --- Google Scholar Stub ---
def fetch_scholar(name):
    return {"scholar_url": f"https://scholar.google.com/scholar?q={name.replace(' ', '+')}"}

# --- Enrichment Routine ---
def enrich_row(row):
    name = row.get("full_name", "")
    user = name.split()[0].lower() if name else None
    result = {}

    if SCRAPE["github"] and user:
        result.update(fetch_github(user))
    if SCRAPE["huggingface"] and user:
        result.update(fetch_huggingface(user))
    if SCRAPE["scholar"] and name:
        result.update(fetch_scholar(name))

    row.update(result)
    row["evidence_urls"] = "; ".join([v for k, v in result.items() if isinstance(v, str) and v.startswith("http")])
    time.sleep(SET["delay_seconds"])
    return row

# --- Run Enrichment ---
files = sorted([f for f in os.listdir(DATA_DIR) if f.endswith(".csv")])
if not files:
    raise FileNotFoundError(f"No CSV files found in {DATA_DIR}")

SRC = os.path.join(DATA_DIR, files[-1])
df = pd.read_csv(SRC)
print(f"📂 Enriching {SRC} ({len(df)} rows)...")

results = []
with concurrent.futures.ThreadPoolExecutor(max_workers=SET["max_threads"]) as ex:
    for row in ex.map(enrich_row, df.to_dict("records")):
        results.append(row)

df_enriched = pd.DataFrame(results)
ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
outfile = os.path.join(OUT_DIR, f"enriched_talent_pro_{ts}.csv")
df_enriched.to_csv(outfile, index=False)

print(f"✅ PRO Enrichment complete → {outfile}")
print("🔗 Added: github_followers, github_bio, huggingface_models, scholar_url, evidence_urls")
