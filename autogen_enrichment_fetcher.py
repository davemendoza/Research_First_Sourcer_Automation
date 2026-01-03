from contracts.canonical_people_schema import enforce_canonical
#!/usr/bin/env python3
import pandas as pd, requests, os, yaml, time, concurrent.futures, datetime

with open("config.yaml","r") as f:
    cfg=yaml.safe_load(f)

DATA_DIR=cfg["data_dir"]
OUT_DIR=cfg["output_dir"]
os.makedirs(OUT_DIR,exist_ok=True)

SCRAPE=cfg["data_sources"]
SET=cfg["scrape_settings"]
HEADERS={"User-Agent":SET["user_agent"]}

def fetch_github(user):
    try:
        r=requests.get(f"https://api.github.com/users/{user}",headers=HEADERS,timeout=SET["timeout_seconds"])
        if r.status_code==200:
            d=r.json()
            return d.get("html_url"), d.get("public_repos",0)
    except Exception: pass
    return None,0

def fetch_huggingface(user):
    try:
        r=requests.get(f"https://huggingface.co/api/users/{user}",headers=HEADERS,timeout=SET["timeout_seconds"])
        if r.status_code==200:
            d=r.json()
            return f"https://huggingface.co/{user}", len(d.get("models",[]))
    except Exception: pass
    return None,0

def fetch_scholar(name):
    return f"https://scholar.google.com/scholar?q={name.replace(' ','+')}", None

def enrich_person(row):
    name=row.get("full_name","")
    github_user=name.split()[0].lower() if name else None

    gh_url,gh_repos=fetch_github(github_user) if SCRAPE["github"] else (None,0)
    hf_url,hf_models=fetch_huggingface(github_user) if SCRAPE["huggingface"] else (None,0)
    scholar_url,_=fetch_scholar(name) if SCRAPE["scholar"] else (None,None)

    evidence="; ".join([x for x in [gh_url,hf_url,scholar_url] if x])
    row.update({
        "github_url":gh_url,
        "github_repo_count":gh_repos,
        "huggingface_url":hf_url,
        "huggingface_models":hf_models,
        "scholar_url":scholar_url,
        "evidence_urls":evidence
    })
    time.sleep(SET["delay_seconds"])
    return row

files=sorted([f for f in os.listdir(DATA_DIR) if f.endswith(".csv")])
SRC=os.path.join(DATA_DIR,files[-1])
df=pd.read_csv(SRC)
print(f"Enriching: {SRC} ({len(df)} rows)")

results=[]
with concurrent.futures.ThreadPoolExecutor(max_workers=SET["max_threads"]) as ex:
    for row in ex.map(enrich_person, df.to_dict("records")):
        results.append(row)

df_enriched=pd.DataFrame(results)
ts=datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
outfile=os.path.join(OUT_DIR,f"enriched_talent_{ts}.csv")
df_enriched = enforce_canonical(df_enriched)
df_enriched.to_csv(outfile,index=False)
print(f"Enrichment complete -> {outfile}")
