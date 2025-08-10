import streamlit as st
from huggingface_hub import HfApi

hf_token = st.secrets["HF_TOKEN"]
st.write("HF_TOKEN loaded:", hf_token)

api = HfApi(token=hf_token)
me = api.whoami()
st.write(f"Logged in as: {me['name']}")
