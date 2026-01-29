import os
import uuid
from datetime import datetime,timezone
from typing import List
from indexing.embeddings import embed_text
from indexing.chunk_documents import chunk_text
from indexing.preprocess import clean_text
from indexing.create_index import es, INDEX_NAME
from utils.cloudinary_upload import upload_chunk_to_cloudinary

from pymongo import MongoClient
from elasticsearch import helpers
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = "ai_search"
COLLECTION = "documents"

client = MongoClient(MONGO_URI)
db = client[DB_NAME]
documents = db[COLLECTION]


def index_all_documents():
    total_docs = documents.count_documents({})
    print(f"Found {total_docs} documents in MongoDB")

    actions = []
    chunk_counter = 0

    for doc in documents.find({}):
        doc_id = doc["doc_id"]
        title = doc.get("title")
        document_type = doc.get("document_type", "unknown")
        raw_text = doc.get("raw_text", "")

        chunks = chunk_text(raw_text)

        for idx, chunk in enumerate(chunks):
            cleaned_chunk = clean_text(chunk)
            if not cleaned_chunk.strip():
                continue

            # -----------------
            # Embedding
            # -----------------
            embedding = embed_text(cleaned_chunk)
            chunk_id = f"{doc_id}_c{idx}"

            # 1️ Upload to Cloudinary
            print("Uploading chunk to Cloudinary...")
            chunk_url = upload_chunk_to_cloudinary(chunk_id, cleaned_chunk)
            print(f"Uploaded chunk to Cloudinary: {chunk_url}")
            
            # 2️ Generate snippet
            snippet = cleaned_chunk[:100] + "..." if len(cleaned_chunk) > 100 else cleaned_chunk

            es_doc = {
                "chunk_id": chunk_id,
                "chunk_url": chunk_url,          
                "snippet": snippet,  

                "doc_id": doc_id,
                "title": title,
                "document_type": document_type,

                "chunk_index": idx,
                "chunk_text": cleaned_chunk,       # i can remove this from here because i am addding a hyperlink for full chunk text .. but fir bhi rkh lete h cross veryfy ke liye

                "embedding": embedding,
                "num_tokens": len(cleaned_chunk.split()),
                "created_at": datetime.now(timezone.utc)
            }

            actions.append({
                "_index": INDEX_NAME,
                "_id": es_doc["chunk_id"],
                "_source": es_doc
            })

            chunk_counter += 1

            # -----------------
            # Bulk Flush (Batching)
            # -----------------
            if len(actions) >= 100:
                helpers.bulk(es, actions)
                actions.clear()

    # Flush remaining
    if actions:
        helpers.bulk(es, actions)

    print(f"Indexed {chunk_counter} chunks into Elasticsearch")

# =========================
# Main
# =========================

if __name__ == "__main__":
    index_all_documents()