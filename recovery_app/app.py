import time
from pathlib import Path
import pandas as pd
import streamlit as st
from PIL import Image

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data"
META = DATA / "metadata.parquet"

st.set_page_config(page_title="Recovery Stories", layout="wide")
st.title("Recovery Stories Dataset")

col1, col2 = st.columns([1,1])
with col1:
    refresh_sec = st.number_input("Auto refresh seconds", min_value=0, max_value=3600, value=30, step=5)
with col2:
    if st.button("Refresh now"):
        st.cache_data.clear()

@st.cache_data(ttl=45)
def load_meta():
    if META.exists():
        return pd.read_parquet(META)
    return pd.DataFrame(columns=["id","created_at","source","author_alias","text","image_path","tags","consent_flag","notes"])

df = load_meta()
st.success(f"Loaded {len(df)} rows from {META.name}")

st.dataframe(df, use_container_width=True)

if refresh_sec:
    time.sleep(int(refresh_sec))
    st.cache_data.clear()
    st.rerun()

