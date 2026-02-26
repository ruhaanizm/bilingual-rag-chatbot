# app/retriever.py

import json
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

from pathlib import Path
from pipeline.config import settings
from pipeline.logger import get_logger
from pipeline.utils import set_seed

logger = get_logger("RETRIEVER")
set_seed(settings.RANDOM_SEED)

MODEL_NAME = "intfloat/multilingual-e5-small"
INDEX_FILE = settings.VECTOR_DB / "faiss.index"
META_FILE = settings.VECTOR_DB / "metadata.json"


class Retriever:
    def __init__(self):
        logger.info("Loading embedding model...")
        self.model = SentenceTransformer(MODEL_NAME)

        logger.info("Loading FAISS index...")
        self.index = faiss.read_index(str(INDEX_FILE))

        with open(META_FILE, "r", encoding="utf-8") as f:
            self.metadata = json.load(f)

    def search(self, query, top_k=5):
        q_emb = self.model.encode(
            ["query: " + query],
            normalize_embeddings=True
        )

        scores, idxs = self.index.search(np.array(q_emb), top_k)

        results = []
        for i in idxs[0]:
            if i < len(self.metadata):
                results.append(self.metadata[i])

        return results