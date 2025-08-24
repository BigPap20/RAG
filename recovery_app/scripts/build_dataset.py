import argparse, time, uuid
from pathlib import Path
import pandas as pd
import requests
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
IMAGES = DATA / "images"
META = DATA / "metadata.parquet"
URLS = DATA / "urls.csv"

IMAGES.mkdir(parents=True, exist_ok=True)

def now():
    return pd.Timestamp.utcnow()

def normalize(row: dict) -> dict:
    d = {}
    d["id"] = row.get("id") or str(uuid.uuid4())
    d["created_at"] = pd.to_datetime(row.get("created_at") or now())
    d["source"] = row.get("source") or "web"
    d["author_alias"] = row.get("author_alias") or "anonymous"
    d["text"] = str(row.get("text") or "").strip()
    d["tags"] = row.get("tags") or ""
    d["consent_flag"] = bool(row.get("consent_flag")) if "consent_flag" in row else False
    d["notes"] = row.get("notes") or ""
    d["image_path"] = row.get("image_path") or ""
    return d

def save_image_bytes(b: bytes, rec_id: str, content_type: str) -> str:
    suffix = ".jpg"
    if "png" in (content_type or "").lower():
        suffix = ".png"
    out = IMAGES / f"{rec_id}{suffix}"
    out.write_bytes(b)
    try:
        Image.open(out).verify()
    except Exception:
        out.unlink(missing_ok=True)
        return ""
    return str(out.relative_to(DATA))

def fetch_image(url: str, rec_id: str) -> str:
    try:
        r = requests.get(url, timeout=20)
        r.raise_for_status()
        return save_image_bytes(r.content, rec_id, r.headers.get("content-type",""))
    except Exception as e:
        print(f"[warn] image fetch failed for {url}: {e}")
        return ""

def import_urls() -> pd.DataFrame:
    if not URLS.exists():
        print(f"[info] no urls.csv at {URLS}")
        return pd.DataFrame()
    df = pd.read_csv(URLS, comment="#")
    rows = []
    for _, r in df.iterrows():
        rec = normalize(r.to_dict())
        img_url = r.get("image_url")
        if img_url:
            rec["image_path"] = fetch_image(img_url, rec["id"])
        rows.append(rec)
    return pd.DataFrame(rows)

def load_db() -> pd.DataFrame:
    if META.exists():
        return pd.read_parquet(META)
    return pd.DataFrame(columns=["id","created_at","source","author_alias","text","image_path","tags","consent_flag","notes"])

def sweep() -> int:
    db = load_db()
    from_urls = import_urls()
    if not from_urls.empty:
        db = pd.concat([db, from_urls], ignore_index=True)
    if db.empty:
        return 0
    db.drop_duplicates(subset=["id"], keep="last", inplace=True)
    db.sort_values("created_at", ascending=False, inplace=True)
    db.to_parquet(META, index=False)
    return len(db)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--once", action="store_true")
    args = parser.parse_args()

    if args.once:
        n = sweep()
        print(f"[done] wrote {n} rows to {META}")
    else:
        print(f"[watching] {DATA}")
        while True:
            n = sweep()
            print(f"[tick] rows={n} file={META.name}")
            time.sleep(10)

