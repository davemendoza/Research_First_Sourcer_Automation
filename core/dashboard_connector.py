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
# © 2025 L. David Mendoza – All Rights Reserved
