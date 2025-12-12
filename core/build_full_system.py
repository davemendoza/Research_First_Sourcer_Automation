#!/usr/bin/env python3
# ===========================================================
#  AI Talent Engine — Full System Autogeneration (Streamlit Edition)
#  © 2025 L. David Mendoza – All Rights Reserved
# ===========================================================
import os, subprocess, datetime, hashlib, json, textwrap

ROOT = os.getcwd()
LOG_DIR = os.path.join(ROOT, "logs")
os.makedirs(LOG_DIR, exist_ok=True)
LOG_FILE = os.path.join(LOG_DIR, f"build_full_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.log")

def log(msg):
    print(msg)
    with open(LOG_FILE, "a") as f: f.write(msg + "\n")

def write_file(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        f.write(content.strip() + "\n# © 2025 L. David Mendoza – All Rights Reserved\n")

# --- demo_logger.py ---
write_file("core/demo_logger.py", '''
import datetime, os
LOG_FILE="logs/demo_activity.log"
def log_run(agent,status="✅ Success",duration=None):
    os.makedirs("logs",exist_ok=True)
    t=datetime.datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
    d=f" | Duration: {duration}" if duration else ""
    msg=f"{t} Agent: {agent} | Status: {status}{d}"
    print(msg)
    with open(LOG_FILE,"a") as f: f.write(msg+"\\n")
''')

# --- integrity_verifier.py ---
write_file("core/integrity_verifier.py", '''
import os,hashlib,json,datetime
def sha256(file):
    h=hashlib.sha256()
    with open(file,"rb") as f:
        for c in iter(lambda: f.read(4096),b""): h.update(c)
    return h.hexdigest()
def verify():
    os.makedirs("logs",exist_ok=True)
    data={}
    for root,_,files in os.walk("."):
        for f in files:
            if f.endswith((".py",".csv",".yaml",".md")):
                p=os.path.join(root,f)
                data[p]=sha256(p)
    with open("logs/provenance_manifest.json","w") as out: json.dump(data,out,indent=2)
    s=datetime.datetime.now().isoformat()
    with open("logs/integrity_audit.log","a") as l: l.write(f"[{s}] Integrity manifest updated ({len(data)} files)\\n")
    print(f"✅ Integrity verification complete: {len(data)} files hashed.")
if __name__=="__main__": verify()
''')

# --- dashboard_connector.py (Streamlit) ---
write_file("core/dashboard_connector.py", '''
import streamlit as st, pandas as pd, glob
st.set_page_config(page_title="AI Talent Engine Dashboard", layout="wide")
st.title("🧠 AI Talent Engine – Signal Intelligence Dashboard")
files=glob.glob("output/*.csv")
if not files: st.warning("No output CSVs found.")
else:
    df=pd.concat([pd.read_csv(f) for f in files],ignore_index=True)
    st.dataframe(df)
    if "Name" in df.columns and "Citations" in df.columns:
        st.subheader("Top Researchers by Citations")
        st.bar_chart(df.sort_values("Citations",ascending=False).head(10),x="Name",y="Citations")
st.sidebar.header("Navigation")
st.sidebar.write("Use demo_trigger.py to run agents.")
st.markdown("---")
st.caption("© 2025 L. David Mendoza – All Rights Reserved")
''')

# --- auto Git push ---
def git_push():
    try:
        subprocess.run(["git","add","."],check=True)
        subprocess.run(["git","commit","-m","Automated Full System Build"],check=True)
        subprocess.run(["git","push","-u","origin","main"],check=True)
        log("✅ Git push successful.")
    except Exception as e: log(f"⚠️ Git push failed: {e}")

log("🚀 Building AI Talent Engine system...")
subprocess.run(["python3","core/integrity_verifier.py"])
git_push()
log("🏁 Full system build complete.")
