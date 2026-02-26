# pipeline/chunker.py

import json
from pathlib import Path
import tiktoken

from config import settings
from logger import get_logger
from utils import content_hash, set_seed

logger = get_logger("CHUNKER")
set_seed(settings.RANDOM_SEED)

# Lightweight tokenizer
enc = tiktoken.get_encoding("cl100k_base")


def tokenize_len(text: str) -> int:
    return len(enc.encode(text))


def split_chunks(text: str, chunk_size: int, overlap: int):
    tokens = enc.encode(text)

    chunks = []
    start = 0

    while start < len(tokens):
        end = start + chunk_size
        chunk_tokens = tokens[start:end]
        chunk_text = enc.decode(chunk_tokens)
        chunks.append(chunk_text)
        start += chunk_size - overlap

    return chunks


def process_file(file_path: Path):
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    text = data["text"]
    source = data.get("source", "unknown")

    if tokenize_len(text) < settings.CHUNK_SIZE:
        chunks = [text]
    else:
        chunks = split_chunks(
            text,
            settings.CHUNK_SIZE,
            settings.CHUNK_OVERLAP,
        )

    for chunk in chunks:
        if len(chunk.strip()) < 50:
            continue

        h = content_hash(chunk)
        out_file = settings.CHUNKS_DIR / f"{h}.json"

        if out_file.exists():
            continue

        chunk_data = {
            "text": chunk,
            "source": source,
            "hash": h,
        }

        with open(out_file, "w", encoding="utf-8") as f:
            json.dump(chunk_data, f, ensure_ascii=False, indent=2)


def run():
    files = list(settings.CLEAN_DIR.glob("*.json"))
    logger.info(f"Clean documents: {len(files)}")

    for f in files:
        process_file(f)

    logger.info("Chunking completed.")