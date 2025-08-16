import os
import time
import requests
import pandas as pd
import streamlit as st

# ---------------------------------------------------------
# Configuration
# ---------------------------------------------------------
DATA_FILE = "scraped_models.txt"   # Local cache file
DEFAULT_IDS = ["gpt2", "bert-base-uncased", "distilbert-base-uncased"]
SCRAPE_INTERVAL = 60  # seconds between refreshes


# ---------------------------------------------------------
# Helpers
# ---------------------------------------------------------
def fetch_df():
    """
    Fetch model data into a Pandas DataFrame.

    Priority:
      1. If 'scraped_models.txt' exists → load IDs from it
      2. Else → fall back to DEFAULT_IDS

    Returns:
        pd.DataFrame: Data containing model_id, likes, downloads
    """
    if os.path.exists(DATA_FILE):
        st.info("✅ Data source: scraped_models.txt")
        with open(DATA_FILE, "r") as f:
            ids = [line.strip() for line in f if line.strip()]
    else:
        st.info("⚠️ No local file found. Using DEFAULT_IDS instead.")
        ids = DEFAULT_IDS

    # Query Hugging Face API
    rows = []
    for mid in ids:
        try:
            r = requests.get(f"https://huggingface.co/api/models/{mid}")
            if r.status_code == 200:
                j = r.json()
                rows.append({
                    "model_id": mid,
                    "likes": j.get("likes", 0),
                    "downloads": j.get("downloads", 0),
                })
            else:
                st.warning(f"⚠️ API returned {r.status_code} for {mid}")
        except Exception as e:
            st.error(f"❌ Error fetching {mid}: {e}")

    return pd.DataFrame(rows)


# ---------------------------------------------------------
# Streamlit App
# ---------------------------------------------------------
def main():
    """Main Streamlit app entry point."""
    st.title("🤗 HF Featured Models")

    # Auto-refresh loop
    while True:
        df = fetch_df()

        if not df.empty:
            # Show table
            st.dataframe(df)

            # Bar charts
            st.bar_chart(df.set_index("model_id")["likes"])
            st.bar_chart(df.set_index("model_id")["downloads"])
        else:
            st.warning("⚠️ No data available.")

        # Sleep before next update
        time.sleep(SCRAPE_INTERVAL)


if __name__ == "__main__":
    main()
