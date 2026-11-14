import streamlit as st
from utils.helpers import df_csv


def show_df(df, download_name=None, key=None, height=None):
    kw = {"height": height} if height else {}
    st.dataframe(df, width="stretch", hide_index=True, **kw)
    if download_name and len(df):
        st.download_button("⬇️ Download CSV", df_csv(df), file_name=download_name, mime="text/csv", key=key or f"dl_{download_name}")
