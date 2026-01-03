from contracts.canonical_people_schema import enforce_canonical
# © 2025 Dave Mendoza, DBA AI Craft, Inc. All rights reserved. Strictly proprietary; no copying, derivative works, reverse engineering, redistribution, or commercial/personal use permitted without written authorization. Governed by Colorado, USA law.
import streamlit as st
import pandas as pd

from phase5.engine.loader import load_data
from phase5.engine.pdf_reports import generate_pdf_bytes, generate_pdf_filename
from phase5.engine.analytics import role_distribution, tier_distribution, average_scores_by_role
from phase5.engine.utils import safe_text


def main():
    st.set_page_config(page_title="AI Talent Engine – Phase 5", layout="wide")

    st.title("AI Talent Engine – Phase 5 Dashboard")
    st.caption("Browse, filter, and generate reports for ranked AI talent leads.")

    df = load_data()

    st.sidebar.header("Filters")

    roles = ["All"] + sorted(df["primary_role"].dropna().unique().tolist())
    tiers = ["All"] + sorted(df["tier"].dropna().unique().tolist())

    sel_role = st.sidebar.selectbox("Primary role", roles)
    sel_tier = st.sidebar.selectbox("Tier", tiers)

    min_score = float(df["signal_strength"].min())
    max_score = float(df["signal_strength"].max())
    score_range = st.sidebar.slider(
        "Score range",
        min_value=min_score,
        max_value=max_score,
        value=(min_score, max_score),
    )

    search_text = st.sidebar.text_input("Search (name, description, strengths)")

    filtered = df.copy()

    if sel_role != "All":
        filtered = filtered[filtered["primary_role"] == sel_role]

    if sel_tier != "All":
        filtered = filtered[filtered["tier"] == sel_tier]

    filtered = filtered[
        (filtered["signal_strength"] >= score_range[0])
        & (filtered["signal_strength"] <= score_range[1])
    ]

    if search_text:
        q = search_text.lower()
        mask = (
            filtered["name"].fillna("").str.lower().str.contains(q)
            | filtered["description"].fillna("").str.lower().str.contains(q)
            | filtered["Strengths"].fillna("").str.lower().str.contains(q)
        )
        filtered = filtered[mask]

    st.subheader("Ranked talent")

    cols_to_show = [
        "rank", "name", "primary_role", "secondary_role",
        "tier", "signal_strength", "Recommendation"
    ]
    st.dataframe(
        filtered[cols_to_show].reset_index(drop=True),
        use_container_width=True,
        hide_index=True,
    )

    st.download_button(
        "Download filtered as CSV",
filtered = enforce_canonical(filtered)
        data=filtered.to_csv(index=False).encode("utf-8"),
        file_name="phase5_filtered_talent.csv",
        mime="text/csv",
    )

    st.markdown("---")

    st.subheader("Analytics")

    col_a, col_b, col_c = st.columns(3)

    with col_a:
        st.markdown("**Role distribution**")
        rd = role_distribution(df)
        st.bar_chart(rd)

    with col_b:
        st.markdown("**Tier distribution**")
        td = tier_distribution(df)
        st.bar_chart(td)

    with col_c:
        st.markdown("**Average score by role**")
        ar = average_scores_by_role(df)
        st.bar_chart(ar)

    st.markdown("---")

    st.subheader("Candidate details")

    if not filtered.empty:
        names = filtered["name"].fillna("Unnamed").tolist()
        selected_name = st.selectbox("Select candidate", names)
        row = filtered[filtered["name"] == selected_name].iloc[0]

        c1, c2 = st.columns(2)

        with c1:
            st.markdown(f"**Name:** {safe_text(row['name'])}")
            st.markdown(f"**Primary role:** {safe_text(row['primary_role'])}")
            st.markdown(f"**Secondary role:** {safe_text(row['secondary_role'])}")
            st.markdown(f"**Tier:** {safe_text(row['tier'])}")
            st.markdown(f"**Score:** {safe_text(row['signal_strength'])}")
            st.markdown(
                f"**Recommendation:** {safe_text(row['Recommendation'])} "
                f"({safe_text(row['Recommendation_Confidence'])}%)"
            )

        with c2:
            st.markdown("**Summary / Description**")
            st.write(safe_text(row.get("description", "")))

        st.markdown("### Strengths")
        st.write(safe_text(row.get("Strengths", "")))

        st.markdown("### Weaknesses / Gaps")
        st.write(safe_text(row.get("Weaknesses", "")))

        pdf_bytes = generate_pdf_bytes(row)
        pdf_name = generate_pdf_filename(row)
        st.download_button(
            "Download candidate PDF report",
            data=pdf_bytes,
            file_name=pdf_name,
            mime="application/pdf",
        )
    else:
        st.info("No candidates match the current filters.")


if __name__ == "__main__":
    main()

def run_pipeline(input_data):
    return {"results": ["ok"], "timestamp": "now"}



def run_pipeline(input_data):
    print("🚀 Phase5 pipeline executing with input:", input_data)
    return {"results": ["ok"], "timestamp": "now"}

Proprietary Rights Notice
------------------------
All code, scripts, GitHub repositories, documentation, data, and GPT-integrated components of the AI Talent Engine – Signal Intelligence and Research_First_Sourcer_Automation Python Automation Sourcing Framework are strictly proprietary. All intellectual property rights, copyrights, trademarks, and related rights are exclusively owned by Dave Mendoza, DBA AI Craft, Inc.
No individual or entity may copy, reproduce, distribute, modify, create derivative works, reverse engineer, decompile, or otherwise use any part of this system, software, or associated materials for personal or commercial purposes without explicit written authorization from Dave Mendoza.
All rights reserved. Unauthorized use may result in legal action.
This statement is governed by the laws of the State of Colorado, USA.
