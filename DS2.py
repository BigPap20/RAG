import os
import time
from pathlib import Path

import requests
from bs4 import BeautifulSoup

DELAY = 2           # seconds, matches robots.txt
HOME = "https://huggingface.co/"
UA = "Mozilla/5.0 (compatible; HF-learning-bot/0.1)"

def scrape_huggingface():
    try:
        headers = {"User-Agent": UA}
        with requests.Session() as sess:
            resp = sess.get(HOME, headers=headers, timeout=15)
            resp.raise_for_status()

        soup = BeautifulSoup(resp.text, "html.parser")

        # simple example: grab titles of featured models
        titles = [tag.text.strip() for tag in soup.select("h3")]
        if titles:
            print("First five featured model titles:")
            for title in titles[:5]:
                print("  ", title)
        else:
            print("No titles found")

    except requests.RequestException as err:
        print(f"HTTP error: {err}")
    except Exception as err:
        print(f"Unexpected error: {err}")
    finally:
        time.sleep(DELAY)

if __name__ == "__main__":
    scrape_huggingface()
