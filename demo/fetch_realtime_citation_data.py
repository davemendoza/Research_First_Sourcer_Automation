from contracts.canonical_people_schema import enforce_canonical
# ======================================================
#  AI Talent Engine — Real-Time Citation Data Fetcher v2.0 (Final, Best-in-Class)
#  © 2025 L. David Mendoza · All Rights Reserved
#  Legal Notice: Confidential & Proprietary — See Legal_Proprietary_Notice.txt
# ======================================================
#  PURPOSE:
#    Fetches true citation velocity and growth metrics from live scholarly APIs
#    (Semantic Scholar + OpenAlex) and integrates into the AI Talent Engine schema.
# ======================================================

import os, requests, pandas as pd, time, json, hashlib, datetime, platform, sys

# ------------------------------------------------------
# Configuration & Governance
# ------------------------------------------------------
CACHE_DIR = "data/cache"
LOG_DIR = "logs"
OUT_CSV = "data/realtime_citation_metrics.csv"
OUT_JSON = "data/realtime_citation_metrics.json"
HASH_LOG = os.path.join(LOG_DIR, "realtime_hashes.log")
os.makedirs(CACHE_DIR, exist_ok=True)
os.makedirs(LOG_DIR, exist_ok=True)

HEADERS = {"User-Agent": "AI-Talent-Engine/2.0 (contact: research@aitalentengine.org)"}
SEMANTIC_SCHOLAR_URL = "https://api.semanticscholar.org/graph/v1/author/search"
OPENALEX_URL = "https://api.openalex.org/authors"

# ------------------------------------------------------
# Utility Functions
# ------------------------------------------------------
def sha256sum(data):
    if isinstance(data, (dict, list)):
        data = json.dumps(data, sort_keys=True).encode()
    elif isinstance(data, str) and os.path.exists(data):
        with open(data, "rb") as f:
            return hashlib.sha256(f.read()).hexdigest()
    return hashlib.sha256(data if isinstance(data, bytes) else str(data).encode()).hexdigest()

def safe_get(url, params):
    for attempt in range(4):
        try:
            r = requests.get(url, params=params, headers=HEADERS, timeout=10)
            if r.status_code == 200:
                return r.json()
            elif r.status_code == 429:
                print("⏳ Rate limit — sleeping briefly")
                time.sleep(2)
        except Exception as e:
            print(f"⚠️ {url} fetch error: {e}")
            time.sleep(1)
    return None

# ------------------------------------------------------
# API Retrieval Logic
# ------------------------------------------------------
def get_semantic_scholar_data(name):
    data = safe_get(SEMANTIC_SCHOLAR_URL, {"query": name, "limit": 1})
    if not data or "data" not in data or not data["data"]:
        return None
    author_id = data["data"][0]["authorId"]
    return safe_get(
        f"https://api.semanticscholar.org/graph/v1/author/{author_id}",
        {"fields": "citationCount,citationsPerYear,influentialCitationCount,coAuthors"},
    )

def get_openalex_data(name):
    data = safe_get(OPENALEX_URL, {"search": name, "per-page": 1})
    if not data or "results" not in data or not data["results"]:
        return None
    return data["results"][0]

# ------------------------------------------------------
# Metric Computation (Real-Time, Deterministic)
# ------------------------------------------------------
def compute_metrics(name):
    cache_path = os.path.join(CACHE_DIR, f"{hashlib.md5(name.encode()).hexdigest()}.json")
    if os.path.exists(cache_path):
        return json.load(open(cache_path))

    scholar, alex = get_semantic_scholar_data(name), get_openalex_data(name)
    m = dict(
        Full_Name=name,
        Citation_Velocity_Score=0,
        Citation_Growth_Rate=0,
        Influence_Rank_Change=0,
        CoAuthor_Influence_Velocity=0,
        Source_SemanticScholar=bool(scholar),
        Source_OpenAlex=bool(alex),
        Retrieved=datetime.datetime.now().isoformat()
    )

    try:
        # --- Semantic Scholar-based metrics ---
        if scholar and "citationsPerYear" in scholar:
            years, vals = list(scholar["citationsPerYear"].keys()), list(scholar["citationsPerYear"].values())
            if len(years) >= 2:
                last2, total = sum(vals[-2:]), sum(vals)
                m["Citation_Velocity_Score"] = round(last2 / total * 10, 3) if total else 0
                m["Citation_Growth_Rate"] = round((vals[-1] - vals[-2]) / max(vals[-2], 1), 3)

        # --- OpenAlex-based rank dynamics ---
        if alex and "counts_by_year" in alex:
            yrs = sorted(alex["counts_by_year"], key=lambda x: x["year"])
            if len(yrs) >= 2:
                new, old = yrs[-1]["works_count"], yrs[-2]["works_count"]
                m["Influence_Rank_Change"] = round((new - old) / max(old, 1), 3)

        # --- Co-Author Network Velocity ---
        if scholar and "coAuthors" in scholar:
            m["CoAuthor_Influence_Velocity"] = round(
                (scholar.get("influentialCitationCount", 0)) /
                max(len(scholar.get("coAuthors", [])) or 1, 1), 3)
    except Exception as e:
        print(f"⚠️ Error processing {name}: {e}")

    json.dump(m, open(cache_path, "w"), indent=2)
    return m

# ------------------------------------------------------
# Data Builder & Logging
# ------------------------------------------------------
def build_realtime_dataframe(names, quiet=False):
    rows = []
    for n in names:
        r = compute_metrics(n)
        rows.append(r)
        if not quiet:
            print(f"✅ {n}: V={r['Citation_Velocity_Score']}, G={r['Citation_Growth_Rate']}, "
                  f"R={r['Influence_Rank_Change']}, C={r['CoAuthor_Influence_Velocity']}")
        time.sleep(0.25)
    df = pd.DataFrame(rows)
df = enforce_canonical(df)
    df.to_csv(OUT_CSV, index=False)
    json.dump(rows, open(OUT_JSON, "w"), indent=2)
    sha = sha256sum(OUT_CSV)
    with open(HASH_LOG, "a") as log:
        log.write(f"{datetime.datetime.now()} | {OUT_CSV} | SHA256:{sha}\n")
    print(f"📦 Saved → {OUT_CSV} ({len(df)} rows) | SHA256 {sha[:12]}…")
    return df

# ------------------------------------------------------
# CLI Runner
# ------------------------------------------------------
def main():
    start = datetime.datetime.now()
    print("🧠 AI Talent Engine — Real-Time Citation Data Fetcher (Final v2.0)")
    input_csv = "data/phase6_output.csv"
    if not os.path.exists(input_csv):
        print("❌ phase6_output.csv not found — run autogenerate_phase_data.py first.")
        sys.exit(1)
    names = pd.read_csv(input_csv)["Full_Name"].dropna().unique().tolist()
    df = build_realtime_dataframe(names)
    print(f"\n✅ Completed realtime data collection for {len(df)} names.")
    print(f"Runtime: {datetime.datetime.now() - start}")

if __name__ == "__main__":
    main()
