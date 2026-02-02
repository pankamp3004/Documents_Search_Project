from fastapi import FastAPI, Query, Request, HTTPException
import time
import os
from typing import Optional, List
from backend.search import hybrid_document_search_rrf
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()


MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("MONGO_DB_NAME", "ai_search")
CHUNK_COLLECTION = os.getenv("CHUNK_COLLECTION_NAME", "document_chunks")  


client = MongoClient(MONGO_URI)
db = client[DB_NAME]
chunks_collection = db[CHUNK_COLLECTION]



app = FastAPI(
    title="Document Search API",
    description="BM25 + Vector Hybrid Search  + RRF Fusion",
)


@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.perf_counter()
    response = await call_next(request)
    process_time = (time.perf_counter() - start_time) * 1000  # ms

    response.headers["X-Process-Time-ms"] = f"{process_time:.2f}"
    print(f"[API LATENCY] {request.url.path} = {process_time:.2f} ms")

    return response



@app.get("/")
def health_check():
    return {"status": "ok", "service": "ecommerce-search"}


@app.get("/chunk/{chunk_id}")
def get_chunk(chunk_id: str):

    chunk = chunks_collection.find_one({"chunk_id": chunk_id})

    if not chunk:
        raise HTTPException(status_code=404, detail="Chunk not found")

    return {
        "chunk_id": chunk["chunk_id"],
        "doc_id": chunk["doc_id"],
        "title": chunk.get("title"),
        "chunk_text": chunk["chunk_text"]
    }


@app.get("/search")
def search_products(
    query: str = Query(..., description="User search query"),
    top_n: int = Query(10, description="Number of results to return"),
    document_type: Optional[str] = Query(None, description="Filter by document type")
):
    """
    Hybrid search endpoint:
    - query: user query text
    - top_n: number of results to return
    - ducument_type: optional document type filter
    """

    # Call your hybrid search
    res = hybrid_document_search_rrf(
        query=query,
        top_n=top_n,
        document_type=document_type
    )

    return res
