#!/usr/bin/env python3
"""
featured_meta.py
Save basic stats for five popular Hugging Face models and log progress.
"""

from datetime import datetime
from huggingface_hub import HfApi
import pandas as pd


def grab_featured_stats() -> pd.DataFrame:
    api = HfApi()
    ids = [
        "deepseek-ai/DeepSeek-R1",
        "black-forest-labs/FLUX.1-dev",
        "CompVis/stable-diffusion-v1-4",
        "stabilityai/stable-diffusion-xl-base-1.0",
        "meta-llama/Meta-Llama-3-8B",
    ]

    rows = []
    for mid in ids:
        info = api.model_info(mid)

        # license can be in cardData["license"] or sometimes as info.license
        lic = None
        if getattr(info, "cardData", None) and "license" in info.cardData:
            lic = info.cardData["license"]
        elif hasattr(info, "license"):
            lic = info.license

        created = getattr(info, "created_at", None)
        if created is not None:
            created = created.strftime("%Y-%m-%d")

        rows.append(
            {
                "model_id": mid,
                "likes": info.likes,
                "downloads": info.downloads,
                "license": lic,
                "created_at": created,
            }
        )

    return pd.DataFrame(rows)


def main() -> None:
    # start marker for logs
    print(f"[{datetime.now().isoformat(timespec='seconds')}] start")

    df = grab_featured_stats()
    print(df)
    df.to_csv("featured_models.csv", index=False)

    # end marker for logs
    print("wrote featured_models.csv")


if __name__ == "__main__":
    main()


