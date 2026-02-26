# pipeline/pdf_extractor.py

import json
import pdfplumber
import pytesseract
from pdf2image import convert_from_path
from pathlib import Path

from config import settings
from logger import get_logger
from utils import content_hash, set_seed

logger = get_logger("PDF_EXTRACTOR")
set_seed(settings.RANDOM_SEED)

# CHANGE if needed
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
POPPLER_PATH = r"C:\poppler\Library\bin"


def extract_text_pdf(pdf_path):
    text = ""

    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                t = page.extract_text()
                if t:
                    text += t + "\n"
    except Exception:
        pass

    return text.strip()


def ocr_pdf(pdf_path):
    text = ""

    try:
        images = convert_from_path(pdf_path, dpi=300, poppler_path=POPPLER_PATH)

        for img in images:
            t = pytesseract.image_to_string(img, lang="eng+hin")
            if t:
                text += t + "\n"

    except Exception as e:
        logger.warning(f"OCR failed: {pdf_path} — {e}")

    return text.strip()


def process_pdf(pdf_path):
    logger.info(f"Processing: {pdf_path.name}")

    text = extract_text_pdf(pdf_path)

    # If text too small → OCR fallback
    if len(text) < settings.MIN_TEXT_LENGTH:
        logger.info("Low text → Running OCR...")
        text = ocr_pdf(pdf_path)

    if len(text) < settings.MIN_TEXT_LENGTH:
        logger.warning("Skipped (too little text)")
        return

    h = content_hash(text)
    out_file = settings.CLEAN_DIR / f"{h}.json"

    if out_file.exists():
        return

    data = {
        "source": str(pdf_path.name),
        "text": text,
        "hash": h,
    }

    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def run():
    pdfs = list(settings.PDF_DIR.glob("*.pdf"))

    logger.info(f"Total PDFs: {len(pdfs)}")

    for pdf in pdfs:
        process_pdf(pdf)