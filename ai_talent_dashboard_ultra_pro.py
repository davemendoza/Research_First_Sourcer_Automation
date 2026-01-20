#!/usr/bin/env python3
"""
AI Talent Intelligence Explorer ULTRA PRO MAX
Complete dashboard with:
- Smart normalization
- Auto-refresh
- Drill-down profiles
- Multi-dataset comparison
"""
import os, glob, time, pandas as pd, numpy as np, streamlit as st, plotly.express as px

st.set_page_config(page_title="AI Talent Intelligence Explorer (ULTRA PRO)", layout="wide")
st.title("🧠 AI Talent Intelligence Explorer (ULTRA PRO)")
st.caption("Autonomous, multi-dataset, full-profile visualization suite for ranked AI talent.")

DATA_DIR = "output"
REFRESH_INTERVAL = 60

def normalize_columns(df):
    rename_map = {"Full Name": "full_name", "Name": "full_name",
                  "Organization": "organization", "Company": "organization",
                  "Job Title": "role_type", "Role": "role_type"}
    df.rename(columns={k: v for k, v in rename_map.items() if k in df.columns}, inplace=True)
    df.columns = [c.lower().replace(" ", "_") for c in df.columns]
    if "full_name" not in df.columns:
        df["full_name"] = df.index.map(lambda i: f"Candidate_{i+1}")
    return df

def get_latest_files():
    files = sorted(glob.glob(f"{DATA_DIR}/*.csv"), key=os.path.getmtime)
    return [f for f in files if "ranked" in f or "enriched" in f]

files = get_latest_files()
if not files:
    st.error("❌ No ranked or enriched datasets found in /output."); st.stop()
file_map = {os.path.basename(f): f for f in files}
selected = st.sidebar.selectbox("📂 Dataset", list(file_map.keys()), index=len(file_map)-1)
df = normalize_columns(pd.read_csv(file_map[selected]))
st.info(f"Loaded: {selected} | Updated: {time.ctime(os.path.getmtime(file_map[selected]))}")

if "final_signal_score" in df.columns:
    df["score_tier"] = pd.qcut(df["final_signal_score"], 4,
                               labels=["Tier 4 (Low)","Tier 3","Tier 2","Tier 1 (Top)"])

st.sidebar.header("🔍 Filters")
if "organization" in df.columns:
    orgs = sorted(df["organization"].dropna().unique().tolist())
    s_org = st.sidebar.multiselect("Organization", orgs)
    if s_org: df = df[df["organization"].isin(s_org)]
if "role_type" in df.columns:
    roles = sorted(df["role_type"].dropna().unique().tolist())
    s_role = st.sidebar.multiselect("Role Type", roles)
    if s_role: df = df[df["role_type"].isin(s_role)]

# Drill-down
st.subheader("🧑‍💼 Drill-Down Profile")
sel = st.selectbox("Select Candidate", sorted(df["full_name"].unique().tolist()))
person = df[df["full_name"] == sel].iloc[0]
st.markdown(f"""
### 👤 {person.get('full_name')}
**Org:** {person.get('organization','N/A')}  
**Role:** {person.get('role_type','N/A')}  
**Score:** {person.get('final_signal_score','N/A')}
""")
links = [k for k in df.columns if 'url' in k]
urls = [f"[{l}]({person[l]})" for l in links if person.get(l)]
if urls: st.markdown("**Links:** " + " | ".join(urls))

# Visuals
st.subheader("📊 Visual Analytics")
col1, col2 = st.columns(2)
with col1:
    if "final_signal_score" in df.columns:
        fig = px.histogram(df, x="final_signal_score", nbins=25, color="score_tier",
                           title="Distribution of Composite Scores")
        st.plotly_chart(fig, use_container_width=True)
with col2:
    if "influence_math" in df.columns and "signal_score" in df.columns:
        fig2 = px.scatter(df, x="influence_math", y="signal_score", color="score_tier",
                          hover_data=["full_name","organization"], title="Influence vs Signal")
        st.plotly_chart(fig2, use_container_width=True)

if "organization" in df.columns:
    org_mean = df.groupby("organization")["final_signal_score"].mean().sort_values(ascending=False).head(15)
    fig3 = px.bar(org_mean, x=org_mean.index, y=org_mean.values, title="Top Orgs by Avg Score")
    st.plotly_chart(fig3, use_container_width=True)

st.success(f"✅ Dashboard Ready | {len(df)} Candidates Visualized.")
