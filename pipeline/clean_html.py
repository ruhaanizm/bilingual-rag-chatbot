# pipeline/clean_html.py

import json
import re
from pathlib import Path

from config import settings
from logger import get_logger
from utils import content_hash, set_seed

logger = get_logger("CLEAN_HTML")
set_seed(settings.RANDOM_SEED)


def normalize_text(text: str) -> str:
    # Unicode-safe whitespace normalization (Hindi preserved)
    text = text.replace("\xa0", " ")
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def process_file(file_path: Path):
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    text = normalize_text(data.get("text", ""))

    if len(text) < settings.MIN_TEXT_LENGTH:
        return

    h = content_hash(text)
    out_file = settings.CLEAN_DIR / f"{h}.json"

    if out_file.exists():
        return

    clean_data = {
        "source": data.get("url", "html_page"),
        "text": text,
        "hash": h,
    }

    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(clean_data, f, ensure_ascii=False, indent=2)


def run():
    raw_files = list(settings.RAW_DIR.glob("*.json"))

    logger.info(f"Raw HTML files: {len(raw_files)}")

    for f in raw_files:
        if f.name == "pdf_links.json":
            continue
        process_file(f)

    logger.info("HTML cleaning completed.")