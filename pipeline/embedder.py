# pipeline/embedder.py

import json
import numpy as np
import faiss
from pathlib import Path
from sentence_transformers import SentenceTransformer

from config import settings
from logger import get_logger
from utils import set_seed

logger = get_logger("EMBEDDER")
set_seed(settings.RANDOM_SEED)

MODEL_NAME = "intfloat/multilingual-e5-small"

INDEX_FILE = settings.VECTOR_DB / "faiss.index"
META_FILE = settings.VECTOR_DB / "metadata.json"


def load_chunks():
    files = list(settings.CHUNKS_DIR.glob("*.json"))
    texts = []
    metadata = []

    for f in files:
        with open(f, "r", encoding="utf-8") as jf:
            data = json.load(jf)
            texts.append(data["text"])
            metadata.append(data)

    return texts, metadata


def embed_texts(model, texts, batch_size=32):
    embeddings = []

    for i in range(0, len(texts), batch_size):
        batch = texts[i : i + batch_size]
        batch = ["passage: " + t for t in batch]  # E5 format
        emb = model.encode(batch, normalize_embeddings=True)
        embeddings.append(emb)

    return np.vstack(embeddings)


def build_index(embeddings):
    dim = embeddings.shape[1]
    index = faiss.IndexFlatIP(dim)  # cosine similarity
    index.add(embeddings)
    return index


def run():
    settings.VECTOR_DB.mkdir(exist_ok=True)

    logger.info("Loading multilingual embedding model...")
    model = SentenceTransformer(MODEL_NAME)

    texts, metadata = load_chunks()
    logger.info(f"Total chunks: {len(texts)}")

    embeddings = embed_texts(model, texts)
    logger.info("Embeddings created.")

    index = build_index(embeddings)
    faiss.write_index(index, str(INDEX_FILE))
    logger.info("FAISS index saved.")

    with open(META_FILE, "w", encoding="utf-8") as f:
        json.dump(metadata, f, ensure_ascii=False)

    logger.info("Metadata saved.")