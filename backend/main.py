from fastapi import FastAPI, Query, Request
import time
from typing import Optional, List
from backend.search import hybrid_document_search_rrf


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
