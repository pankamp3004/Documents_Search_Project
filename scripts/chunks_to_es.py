import os
import uuid
from datetime import datetime,timezone
from typing import List
from indexing.embeddings import embed_text
from indexing.chunk_documents import chunk_text
from indexing.preprocess import clean_text
from indexing.create_index import es, INDEX_NAME
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

            es_doc = {
                "chunk_id": str(uuid.uuid4()),
                "doc_id": doc_id,
                "title": title,
                "document_type": document_type,

                "chunk_index": idx,
                "chunk_text": cleaned_chunk,

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