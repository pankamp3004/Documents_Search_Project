from fastapi import FastAPI, Query, Request, HTTPException
import time
from fastapi.responses import HTMLResponse
import html

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



# @app.get("/chunk/{chunk_id}")
# def get_chunk(chunk_id: str):

#     chunk = chunks_collection.find_one({"chunk_id": chunk_id})

#     if not chunk:
#         raise HTTPException(status_code=404, detail="Chunk not found")

#     return {
#         # "chunk_id": chunk["chunk_id"],
#         # "doc_id": chunk["doc_id"],
#         # "title": chunk.get("title"),
#         "chunk_text": chunk["chunk_text"]
#     }




@app.get("/chunk/{chunk_id}", response_class=HTMLResponse)
def get_chunk(chunk_id: str):

    chunk = chunks_collection.find_one({"chunk_id": chunk_id})

    if not chunk:
        raise HTTPException(status_code=404, detail="Chunk not found")

    title = chunk.get("title", "Document Reader")
    chunk_text = html.escape(chunk["chunk_text"])


    html_page = f"""
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<title>{title}</title>

<style>

/* =========================
   Global
========================= */
body {{
    margin: 0;
    font-family: Inter, -apple-system, BlinkMacSystemFont, sans-serif;
    background: linear-gradient(135deg,#667eea,#764ba2);
    display: flex;
    flex-direction: column;
    height: 100vh;
}}

/* =========================
   Top Navbar (Glass style)
========================= */
.navbar {{
    backdrop-filter: blur(12px);
    background: rgba(255,255,255,0.15);
    padding: 14px 28px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    color: white;
    position: sticky;
    top: 0;
}}

.nav-title {{
    font-size: 18px;
    font-weight: 700;
}}

/* Buttons */
.btn {{
    border: none;
    padding: 8px 14px;
    border-radius: 8px;
    cursor: pointer;
    font-weight: 600;
    margin-left: 8px;
}}

.btn-light {{
    background: white;
    color: #333;
}}

.btn-primary {{
    background: #10b981;
    color: white;
}}

.btn:hover {{
    opacity: 0.9;
}}

/* =========================
   Reader Container
========================= */
.wrapper {{
    flex: 1;
    display: flex;
    justify-content: center;
    align-items: center;
    padding: 40px 20px;
}}

.card {{
    width: 100%;
    max-width: 900px;
    height: 85vh;
    background: white;
    border-radius: 22px;
    padding: 40px;
    box-shadow: 0 20px 60px rgba(0,0,0,0.25);
    display: flex;
    flex-direction: column;
}}

/* Title */
.doc-title {{
    font-size: 26px;
    font-weight: 800;
    margin-bottom: 20px;
    color: #111827;
}}

/* Text Content */
.content {{
    flex: 1;
    overflow-y: auto;
    line-height: 1.9;
    font-size: 18px;
    color: #374151;
    white-space: pre-wrap;
}}

/* Scrollbar */
.content::-webkit-scrollbar {{
    width: 8px;
}}
.content::-webkit-scrollbar-thumb {{
    background: #cbd5e1;
    border-radius: 8px;
}}

</style>

<script>
function copyText() {{
    const text = document.getElementById("chunk").innerText;
    navigator.clipboard.writeText(text);
    alert("Copied to clipboard!");
}}

function downloadTxt() {{
    const text = document.getElementById("chunk").innerText;
    const blob = new Blob([text], {{type: "text/plain"}});
    const a = document.createElement("a");
    a.href = URL.createObjectURL(blob);
    a.download = "chunk.txt";
    a.click();
}}
</script>

</head>

<body>

<!-- ================= Navbar ================= -->
<div class="navbar">
    <div class="nav-title">📖 {title}</div>

    <div>
        <button class="btn btn-light" onclick="history.back()">← Back</button>
        <button class="btn btn-light" onclick="copyText()">Copy</button>
        <button class="btn btn-primary" onclick="downloadTxt()">Download</button>
    </div>
</div>


<!-- ================= Reader ================= -->
<div class="wrapper">
    <div class="card">

        <div class="doc-title">{title}</div>

        <div id="chunk" class="content">
{chunk_text}
        </div>

    </div>
</div>

</body>
</html>
"""

    return HTMLResponse(content=html_page)

