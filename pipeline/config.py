# pipeline/config.py

import os
from pathlib import Path
from dotenv import load_dotenv
from pydantic import BaseModel

load_dotenv()


class Settings(BaseModel):
    PROJECT_NAME: str = os.getenv("PROJECT_NAME", "bilingual-rag")
    DATA_DIR: Path = Path(os.getenv("DATA_DIR", "data"))
    VECTOR_DB: Path = Path(os.getenv("VECTOR_DB", "vectordb"))

    RAW_DIR: Path = DATA_DIR / "raw"
    CLEAN_DIR: Path = DATA_DIR / "clean"
    CHUNKS_DIR: Path = DATA_DIR / "chunks"
    PDF_DIR: Path = DATA_DIR / "pdfs"

    MIN_TEXT_LENGTH: int = 300
    CHUNK_SIZE: int = 500
    CHUNK_OVERLAP: int = 50

    RANDOM_SEED: int = 42


settings = Settings()