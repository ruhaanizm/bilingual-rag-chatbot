# Bilingual RAG Chatbot (English + Hindi)

Lightweight, CPU-friendly, deterministic Retrieval-Augmented Generation chatbot.

## Features

- English + Hindi support
- HTML scraping
- PDF extraction + OCR
- Clean UTF-8 corpus
- Token-aware chunking
- Multilingual embeddings (E5-small)
- FAISS vector search
- Grounded CLI chatbot (no hallucination)

## Setup

```bash
python -m venv venv
venv\Scripts\activate   # Windows
pip install -r requirements.txt