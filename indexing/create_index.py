from elasticsearch import Elasticsearch
import os
from dotenv import load_dotenv

load_dotenv()

# =========================
# Config
# =========================

ELASTIC_USERNAME = "elastic"
ELASTIC_PASSWORD = os.getenv("ELASTIC_PASSWORD")
INDEX_NAME = os.getenv("INDEX_NAME", "documents_index")
# =========================
# ES Client
# =========================
# Connect to Elasticsearch
es = Elasticsearch(
    "https://localhost:9200",
    basic_auth=(ELASTIC_USERNAME, ELASTIC_PASSWORD),
    verify_certs=False  # local self-signed cert
)

# =========================
# Index Mapping
# =========================

INDEX_MAPPING = {
    "settings": {
        "number_of_shards": 1,
        "number_of_replicas": 0,
    },
    "mappings": {
        "properties": {

            # Identifiers
            "chunk_id": {"type": "keyword"},
            "doc_id": {"type": "keyword"},

            # Metadata
            "title": {"type": "text"},
            "document_type": {"type": "keyword"},

            # Chunk info
            "chunk_index": {"type": "integer"},
            "chunk_text": {
                "type": "text",
                "analyzer": "standard"
            },

            # Vector Embedding (Sentence Transformers)
            "embedding": {
                "type": "dense_vector",
                "dims": 384,
                "index": True,
                "similarity": "cosine"
            },

            # Stats
            "num_tokens": {"type": "integer"},

            # Timestamp
            "created_at": {"type": "date"}
        }
    }
}

# =========================
# Create Index
# =========================

def create_index():
    if es.indices.exists(index=INDEX_NAME):
        print(f"Index '{INDEX_NAME}' already exists. Deleting...")
        es.indices.delete(index=INDEX_NAME)

    print(f"Creating index: {INDEX_NAME}")
    es.indices.create(index=INDEX_NAME, body=INDEX_MAPPING)
    print("Index created successfully")

# =========================
# Main
# =========================

if __name__ == "__main__":
    create_index()
