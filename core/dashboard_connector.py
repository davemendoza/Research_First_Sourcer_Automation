# Added auto-refresh and conference mode toggle
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
