#!/usr/bin/env python3
"""
data_scrap.py

Pull the first five featured Hugging Face model IDs.

Default: use the official Hugging Face Hub client (fast and robust).
Fallback: scrape the landing page only if the client is missing.

Requirements
------------
pip install huggingface_hub requests beautifulsoup4
"""

import time

# switch to the scraper automatically if the Hub client is not available
USE_SCRAPER = False
try:
    from huggingface_hub import HfApi
except ImportError:
    USE_SCRAPER = True

if USE_SCRAPER:
    import requests
    from bs4 import BeautifulSoup

HOME = "https://huggingface.co/"
UA = "Mozilla/5.0 (compatible; HF-learning-bot/0.2)"
DELAY = 2          # seconds for polite scraping
COUNT = 5          # number of model IDs to show


def featured_via_api(n=COUNT):
    """Return the top *n* models sorted by likes using the Hub client."""
    api = HfApi()
    models = api.list_models(sort="likes", direction=-1, limit=n)
    return [m.modelId for m in models]


def featured_via_scraper(n=COUNT):
    """Return the first *n* models found on the landing page."""
    resp = requests.get(HOME, headers={"User-Agent": UA}, timeout=15)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")

    links = soup.select('a[href^="/models/"]')
    ids = []
    for link in links:
        slug = link["href"].lstrip("/")
        # keep slugs shaped like "org/model"
        if slug.count("/") == 1 and not slug.endswith("tree/main"):
            ids.append(slug)

    ids = list(dict.fromkeys(ids))        # preserve order and ensure unique
    return ids[:n]


def main():
    ids = featured_via_scraper() if USE_SCRAPER else featured_via_api()
    print("Featured model IDs:")
    for mid in ids:
        print(" ", mid)

    if USE_SCRAPER:
        time.sleep(DELAY)                 # respect robots.txt


if __name__ == "__main__":
    main()
