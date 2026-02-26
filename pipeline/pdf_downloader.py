# pipeline/pdf_downloader.py

import json
import time
import requests
import certifi
from pathlib import Path
from urllib.parse import urlparse

from config import settings
from logger import get_logger
from utils import content_hash, set_seed

logger = get_logger("PDF_DOWNLOADER")
set_seed(settings.RANDOM_SEED)

HEADERS = {
    "User-Agent": "Mozilla/5.0",
}


def safe_filename(url):
    name = urlparse(url).path.split("/")[-1]
    if not name.lower().endswith(".pdf"):
        name += ".pdf"
    return name


def download_pdf(url, out_path):
    try:
        r = requests.get(url, headers=HEADERS, timeout=30, verify=certifi.where(), stream=True)
        if r.status_code != 200:
            return False

        with open(out_path, "wb") as f:
            for chunk in r.iter_content(1024 * 32):
                if chunk:
                    f.write(chunk)

        return True

    except Exception as e:
        logger.warning(f"Failed: {url} — {e}")
        return False


def run():
    pdf_links_file = settings.RAW_DIR / "pdf_links.json"
    if not pdf_links_file.exists():
        logger.error("No pdf_links.json found. Run scraper first.")
        return

    with open(pdf_links_file, "r", encoding="utf-8") as f:
        links = json.load(f)

    logger.info(f"Total PDFs found: {len(links)}")

    downloaded = 0
    skipped = 0

    for url in links:
        filename = safe_filename(url)
        out_file = settings.PDF_DIR / filename

        if out_file.exists():
            skipped += 1
            continue

        logger.info(f"Downloading: {filename}")

        ok = download_pdf(url, out_file)
        if ok:
            downloaded += 1
        else:
            if out_file.exists():
                out_file.unlink()

        time.sleep(1)

    logger.info(f"Downloaded: {downloaded}")
    logger.info(f"Skipped existing: {skipped}")