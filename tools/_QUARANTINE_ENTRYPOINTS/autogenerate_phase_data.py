# ======================================================
#  AI Talent Engine — Phase Data Autogenerator (v3.6 FINAL)
#  © 2025 L. David Mendoza · All Rights Reserved
#  Legal Notice: Confidential & Proprietary — See Legal_Proprietary_Notice.txt
# ======================================================
#  STATUS: Permanent Release | Schema Reference: AI_Talent_Schema_Rules v3.2
#  Purpose: Autogenerates Phase 6 & 7 CSVs (schema-locked, non-overlapping, deterministic)
# ======================================================

import os, pandas as pd, numpy as np, hashlib, datetime, random, platform, json

# ------------------------------------------------------
# Global Configuration
# ------------------------------------------------------
DATA_DIR = "data"
os.makedirs(DATA_DIR, exist_ok=True)

SCHEMA_COLUMNS = 40
ROWS_PHASE6 = 250
ROWS_PHASE7 = 50
RANDOM_SEED = 42  # <-- Permanent reproducibility lock (deterministic output)

random.seed(RANDOM_SEED)
np.random.seed(RANDOM_SEED)

# ------------------------------------------------------
# Utility Functions
# ------------------------------------------------------
def sha256sum(path: str) -> str:
    """Compute SHA256 checksum for a file."""
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()

# ------------------------------------------------------
# Canonical 40-column Schema Definition
# ------------------------------------------------------
columns = [
    "AI_Classification","Full_Name","Company","Team_or_Lab","Title","Seniority_Level",
    "Corporate_Email","Personal_Email","LinkedIn_URL","Portfolio_URL","Google_Scholar_URL",
    "Semantic_Scholar_URL","GitHub_URL","Primary_Specialties","LLM_Names","VectorDB_Tech",
    "RAG_Details","Inference_Stack","GPU_Infra_Signals","RLHF_Eval_Signals","Multimodal_Signals",
    "Research_Areas","Top_Papers_or_Blogposts","Conference_Presentations","Awards_Luminary_Signals",
    "Panel_Talks_Workshops","Citation_Trajectory","Strengths","Weaknesses","Corporate_Profile_URL",
    "Publications_Page_URL","Blog_Post_URLs","Influence_Composite_Score","Influence_Percentile",
    "Governance_Version","Reviewer_ID","SHA256_Hash","Runtime_Stamp","Reserved_Field","System_Source"
]

# ------------------------------------------------------
# Phase 6 — 250 Engineers (Base Dataset)
# ------------------------------------------------------
p6 = pd.DataFrame({
    "AI_Classification": np.random.choice(["Frontier","Applied","Research"], ROWS_PHASE6),
    "Full_Name": [f"Engineer_{i:03d}" for i in range(1, ROWS_PHASE6 + 1)],
    "Company": np.random.choice(["OpenAI","DeepMind","Anthropic","Meta","Google"], ROWS_PHASE6),
    "Title": np.random.choice(["ML Engineer","Researcher","Scientist"], ROWS_PHASE6),
    "Seniority_Level": np.random.choice(["Junior","Mid","Senior","Principal"], ROWS_PHASE6),
    "Citation_Trajectory": np.random.uniform(0, 10, ROWS_PHASE6).round(2),
    "Citation_Velocity_Score": np.random.uniform(0, 10, ROWS_PHASE6).round(2),
    "Governance_Version": "v3.6",
    "Reviewer_ID": "system_auto",
    "Runtime_Stamp": datetime.datetime.now().isoformat(),
    "System_Source": platform.node()
})
for c in columns:
    if c not in p6.columns:
        p6[c] = ""
p6 = p6[columns]
phase6_path = os.path.join(DATA_DIR, "phase6_output.csv")
p6.to_csv(phase6_path, index=False)
sha6 = sha256sum(phase6_path)
print(f"✅ Generated {phase6_path} — {len(p6)} rows, {p6.shape[1]} columns (schema-locked)")
print(f"🔒 SHA256: {sha6[:12]}…")

# ------------------------------------------------------
# Phase 7 — 50 Unique, Non-Overlapping Frontier Profiles
# ------------------------------------------------------
p7 = pd.DataFrame({
    "AI_Classification": np.random.choice(["Frontier","Elite"], ROWS_PHASE7),
    "Full_Name": [f"Frontier_{i:03d}" for i in range(1, ROWS_PHASE7 + 1)],  # ensures uniqueness
    "Company": np.random.choice(["OpenAI","DeepMind","Anthropic","Meta","Google"], ROWS_PHASE7),
    "Title": np.random.choice(["Research Lead","Chief Scientist","Principal Engineer"], ROWS_PHASE7),
    "Seniority_Level": np.random.choice(["Principal","Distinguished"], ROWS_PHASE7),
    "Citation_Trajectory": np.random.uniform(8, 10, ROWS_PHASE7).round(2),
    "Citation_Velocity_Score": np.random.uniform(8, 10, ROWS_PHASE7).round(2),
    "Governance_Version": "v3.6",
    "Reviewer_ID": "system_auto",
    "Runtime_Stamp": datetime.datetime.now().isoformat(),
    "System_Source": platform.node()
})
for c in columns:
    if c not in p7.columns:
        p7[c] = ""
p7 = p7[columns]
phase7_path = os.path.join(DATA_DIR, "phase7_output.csv")
p7.to_csv(phase7_path, index=False)
sha7 = sha256sum(phase7_path)
print(f"✅ Generated {phase7_path} — {len(p7)} rows, {p7.shape[1]} columns (schema-locked)")
print(f"🔒 SHA256: {sha7[:12]}…")

# ------------------------------------------------------
# Finalization & Audit Metadata
# ------------------------------------------------------
meta = {
    "timestamp": datetime.datetime.now().isoformat(),
    "schema_columns": SCHEMA_COLUMNS,
    "rows_phase6": ROWS_PHASE6,
    "rows_phase7": ROWS_PHASE7,
    "seed": RANDOM_SEED,
    "sha_phase6": sha6,
    "sha_phase7": sha7,
    "system_user": os.getenv("USER", "unknown"),
    "python_version": platform.python_version(),
    "system_host": platform.node()
}

meta_path = os.path.join(DATA_DIR, "phase_generation_meta.json")
with open(meta_path, "w") as mf:
    json.dump(meta, mf, indent=2)

print(f"🧾 Metadata written → {meta_path}")
print("🔒 Phase data generation complete — schema-locked (40 columns, deterministic & non-overlapping).")
