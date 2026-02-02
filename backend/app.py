import streamlit as st
import requests
from typing import List, Dict

# =========================
# Config & Setup
# =========================
API_URL = "http://127.0.0.1:8000/search"

st.set_page_config(
    page_title="AI Document Search | Neural Engine",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# =========================
# PIXEL PERFECT CSS
# =========================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700;800&display=swap');

    /* Hide Streamlit Header/Footer */
    header, footer, #MainMenu {visibility: hidden;}
    .stDeployButton {display:none;}
    
    /* Global Styles */
    .stApp {
        background-color: #050508 !important;
        background-image: 
            radial-gradient(circle at 50% 50%, rgba(102, 32, 174, 0.15) 0%, transparent 50%),
            radial-gradient(circle at 0% 0%, rgba(102, 32, 174, 0.08) 0%, transparent 30%) !important;
        font-family: 'Poppins', sans-serif !important;
    }

    /* Navbar Simulation */
    .nav-container {
        position: fixed;
        top: 0; left: 0; right: 0;
        padding: 10px 60px;
        background: rgba(10, 10, 15, 0.85);
        backdrop-filter: blur(25px);
        border-bottom: 1px solid rgba(255, 255, 255, 0.08);
        z-index: 1000;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }

    /* Hero Text */
    .hero-title {
        font-size: 4.2rem !important;
        font-weight: 800 !important;
        letter-spacing: -3px !important;
        color: white !important;
        text-align: center;
        margin-top: 80px !important;
        margin-bottom: 5px !important;
    }
    .hero-sub {
        font-size: 1.6rem !important;
        color: #94a3b8 !important;
        text-align: center;
        max-width: 850px;
        margin: 0 auto 50px auto !important;
        line-height: 1.6;
    }

    /* Input Box Design */
    div[data-baseweb="input"] {
        background-color: rgba(255, 255, 255, 0.04) !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        border-radius: 12px !important;
        padding: 8px !important;
    }
    input {
        color: white !important;
        font-size: 1.1rem !important;
    }

    /* Search Button */
    div.stButton > button {
        background: #6620ae !important;
        color: white !important;
        border-radius: 10px !important;
        border: none !important;
        padding: 12px 30px !important;
        font-weight: 600 !important;
        transition: 0.3s !important;
        box-shadow: 0 0 15px rgba(102, 32, 174, 0.4) !important;
    }
    div.stButton > button:hover {
        transform: scale(1.02);
        box-shadow: 0 0 25px rgba(102, 32, 174, 0.6) !important;
    }

    /* Slider & Labels */
    .stSlider label, .stSelectbox label {
        color: #94a3b8 !important;
        font-size: 0.7rem !important;
        text-transform: uppercase !important;
        letter-spacing: 1px !important;
        font-weight: 600 !important;
    }

    /* Custom Footer */
    .custom-footer {
        text-align: center;
        color: #4b5563;
        font-size: 0.8rem;
        margin-top: 100px;
        padding-bottom: 40px;
    }
    .st-emotion-cache-zy6yx3{
        padding-top:0 !important;
            }
div[data-testid="stHorizontalBlock"] 
  > div[data-testid="stColumn"]:nth-child(4) {
    display: none;
}
  .st-emotion-cache-1vo6xi6{
            min-height:90px !important;
    border-radius:50% !important;
            }  
            div[data-baseweb="input"] {
   
     padding: 0px !important; 
    height: 101%;
}
            .st-emotion-cache-79elbk{
            height:100% !important;}
    .st-d9 {
    font-size: 20px !important;
    padding: 20px;
}
</style>
""", unsafe_allow_html=True)

# =========================
# TOP NAVIGATION BAR
# =========================
# Using columns to place settings in the top right like the screenshot
nav_col1, nav_col2, nav_col3, nav_col4 = st.columns([2, 1, 1, 1])

with nav_col1:
    st.markdown('<div style="font-weight:700; font-size:1.8rem; color:white; padding-top:15px;">📚 AI Document Search</div>', unsafe_allow_html=True)

with nav_col2:
    top_n = st.slider("MAX RESULTS", 1, 50, 15)

with nav_col3:
    category_display = st.selectbox("CATEGORY", options=["All Assets", "Library Books", "Digital Blogs", "Scientific Papers"])
    # Map back to API values
    category_map = {"All Assets": "All", "Library Books": "book", "Digital Blogs": "blog", "Scientific Papers": "paper"}
    document_type = category_map[category_display]

# =========================
# MAIN HERO SECTION
# =========================
st.markdown('<h1 class="hero-title">AI Document Search</h1>', unsafe_allow_html=True)
st.markdown('<p class="hero-sub">Explore a universe of knowledge across ML, DL, and NLP documents using <b style="color:white">hybrid semantic + keyword search</b>.</p>', unsafe_allow_html=True)

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
                st.markdown("""<div style="margin: 20px 0; border-bottom: 1px solid rgba(255,255,255,0.1); padding-bottom: 20px;">""", unsafe_allow_html=True)
                cols = st.columns([3, 1])
                with cols[0]:
                    st.markdown(f"#### {r.get('title', 'Unknown')}")
                    st.markdown(f"<code style='color:#6620ae'>{r.get('document_type', 'N/A').upper()}</code>", unsafe_allow_html=True)
                    st.write(r.get("snippet"))
                    chunk_url = r.get("chunk_url")
                    if chunk_url:
                        st.markdown(f"[View Full Document]({chunk_url})")
                with cols[1]:
                    st.metric("Score", f"{r.get('rrf_score', 0):.4f}")
                st.markdown("</div>", unsafe_allow_html=True)

# =========================
# FOOTER
# =========================
st.markdown('<div class="custom-footer">Powered by Elasticsearch Hybrid Search + Sentence Transformers</div>', unsafe_allow_html=True)