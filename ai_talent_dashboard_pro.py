#!/usr/bin/env python3
"""
AI Talent Intelligence Explorer (PRO++) — with Smart Normalization
------------------------------------------------------------------
✅ Auto-normalizes key columns (e.g., full_name)
✅ Auto-refresh and profile drill-down
✅ Future-ready for multi-dataset comparison
"""

import os, glob, time, pandas as pd, streamlit as st, plotly.express as px

st.set_page_config(page_title="AI Talent Intelligence Explorer (PRO++)", layout="wide")
st.title("🧠 AI Talent Intelligence Explorer (PRO++)")
st.caption("Smart-normalized, auto-refresh drill-down dashboard for ranked AI profiles")

# ---------- Locate latest valid dataset ----------
def get_latest_file():
    files = sorted(
        glob.glob("output/*ranked*.csv") + glob.glob("output/*enriched*.csv"),
        key=os.path.getmtime
    )
    return files[-1] if files else None

latest = get_latest_file()
if not latest:
    st.error("❌ No ranked or enriched datasets found in /output.")
    st.stop()

last_update = os.path.getmtime(latest)
st.info(f"📄 Loaded dataset: **{os.path.basename(latest)}** | Last Updated: {time.ctime(last_update)}")

df = pd.read_csv(latest)

# ---------- Smart normalization ----------
rename_map = {
    "Full Name": "full_name",
    "Name": "full_name",
    "Person": "full_name",
    "Candidate": "full_name",
    "Organization": "organization",
    "Company": "organization",
    "Employer": "organization",
    "Job Title": "role_type",
    "Role": "role_type",
    "AI Role": "role_type"
}
df.rename(columns={k: v for k, v in rename_map.items() if k in df.columns}, inplace=True)

if "full_name" not in df.columns:
    st.warning("⚠️ No explicit name column found. Generating synthetic IDs...")
    df["full_name"] = df.index.map(lambda i: f"Candidate_{i+1}")

# ---------- Sidebar Filters ----------
st.sidebar.header("🔍 Filters")

orgs = sorted(df["organization"].dropna().unique().tolist()) if "organization" in df.columns else []
roles = sorted(df["role_type"].dropna().unique().tolist()) if "role_type" in df.columns else []

selected_orgs = st.sidebar.multiselect("Organization", orgs)
selected_roles = st.sidebar.multiselect("AI Role Type", roles)

if selected_orgs:
    df = df[df["organization"].isin(selected_orgs)]
if selected_roles:
    df = df[df["role_type"].isin(selected_roles)]

# ---------- Score Tier Filter ----------
if "final_signal_score" in df.columns:
    df["score_tier"] = pd.qcut(df["final_signal_score"],
                               q=4, labels=["Tier 4 (Low)","Tier 3","Tier 2","Tier 1 (Top)"])
    tiers = st.sidebar.multiselect("Score Tier", sorted(df["score_tier"].unique().tolist()))
    if tiers:
        df = df[df["score_tier"].isin(tiers)]

# ---------- Drill-Down Profile Viewer ----------
st.subheader("🧑‍💼 Drill-Down Profile Panel")

selected_person = st.selectbox("Select Candidate", sorted(df["full_name"].dropna().unique().tolist()))
person = df[df["full_name"] == selected_person].iloc[0]

st.markdown(f"""
### 👤 {person.get('full_name','Unknown')}
**Organization:** {person.get('organization','N/A')}  
**Role:** {person.get('role_type','N/A')}  
**Composite Score:** {person.get('final_signal_score','N/A')}  
**Influence Math:** {person.get('influence_math','N/A')}  
**Signal Score:** {person.get('signal_score','N/A')}  
**Email:** {person.get('email','N/A')} | **Phone:** {person.get('phone','N/A')}
""")

links = []
for key in ["github_url","huggingface_url","linkedin_url","semantic_scholar_url","resume_link"]:
    if key in df.columns and pd.notna(person.get(key)):
        links.append(f"[{key.replace('_url','').title()}]({person[key]})")
if links:
    st.markdown("**Profiles:** " + " | ".join(links))
if "evidence_urls" in df.columns:
    st.markdown(f"**Evidence:** {person['evidence_urls']}")

# ---------- Main Data Table ----------
st.subheader("🏅 Ranked Talent Overview")
cols = [c for c in [
    "rank","full_name","organization","role_type",
    "final_signal_score","influence_math","signal_score","citation_score",
    "github_followers","huggingface_models","semantic_citations","evidence_urls"
] if c in df.columns]
st.dataframe(df[cols].head(300), use_container_width=True)

# ---------- Visual Analytics ----------
st.subheader("📊 Visual Analytics")
col1, col2 = st.columns(2)

with col1:
    if "final_signal_score" in df.columns:
        fig = px.histogram(df, x="final_signal_score", nbins=30,
                           color="score_tier" if "score_tier" in df.columns else None,
                           title="Distribution of Final Signal Scores")
        st.plotly_chart(fig, use_container_width=True)

with col2:
    if "influence_math" in df.columns and "signal_score" in df.columns:
        fig2 = px.scatter(df, x="influence_math", y="signal_score",
                          color="score_tier" if "score_tier" in df.columns else None,
                          hover_data=["full_name","organization"],
                          title="Influence vs Signal Correlation")
        st.plotly_chart(fig2, use_container_width=True)

# ---------- Top Organizations ----------
st.subheader("🏢 Top Organizations by Avg Score")
if "organization" in df.columns and "final_signal_score" in df.columns:
    org_mean = (df.groupby("organization")["final_signal_score"]
                .mean().reset_index()
                .sort_values("final_signal_score", ascending=False).head(15))
    fig3 = px.bar(org_mean, x="organization", y="final_signal_score",
                  title="Top Organizations by Average Composite Score")
    st.plotly_chart(fig3, use_container_width=True)

st.success(f"✅ Dashboard Ready | {len(df)} candidates visualized.")
