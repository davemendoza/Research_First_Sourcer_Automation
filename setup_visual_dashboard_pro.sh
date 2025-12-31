#!/bin/bash
set -e

echo "=============================================================="
echo "📊 Setting up AI Talent Intelligence Visualization Dashboard"
echo "=============================================================="

cat <<'PY' > ai_talent_dashboard_pro.py
#!/usr/bin/env python3
import os, pandas as pd, streamlit as st, plotly.express as px, glob

st.set_page_config(page_title="AI Talent Intelligence Dashboard", layout="wide")

st.title("🧠 AI Talent Intelligence Explorer (PRO)")
st.caption("Interactive Explorer for Ranked AI Talent Profiles")

# --- Locate latest ranked file ---
latest = sorted(glob.glob("output/final_talent_ranked_pro_*.csv"))[-1]
st.info(f"Loaded dataset: `{os.path.basename(latest)}`")

df = pd.read_csv(latest)

# --- Sidebar Filters ---
st.sidebar.header("🔍 Filters")
orgs = sorted(df["organization"].dropna().unique().tolist()) if "organization" in df.columns else []
roles = sorted(df["role_type"].dropna().unique().tolist()) if "role_type" in df.columns else []

selected_org = st.sidebar.multiselect("Organization", orgs)
selected_role = st.sidebar.multiselect("AI Role Type", roles)

if selected_org:
    df = df[df["organization"].isin(selected_org)]
if selected_role:
    df = df[df["role_type"].isin(selected_role)]

# --- Score Tier Filter ---
if "final_signal_score" in df.columns:
    df["score_tier"] = pd.qcut(df["final_signal_score"], q=4, labels=["Tier 4","Tier 3","Tier 2","Tier 1"])
    selected_tiers = st.sidebar.multiselect("Score Tier", sorted(df["score_tier"].unique().tolist()))
    if selected_tiers:
        df = df[df["score_tier"].isin(selected_tiers)]

# --- Main Table View ---
st.subheader("🏅 Ranked Talent Overview")
st.dataframe(df[[
    "rank","full_name","organization","role_type",
    "final_signal_score","influence_math","signal_score","citation_score",
    "github_followers","huggingface_models","semantic_citations","evidence_urls"
]].head(500), use_container_width=True)

# --- Visualization Section ---
st.subheader("📈 Visual Analytics")

col1, col2 = st.columns(2)

with col1:
    if "final_signal_score" in df.columns:
        fig = px.histogram(df, x="final_signal_score", nbins=30,
                           title="Distribution of Final Signal Scores",
                           color="score_tier" if "score_tier" in df.columns else None)
        st.plotly_chart(fig, use_container_width=True)

with col2:
    if "influence_math" in df.columns and "signal_score" in df.columns:
        fig2 = px.scatter(df, x="influence_math", y="signal_score",
                          color="score_tier" if "score_tier" in df.columns else None,
                          hover_data=["full_name","organization"],
                          title="Influence vs Signal Score Correlation")
        st.plotly_chart(fig2, use_container_width=True)

st.subheader("🏢 Top Organizations by Avg. Score")
if "organization" in df.columns:
    org_mean = (df.groupby("organization")["final_signal_score"]
                .mean().reset_index().sort_values("final_signal_score", ascending=False).head(15))
    fig3 = px.bar(org_mean, x="organization", y="final_signal_score",
                  title="Top Organizations by Average Composite Score")
    st.plotly_chart(fig3, use_container_width=True)

st.success(f"✅ Dashboard Loaded: {len(df)} candidates visualized.")
PY

chmod +x ai_talent_dashboard_pro.py

echo "=============================================================="
echo "✅ Visualization Dashboard Installed!"
echo "To launch, run:"
echo ""
echo "   streamlit run ai_talent_dashboard_pro.py"
echo ""
echo "=============================================================="
