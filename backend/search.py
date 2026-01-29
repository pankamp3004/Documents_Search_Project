from typing import List, Dict, Any, Optional

from indexing.embeddings import embed_text
from indexing.create_index import es, INDEX_NAME


# =========================
# BM25 Search
# =========================

def bm25_search(query: str, size: int = 50, document_type: Optional[str] = None):
    filters = []
    if document_type:
        filters.append({"term": {"document_type": document_type}})

    body = {
        "size": size,
        "query": {
            "bool": {
                "filter": filters,
                "must": [
                    {
                        "match": {
                            "chunk_text": {
                                "query": query,
                                "operator": "and"
                            }
                        }
                    }
                ]
            }
        }
    }

    return es.search(index=INDEX_NAME, body=body, request_timeout=30)


# =========================
# Vector Search
# =========================

def vector_search(
    query_vector,
    k: int = 50,
    num_candidates: int = 200,
    document_type: Optional[str] = None
):
    filters = []
    if document_type:
        filters.append({"term": {"document_type": document_type}})

    body = {
        "size": k,
        "knn": {
            "field": "embedding",
            "query_vector": query_vector,
            "k": k,
            "num_candidates": num_candidates,
            "filter": filters
        }
    }

    return es.search(index=INDEX_NAME, body=body, request_timeout=30)


# =========================
# Ranking Utilities
# =========================

def extract_ranks(hits) -> Dict[str, int]:
    ranks = {}
    for i, hit in enumerate(hits):
        ranks[hit["_id"]] = i + 1  # rank starts at 1
    return ranks


def reciprocal_rank_fusion(bm25_hits, vector_hits, k: int = 60) -> Dict[str, float]:
    bm25_ranks = extract_ranks(bm25_hits)
    vector_ranks = extract_ranks(vector_hits)

    fused_scores = {}
    all_doc_ids = set(bm25_ranks) | set(vector_ranks)

    for doc_id in all_doc_ids:
        score = 0.0

        if doc_id in bm25_ranks:
            score += 1.0 / (k + bm25_ranks[doc_id])

        if doc_id in vector_ranks:
            score += 1.0 / (k + vector_ranks[doc_id])

        fused_scores[doc_id] = score

    return fused_scores


# =========================
# Hybrid Search (FINAL)
# =========================

def hybrid_document_search_rrf(
    query: str,
    top_n: int = 10,
    document_type: Optional[str] = None,
    min_rrf_score: float = 0.0155  # threshold
) -> List[Dict[str, Any]]:

    # 1️ BM25 search
    bm25_res = bm25_search(query, size=50, document_type=document_type)
    bm25_hits = bm25_res["hits"]["hits"]

    # 2️ Vector search
    query_vector = embed_text(query)
    vector_res = vector_search(query_vector, k=50, document_type=document_type)
    vector_hits = vector_res["hits"]["hits"]

    # # 3️ Build ranks (for dual-signal requirement)    j# it means .. documents must appear in both searches
    # bm25_ranks = extract_ranks(bm25_hits)
    # vector_ranks = extract_ranks(vector_hits)

    # 4️ RRF fusion
    fused_scores = reciprocal_rank_fusion(bm25_hits, vector_hits, k=60)

    # 5️ Lookup full docs
    doc_lookup = {}
    for hit in bm25_hits + vector_hits:
        doc_lookup[hit["_id"]] = hit

    # 6️ Sort by RRF score
    ranked = sorted(
        fused_scores.items(),
        key=lambda x: x[1],
        reverse=True
    )

    # 7️ Build final results with threshold + dual-signal
    results: List[Dict[str, Any]] = []

    for doc_id, rrf_score in ranked:

        # Threshold filter
        if rrf_score < min_rrf_score:
            continue

        # # Require BOTH BM25 and Vector
        # if doc_id not in bm25_ranks or doc_id not in vector_ranks:
        #     continue

        hit = doc_lookup[doc_id]
        src = hit["_source"]

        results.append({
            "rrf_score": rrf_score,
            "chunk_text": src.get("chunk_text", ""),
            "snippet": src.get("snippet", ""), 
            "chunk_url": src.get("chunk_url"),       
            "title": src.get("title"),
            "doc_id": src.get("doc_id"),
            "chunk_index": src.get("chunk_index"),
            "document_type": src.get("document_type"),
        })

        if len(results) >= top_n:
            break

    return results


