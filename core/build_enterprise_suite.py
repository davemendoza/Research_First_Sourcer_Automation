#!/usr/bin/env python3
# ===========================================================
#  AI Talent Engine — Enterprise Build Suite
#  © 2025  L. David Mendoza  –  All Rights Reserved
# ===========================================================
import os, subprocess, datetime, json, hashlib, platform

ROOT = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(ROOT, ".."))
LOGS = os.path.join(BASE, "logs")
os.makedirs(LOGS, exist_ok=True)
LOG_FILE = os.path.join(LOGS, f"enterprise_build_{datetime.datetime.now():%Y%m%d_%H%M%S}.log")

def log(msg):
    stamp = datetime.datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
    print(msg)
    with open(LOG_FILE, "a") as f:
        f.write(f"{stamp} {msg}\n")

def build_system_health():
    p = os.path.join(BASE, "core/system_health.py")
    code = """#!/usr/bin/env python3
import os, subprocess, platform, datetime, json
LOG_FILE = 'logs/system_health.log'
def check(cmd):
    try:
        subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return True
    except Exception:
        return False
report = {'timestamp': datetime.datetime.now().isoformat(),
          'python': platform.python_version(),
          'streamlit': check(['python3','-m','streamlit','--version']),
          'ssh': check(['ssh','-T','git@github.com']),
          'audio': check(['pgrep','-x','coreaudiod'])}
with open(LOG_FILE,'w') as f: json.dump(report,f,indent=2)
print('✅ System health diagnostics complete →',LOG_FILE)
"""
    open(p,"w").write(code)
    os.chmod(p,0o755)
    log("✓ system_health.py written")

def build_version_manifest():
    p = os.path.join(BASE, "core/version_manifest.py")
    code = """#!/usr/bin/env python3
import json, datetime, subprocess, os
LOG_FILE='logs/version_manifest.json'
git_hash = subprocess.getoutput('git rev-parse HEAD') or 'unknown'
manifest={'build_version':'1.0.0',
          'schema':'AI_Talent_Schema_Rules v3.2',
          'timestamp':datetime.datetime.now().isoformat(),
          'commit':git_hash}
os.makedirs('logs',exist_ok=True)
json.dump(manifest,open(LOG_FILE,'w'),indent=2)
print('✅ Version manifest written →',LOG_FILE)
"""
    open(p,"w").write(code)
    os.chmod(p,0o755)
    log("✓ version_manifest.py written")

def build_unit_tests():
    folder = os.path.join(BASE, "core/tests")
    os.makedirs(folder, exist_ok=True)
    open(os.path.join(folder,"test_sanity.py"),"w").write(
        "import unittest, os\nclass Sanity(unittest.TestCase):\n"
        "    def test_repo_exists(self):\n"
        "        self.assertTrue(os.path.exists('core'))\n"
        "if __name__ == '__main__':\n    unittest.main()\n")
    log("✓ core/tests/test_sanity.py created")

def build_integrity_verifier():
    p = os.path.join(BASE, "core/integrity_verifier.py")
    code = """#!/usr/bin/env python3
import os, hashlib, json, datetime
LOG='logs/provenance_manifest.json'
def hash_file(p):
    h=hashlib.sha256()
    with open(p,'rb') as f:
        for c in iter(lambda: f.read(8192),b''): h.update(c)
    return h.hexdigest()
manifest={'timestamp':datetime.datetime.now().isoformat(),'files':{}}
for root,_,files in os.walk('.'):
    for f in files:
        if f.endswith('.py'):
            full=os.path.join(root,f)
            manifest['files'][full]=hash_file(full)
json.dump(manifest,open(LOG,'w'),indent=2)
print('✅ Integrity verification complete →',LOG)
"""
    open(p,"w").write(code)
    os.chmod(p,0o755)
    log("✓ integrity_verifier.py upgraded")

def build_dashboard_upgrade():
    p = os.path.join(BASE, "core/dashboard_connector.py")
    code = """# Added auto-refresh and conference mode toggle
import streamlit as st, os, time, glob, pandas as pd
st.set_page_config(page_title='AI Talent Engine', layout='wide')
st.title('AI Talent Engine — Signal Intelligence Dashboard')
st.sidebar.header('Options')
refresh = st.sidebar.checkbox('Auto-refresh every 10 s', value=True)
conference = st.sidebar.checkbox('Conference Narration Mode', value=False)
csvs = glob.glob('output/*.csv')
if not csvs:
    st.info('No CSV outputs found. Run an agent to populate data.')
else:
    for c in csvs:
        st.subheader(os.path.basename(c))
        st.dataframe(pd.read_csv(c))
if refresh: time.sleep(10); st.experimental_rerun()
"""
    open(p,"w").write(code)
    log("✓ dashboard_connector.py upgraded")

def build_research_graph():
    p = os.path.join(BASE, "core/research_graph_builder.py")
    open(p,"w").write(
        "import networkx as nx, matplotlib.pyplot as plt, json\n"
        "G=nx.Graph(); G.add_edge('Researcher A','Researcher B')\n"
        "nx.draw(G,with_labels=True); plt.savefig('output/research_graph.png')\n"
        "print('✅ research_graph_builder completed → output/research_graph.png')\n")
    log("✓ research_graph_builder.py written")

def build_talent_signal_analyzer():
    p = os.path.join(BASE, "core/talent_signal_analyzer.py")
    open(p,"w").write(
        "import pandas as pd, glob, os\nout='output/ai_talent_master_dataset.csv'\n"
        "frames=[pd.read_csv(f) for f in glob.glob('output/*.csv') if f.endswith('.csv')]\n"
        "if frames: pd.concat(frames).to_csv(out,index=False); print('✅ Master dataset written →',out)\n"
        "else: print('⚠️ No CSVs found for aggregation.')\n")
    log("✓ talent_signal_analyzer.py written")

for fn in [build_system_health, build_version_manifest, build_unit_tests,
           build_integrity_verifier, build_dashboard_upgrade,
           build_research_graph, build_talent_signal_analyzer]:
    try: fn()
    except Exception as e: log(f"⚠️ {fn.__name__} failed: {e}")

try:
    subprocess.run(["git","add","."],check=True)
    subprocess.run(["git","commit","-m","Enterprise Suite Build"],check=True)
    subprocess.run(["git","push"],check=True)
    log("✅ Git push successful.")
except Exception as e:
    log(f"⚠️ Git push failed: {e}")

log("🏁 Enterprise build complete.")
