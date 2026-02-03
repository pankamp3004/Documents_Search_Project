import streamlit as st
import requests
from typing import List, Dict

# =========================
# Config & Setup
# =========================
API_URL = "http://127.0.0.1:8000/search"

st.set_page_config(
    page_title="Hybrid Document Search | Neural Engine",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# =========================
# PIXEL PERFECT CSS
# =========================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');

/* ---------------- GLOBAL ---------------- */
header, footer, #MainMenu {visibility:hidden;}
.stDeployButton {display:none;}

.stApp {
    font-family: 'Inter', sans-serif !important;
    background:
        radial-gradient(circle at 30% 20%, rgba(255,193,7,0.12), transparent 40%),
        radial-gradient(circle at 80% 70%, rgba(255,193,7,0.06), transparent 40%),
        linear-gradient(180deg,#060606,#0b0b0b) !important;
    color:white;
}


/* ---------------- NAVBAR ---------------- */
.nav-container {
    background: rgba(15,15,15,0.75);
    backdrop-filter: blur(20px);
    border-bottom: 1px solid rgba(255,255,255,0.06);
}


/* ---------------- HERO TITLE ---------------- */
.hero-title {
    font-size: 4rem !important;
    font-weight: 700 !important;
    letter-spacing: -2px !important;
    text-align:center;
    margin-top: 90px !important;

    background: linear-gradient(90deg,#ffffff,#ffe082,#ffc107);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

.hero-sub {
    font-size: 1.6rem !important;
    color: #9ca3af !important;
    text-align:center;
    max-width: 900px;
    margin: 0 auto 60px auto !important;
}


/* ---------------- SEARCH INPUT ---------------- */
div[data-baseweb="input"] {
    background: #2c2c2c !important;
    border: 1px solid rgba(255,255,255,0.08) !important;
    border-radius: 18px !important;
    padding: 18px !important;

    backdrop-filter: blur(18px);
}

input {
    color:white !important;
    font-size: 1.2rem !important;
}


/* ---------------- GOLD SEARCH BUTTON ---------------- */
div.stButton > button {
    background: linear-gradient(135deg,#ffc107,#ffb300) !important;
    color:#111 !important;
    font-weight:700 !important;
    border-radius:14px !important;
    padding:14px 32px !important;
    border:none !important;

    box-shadow: 0 0 25px rgba(255,193,7,0.35);
    transition:0.25s ease;
}

div.stButton > button:hover {
    transform: scale(1.05);
    box-shadow: 0 0 40px rgba(255,193,7,0.65);
}


/* ---------------- RESULT CARDS ---------------- */
.result-card {
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 18px;
    padding: 24px;
    margin-bottom: 22px;
    backdrop-filter: blur(12px);
}


/* ---------------- LABELS ---------------- */
.stSlider label,
.stSelectbox label {
    color:#9ca3af !important;
    font-size:0.75rem !important;
    text-transform:uppercase !important;
    letter-spacing:1px !important;
    font-weight:600 !important;
}


/* ---------------- FOOTER ---------------- */
.custom-footer {
    text-align:center;
    margin-top:120px;
    font-size:14px;
    color:#6b7280;
}


/* ---------------- LAYOUT FIXES ---------------- */
.st-emotion-cache-1n6tfoc {
    width:70% !important;
    margin:auto !important;
}
.st-emotion-cache-zy6yx3 {
    padding-top: 0 !important;
}
            div[data-baseweb="input"] {
    height: 56px !important;
    display: flex !important;
    align-items: center !important;
    padding: 0 18px !important;
    border-radius: 14px !important;
}

/* actual input text */
div[data-baseweb="input"] input {
    height: 100% !important;
    padding: 0 !important;
    background: #2c2c2c; !important;        
}

/* button exact same height */
div.stButton > button {
    height: 56px !important;
    padding: 0 28px !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
}
            div[data-baseweb="input"] input::placeholder {
    color: #9ca3af !important;   /* grey */
    opacity: 1 !important;
}

/* for full browser support */
div[data-baseweb="input"] input::-webkit-input-placeholder {
    color: #9ca3af !important;
}
div[data-baseweb="input"] input:-ms-input-placeholder {
    color: #9ca3af !important;
}
            .st-emotion-cache-1hm023c p{
            font-weight:500 !important;
            }
         /* ================= TOOLTIP ================= */

.tooltip {
    position: relative;
    display: inline-block;
    cursor: pointer;
}

/* tooltip box */
.tooltip .tooltiptext {
    visibility: hidden;
    opacity: 0;

    width: 620px;
    max-height: 320px;
    overflow-y: auto;

    background: rgba(25,25,25,0.95);
    color: #e5e7eb;

    text-align: left;
    padding: 14px;
    border-radius: 12px;

    font-size: 13px;
    line-height: 1.5;

    border: 1px solid rgba(255,255,255,0.08);
    backdrop-filter: blur(10px);

    position: absolute;
    z-index: 999;

    bottom: 140%;
    left: 0;

    box-shadow: 0 10px 40px rgba(0,0,0,0.6);

    transition: 0.25s ease;
}

/* show on hover */
.tooltip:hover .tooltiptext {
    visibility: visible;
    opacity: 1;
}

</style>
""", unsafe_allow_html=True)

# =========================
# TOP NAVIGATION BAR
# =========================
# Using columns to place settings in the top right like the screenshot
nav_col1, nav_col2, nav_col3 = st.columns([2, 0.5, 0.5])

with nav_col1:
    st.markdown('<div style="font-weight:600; font-size:1.4rem; color:white; padding-top:15px;">✨ Hybrid Document Search</div>', unsafe_allow_html=True)

with nav_col2:
    top_n = st.slider("MAX RESULTS", 1, 50, 15)

with nav_col3:
    category_display = st.selectbox("CATEGORY", options=["All Assets", "Books", "Blogs", "Research Papers"])
    # Map back to API values
    category_map = {"All Assets": "All", "Library Books": "book", "Digital Blogs": "blog", "Scientific Papers": "paper"}
    document_type = category_map[category_display]

# =========================
# MAIN HERO SECTION
# =========================
st.markdown('<h1 class="hero-title">Hybrid Document Search</h1>', unsafe_allow_html=True)
st.markdown('<p class="hero-sub">Explore a universe of knowledge across ML, DL, and NLP documents using <b style="color:white">semantic search + keyword search</b>.</p>', unsafe_allow_html=True)

# SEARCH BOX CENTERED
c1, c2, c3 = st.columns([1, 4, 1])
with c2:
    st.markdown('<p style="color:#94a3b8; font-size:1.4rem; margin-bottom:10px;">Start your research:</p>', unsafe_allow_html=True)
    
    # Placing button next to input using inner columns
    search_col, btn_col = st.columns([4, 1])
    with search_col:
        query = st.text_input("Query", placeholder="e.g. How does self-attention work in Transformers?", label_visibility="collapsed")
    with btn_col:
        search_clicked = st.button("🔍 Search")

# =========================
# FUNCTIONALITY (UNCHANGED)
# =========================
def call_search_api(query: str, top_n: int, document_type: str):
    params = {"query": query, "top_n": top_n}
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
# RESULTS DISPLAY
# =========================
if search_clicked and query.strip():
    with st.spinner("Searching documents..."):
        results = call_search_api(query, top_n, document_type)

    if not results:
        st.warning("No results found.")
    else:
        for i, r in enumerate(results, start=1):
            with st.container():
                st.markdown("""<div class="resultBox" style="margin: 0;padding-left:40px !important; border-bottom: 1px solid rgba(255,255,255,0.1); padding-bottom: 0px;">""", unsafe_allow_html=True)
                cols = st.columns([3, 0.1])
                with cols[0]:
                    st.markdown(f"#### {r.get('title', 'Unknown')}")
                    st.markdown(f"<code style='color:#6620ae'>{r.get('document_type', 'N/A').upper()}</code>", unsafe_allow_html=True)
                    st.write(r.get("snippet"))
                    chunk_url = r.get("chunk_url")
                    chunk_text = r.get("chunk_text", "")
                    # if chunk_text: 
                    #     st.write("**Full Document Text:**")
                    #     st.write(chunk_text)
                    if chunk_url:
                        st.markdown(f"""
                                     <a href="{chunk_url}" target="_blank">
                            <div class="tooltip">
                               View Full Document
                                <span class="tooltiptext">{chunk_text}</span>
                            </div></a>
                            """, unsafe_allow_html=True)
                # with cols[1]:
                #     st.metric("Score", f"{r.get('rrf_score', 0):.4f}")
                st.markdown("</div>", unsafe_allow_html=True)

# =========================
# FOOTER
# =========================
st.markdown('<div class="custom-footer">Powered by Elasticsearch Hybrid Search + Sentence Transformers</div>', unsafe_allow_html=True)