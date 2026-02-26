# pipeline/scraper.py

import certifi
import json
import time
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from pathlib import Path

from config import settings
from logger import get_logger
from utils import content_hash, set_seed

logger = get_logger("SCRAPER")
set_seed(settings.RANDOM_SEED)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    "Accept-Language": "en-US,en;q=0.9,hi;q=0.8",
}

VISITED = set()
PDF_LINKS = set()


def same_domain(base, url):
    return urlparse(base).netloc == urlparse(url).netloc


def fetch(url):
    try:
        r = requests.get(url, headers=HEADERS, timeout=15, verify=certifi.where())
        if r.status_code == 200:
            return r.text
    except Exception as e:
        logger.warning(f"Failed: {url} — {e}")
    return None


def extract_text(html):
    soup = BeautifulSoup(html, "lxml")

    # remove scripts/styles
    for tag in soup(["script", "style", "noscript"]):
        tag.extract()

    text = soup.get_text(separator="\n")
    text = " ".join(text.split())
    return text


def save_json(url, text):
    if len(text) < settings.MIN_TEXT_LENGTH:
        return

    h = content_hash(text)
    out_file = settings.RAW_DIR / f"{h}.json"
    if out_file.exists():
        return

    data = {
        "url": url,
        "text": text,
        "hash": h,
    }

    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def collect_links(base_url, html):
    soup = BeautifulSoup(html, "lxml")

    for a in soup.find_all("a", href=True):
        link = urljoin(base_url, a["href"]).split("#")[0]

        if link.lower().endswith(".pdf"):
            PDF_LINKS.add(link)
            continue

        if same_domain(base_url, link):
            if link not in VISITED:
                VISITED.add(link)
                yield link


def crawl(start_url, max_pages=100):
    queue = [start_url]
    VISITED.add(start_url)

    while queue and len(VISITED) <= max_pages:
        url = queue.pop(0)
        logger.info(f"Crawling: {url}")

        html = fetch(url)
        if not html:
            continue

        text = extract_text(html)
        save_json(url, text)

        for link in collect_links(start_url, html):
            queue.append(link)

        time.sleep(1)  # polite crawling

    # Save PDF links
    pdf_file = settings.RAW_DIR / "pdf_links.json"
    with open(pdf_file, "w", encoding="utf-8") as f:
        json.dump(list(PDF_LINKS), f, indent=2)

    logger.info(f"Saved {len(PDF_LINKS)} PDF links.")