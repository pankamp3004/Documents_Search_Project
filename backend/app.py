import streamlit as st
import requests
from typing import List, Dict

# =========================
# Config
# =========================

API_URL = "http://127.0.0.1:8000/search"

st.set_page_config(
    page_title="AI Document Search",
    page_icon="📚",
    layout="wide"
)

# =========================
# Sidebar
# =========================

st.sidebar.title("🔍 Search Settings")

top_n = st.sidebar.slider("Number of results", 5, 30, 10)

document_type = st.sidebar.selectbox(
    "Document Type Filter",
    options=["All", "book", "blog", "paper"],
    index=0
)

# =========================
# Header
# =========================

st.title("📚 AI Document Search")
st.markdown("Search across ML, DL, NLP documents using **hybrid semantic + keyword search**.")

# =========================
# Search Input
# =========================

query = st.text_input(
    "Enter your query:",
    placeholder="e.g. Explain transformer attention mechanism"
)

search_clicked = st.button("🔎 Search")

# =========================
# Helper: API Call
# =========================

def call_search_api(query: str, top_n: int, document_type: str):
    params = {
        "query": query,
        "top_n": top_n
    }

    if document_type != "All":
        params["document_type"] = document_type

    try:
        resp = requests.get(API_URL, params=params, timeout=30)
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        st.error(f"API error: {e}")
        return []

# =========================
# Results Display
# =========================

if search_clicked and query.strip():
    with st.spinner("Searching documents..."):
        results = call_search_api(query, top_n, document_type)

    if not results:
        st.warning("No results found.")
    else:
        st.success(f"Found {len(results)} results")

        for i, r in enumerate(results, start=1):
            with st.container():
                st.markdown("---")
                cols = st.columns([3, 1])

                with cols[0]:
                    st.markdown(f"### 🔹 Result #{i}")
                    st.markdown(f"**Source:** `{r.get('title', 'Unknown')}`")
                    st.markdown(f"**Document Type:** `{r.get('document_type', 'N/A')}`")
                    st.markdown(f"**Chunk Index:** `{r.get('chunk_index')}`")

                with cols[1]:
                    st.metric("Score", f"{r.get('rrf_score', 0):.4f}")

                # Chunk Text (Expandable)
                with st.expander("📄 View Chunk Text"):
                    st.write(r.get("chunk_text", ""))

# =========================
# Footer
# =========================

st.markdown("---")
st.caption("Powered by Elasticsearch Hybrid Search + Sentence Transformers")
