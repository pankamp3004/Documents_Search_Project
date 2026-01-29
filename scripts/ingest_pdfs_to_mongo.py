import os
import uuid
from datetime import datetime, timezone
from pymongo import MongoClient
import pdfplumber
from dotenv import load_dotenv

load_dotenv()

# =========================
# Config
# =========================

DATA_DIR = "data/pdfs"
MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = "ai_search"
COLLECTION = "documents"

# =========================
# Mongo Setup
# =========================

client = MongoClient(MONGO_URI)
db = client[DB_NAME]
documents = db[COLLECTION]

# =========================
# PDF Extraction
# =========================

def extract_pdf_text(path: str):
    full_text = []
    num_pages = 0

    with pdfplumber.open(path) as pdf:
        num_pages = len(pdf.pages)
        for i, page in enumerate(pdf.pages):
            text = page.extract_text()
            if text:
                full_text.append(text)

    return "\n".join(full_text), num_pages


# =========================
# Ingest Single PDF
# =========================

def ingest_pdf(path: str):
    print(f" Processing: {path}")

    raw_text, num_pages = extract_pdf_text(path)

    if not raw_text.strip():
        print(f" No text extracted from {path}")
        return

    doc = {
        "doc_id": str(uuid.uuid4()),

        # Metadata
        "title": os.path.basename(path),
        "source": "local",
        "file_name": os.path.basename(path),
        "file_type": "pdf",
        "document_type": "book",

        "author": None,
        "published_year": None,

        # Raw Content
        "raw_text": raw_text,

        # Stats
        "num_pages": num_pages,
        "file_size_kb": os.path.getsize(path) // 1024,

        # Timestamps
        "ingested_at": datetime.now(timezone.utc)
    }

    documents.insert_one(doc)
    print(f"Ingested: {doc['title']} | Pages: {num_pages}")

# =========================
# Ingest All PDFs
# =========================

def ingest_all_pdfs():
    for fname in os.listdir(DATA_DIR):
        if fname.lower().endswith(".pdf"):
            path = os.path.join(DATA_DIR, fname)
            ingest_pdf(path)

# =========================
# Main
# =========================

if __name__ == "__main__":
    ingest_all_pdfs()
    print("\nPDF ingestion completed!")
