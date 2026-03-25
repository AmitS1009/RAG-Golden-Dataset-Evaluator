import streamlit as st
import json

# Set up page configuration
st.set_page_config(
    page_title="RAG Golden Dataset Evaluator",
    page_icon="🧠",
    layout="wide"
)

# Custom CSS for nicer UI
st.markdown("""
    <style>
    .qa-box {
        background-color: #f8f9fa;
        padding: 20px;
        border-radius: 10px;
        margin-bottom: 20px;
        border-left: 5px solid #0052cc;
        color: #1e1e1e;
    }
    .qa-q {
        font-weight: 600;
        font-size: 1.15em;
        margin-bottom: 10px;
        color: #000;
    }
    .qa-a {
        margin-bottom: 10px;
        color: #333;
    }
    .qa-source {
        font-size: 0.85em;
        color: #0052cc;
        font-weight: 600;
        text-align: right;
    }
    </style>
""", unsafe_allow_html=True)

st.title("🧠 RAG Engine: Golden Evaluation Dataset")
st.markdown("A robust, carefully curated evaluation set for testing RAG pipelines against advanced Deep Learning academic lectures.")

# Read Data
@st.cache_data
def load_data():
    try:
        with open("golden_dataset.json", "r", encoding="utf-8") as f:
            data = json.load(f)
        return data
    except Exception as e:
        return []

@st.cache_data
def load_methodology():
    try:
        with open("methodology.md", "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        return "Methodology document not found."

qa_pairs = load_data()
method_text = load_methodology()

# Layout: 2 Columns
col1, col2 = st.columns([1.5, 1])

with col1:
    st.header("📚 Evaluation QA Pairs (Top 5)")
    st.markdown("These pairs test conceptual nuances, demanding strictly grounded retrievals.")
    
    if qa_pairs:
        for idx, pair in enumerate(qa_pairs):
            st.markdown(f"""
                <div class="qa-box">
                    <div class="qa-q">Q{idx + 1}: {pair.get('question', '')}</div>
                    <div class="qa-a"><strong>Expected Answer:</strong> {pair.get('answer', '')}</div>
                    <div class="qa-source">▶ Source: {pair.get('source', '')}</div>
                </div>
            """, unsafe_allow_html=True)
    else:
        st.warning("No dataset found. Run `generate_golden_dataset.py` first.")

with col2:
    st.header("🔬 Methodology")
    with st.expander("Read Methodology Document", expanded=True):
        st.markdown(method_text)
    
    st.header("🎯 Project Source Videos")
    st.markdown("""
    1. **But what is a Neural Network?** (3Blue1Brown)
    2. **Transformers, the tech behind LLMs** (3Blue1Brown)
    3. **What is Deep Learning?** (CampusX - Hindi)
    4. **All About ML & Deep Learning** (CodeWithHarry - Hindi)
    """)
    
    st.info("Pipeline Execution Note: Built using Python, python-dotenv, and Groq SDK (Llama 3 Model). Transcript fetching implemented fallback strategies due to YouTube API rate-limiting.")

st.markdown("---")
st.caption("Livo AI Agent Assignment implementation.")
