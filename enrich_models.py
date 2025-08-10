#!/usr/bin/env python3
"""
enrich_models.py
Read scraped_models.txt and write scraped_models_meta.csv with likes/downloads/etc.
"""

import argparse
from pathlib import Path
from datetime import datetime
import csv
import os

from huggingface_hub import HfApi, login

VERSION = "enrich_v2_cli"
print(f"ENRICH_VERSION {VERSION}")
print(f"EXECUTING_FILE {__file__}")
print(f"CWD {os.getcwd()}")

def safe_license(info):
    if getattr(info, "cardData", None) and "license" in info.cardData:
        return info.cardData["license"]
    return getattr(info, "license", None)

def enrich(txt_path: Path, csv_path: Path):
    # optional: login if token present (idempotent)
    token = os.environ.get("HUGGINGFACE_HUB_TOKEN")
    if token:
        try:
            login(token=token)
        except Exception:
            pass

    if not txt_path.exists():
        raise FileNotFoundError(f"Input file not found: {txt_path}")

    ids = [ln.strip() for ln in txt_path.read_text(encoding="utf-8").splitlines() if ln.strip()]

    api = HfApi()
    rows = []
    for mid in ids:
        try:
            info = api.model_info(mid)
            rows.append({
                "model_id": mid,
                "likes": info.likes,
                "downloads": info.downloads,
                "license": safe_license(info),
                "created_at": (info.created_at.strftime("%Y-%m-%d")
                               if getattr(info, "created_at", None) else None),
                "last_modified": (info.lastModified.strftime("%Y-%m-%d")
                                  if getattr(info, "lastModified", None) else None),
            })
            print("ok:", mid)
        except Exception as e:
            print("skip:", mid, "->", e)

    if not rows:
        print("No rows to write.")
        return

    csv_path.parent.mkdir(parents=True, exist_ok=True)
    keys = ["model_id", "likes", "downloads", "license", "created_at", "last_modified"]
    with csv_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        writer.writerows(rows)

    print(f"Wrote {len(rows)} rows to {csv_path.resolve()} at {datetime.now():%Y-%m-%d %H:%M:%S}")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--in", dest="in_path", type=Path, default=Path("scraped_models.txt"),
                        help="input text file with model ids (one per line)")
    parser.add_argument("--out", dest="out_path", type=Path, default=Path("scraped_models_meta.csv"),
                        help="output CSV path")
    args = parser.parse_args()
    enrich(args.in_path, args.out_path)

if __name__ == "__main__":
    main()
