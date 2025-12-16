# ======================================================
#  AI Talent Engine — Audit Validator v1.0
#  © 2025 L. David Mendoza · All Rights Reserved
#  Legal Notice: Confidential & Proprietary — See Legal_Proprietary_Notice.txt
# ======================================================

import os, glob, pandas as pd, hashlib, datetime, json

DATA_DIR="data"
LOG_DIR="logs"
ASSETS_DIR="demo_assets"
expected_cols=40
report_path=os.path.join(ASSETS_DIR,f"audit_report_{datetime.datetime.now():%Y%m%d_%H%M}.json")

def sha256sum(path:str)->str:
    h=hashlib.sha256()
    with open(path,"rb") as f:
        for chunk in iter(lambda:f.read(8192),b""):
            h.update(chunk)
    return h.hexdigest()

def audit_csv(path:str):
    df=pd.read_csv(path)
    result={
        "file":path,
        "rows":len(df),
        "columns":df.shape[1],
        "schema_ok":df.shape[1]==expected_cols,
        "sha256":sha256sum(path)
    }
    if "Citation_Trajectory" in df.columns:
        numeric_ok=pd.to_numeric(df["Citation_Trajectory"],errors="coerce").between(0,10).all()
    else:
        numeric_ok=True
    result["numeric_ok"]=numeric_ok
    result["pass"]=result["schema_ok"] and numeric_ok
    return result

def audit_logs():
    hashes=[]
    for log in glob.glob(os.path.join(LOG_DIR,"hash_*.log")):
        with open(log) as f:
            hashes.extend(line.strip() for line in f if "SHA256" in line)
    return hashes

def main():
    print(f"[{datetime.datetime.now()}] Running AI Talent Engine Audit Validator…")
    results=[audit_csv(p) for p in glob.glob(os.path.join(DATA_DIR,"*_demo.csv"))]
    log_hashes=audit_logs()
    passed=[r for r in results if r["pass"]]
    failed=[r for r in results if not r["pass"]]
    summary={
        "timestamp":datetime.datetime.now().isoformat(),
        "total_files":len(results),
        "passed":len(passed),
        "failed":len(failed),
        "results":results,
        "log_hash_lines":len(log_hashes)
    }
    os.makedirs(ASSETS_DIR,exist_ok=True)
    with open(report_path,"w") as f:json.dump(summary,f,indent=2)
    print(f"✅ Audit completed — {len(passed)} passed / {len(failed)} failed")
    print(f"📄 JSON report → {report_path}")

if __name__=="__main__":
    main()
