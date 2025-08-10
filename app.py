# app.py – cloud friendly (reads CSV_URL if set, else calls HF API)
import os, time
import pandas as pd
import streamlit as st
from datetime import datetime
from huggingface_hub import HfApi, login

IDS = [
    "deepseek-ai/DeepSeek-R1",
    "black-forest-labs/FLUX.1-dev",
    "CompVis/stable-diffusion-v1-4",
    "stabilityai/stable-diffusion-xl-base-1.0",
    "meta-llama/Meta-Llama-3-8B",
]

st.set_page_config(page_title="HF Featured Models", layout="wide")
st.title("Hugging Face models")

if st.button("Refresh now"):
    st.cache_data.clear()
    st.rerun()

refresh_sec = st.sidebar.slider("Auto refresh (sec)", 15, 300, 60, 15)

@st.cache_data(ttl=60)
def fetch_df():
    csv_url = os.getenv("CSV_URL", "").strip()
    token = st.secrets.get("HUGGINGFACE_HUB_TOKEN") if hasattr(st, "secrets") else None
    if csv_url:
        return pd.read_csv(csv_url)
    if token:
        try: login(token)  # idempotent
        except Exception: pass
    api = HfApi()
    rows = []
    for mid in IDS:
        info = api.model_info(mid)
        lic = info.cardData.get("license") if getattr(info, "cardData", None) else getattr(info, "license", None)
        created = info.created_at.strftime("%Y-%m-%d") if getattr(info, "created_at", None) else None
        rows.append({"model_id": mid, "likes": info.likes, "downloads": info.downloads, "license": lic, "created_at": created})
    return pd.DataFrame(rows)

df = fetch_df()
st.caption(f"Loaded at {datetime.now():%Y-%m-%d %H:%M:%S}")
st.dataframe(df, use_container_width=True)

c1, c2 = st.columns(2)
with c1: st.bar_chart(df.set_index("model_id")[["likes"]])
with c2: st.bar_chart(df.set_index("model_id")[["downloads"]])

time.sleep(refresh_sec)
st.rerun()
# app.py – cloud friendly (reads CSV_URL if set, else calls HF API)
# app.py – cloud friendly (reads CSV_URL if set, else calls HF API)
# app.py – cloud friendly (reads CSV_URL if set, else calls HF API)
# app.py – cloud friendly (reads CSV_URL if set, else calls HF API)