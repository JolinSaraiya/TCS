"""AI Pulse — Interactive AI Newsletter Curator & Review Station
Main Streamlit Entrypoint.
"""
import json
import os

import streamlit as st
from dotenv import load_dotenv

import pipeline
import storage
from config import AS_OF, SAMPLE_ITEMS_PATH, STATE_PATH
from ui_newsletter import render_export_tab, render_newsletter_tab
from ui_review import render_review_tab

load_dotenv()
st.set_page_config(
    page_title="AI Pulse | AI Newsletter Engine",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom styling for high aesthetic polish
st.markdown("""
<style>
    /* Metric styling */
    [data-testid="stMetricValue"] {
        font-size: 1.8rem !important;
        font-weight: 700 !important;
    }
    /* Buttons */
    button[kind="primary"] {
        border-radius: 6px;
    }
    /* Badges */
    .source-badge-cached {
        background-color: #fef3c7;
        color: #92400e;
        padding: 3px 8px;
        border-radius: 12px;
        font-weight: 600;
        font-size: 12px;
    }
    .source-badge-live {
        background-color: #d1fae5;
        color: #065f46;
        padding: 3px 8px;
        border-radius: 12px;
        font-weight: 600;
        font-size: 12px;
    }
</style>
""", unsafe_allow_html=True)


def load_raw_items() -> list[dict]:
    with open(SAMPLE_ITEMS_PATH, encoding="utf-8") as f:
        return json.load(f)


def init_state() -> dict:
    if "state" not in st.session_state:
        state = storage.load_state()
        if not state.get("items"):
            items = load_raw_items()
            use_cache = os.getenv("USE_CACHE_ONLY", "true").lower() == "true"
            out = pipeline.run_pipeline(items, use_cache=use_cache)
            state = {
                "run_source": out.get("run_source", "cached"),
                "headline": out.get("headline", ""),
                "challenge": out.get("challenge", ""),
                "period": "weekly",
                "items": storage.merge(items, out)
            }
            storage.save_state(state)
        st.session_state["state"] = state
    return st.session_state["state"]


state = init_state()

# --- SIDEBAR ---
with st.sidebar:
    st.image("https://img.icons8.com/isometric-line/96/artificial-intelligence.png", width=64)
    st.title("AI Pulse")
    st.caption("Curated AI News for Future Software Engineers")

    source_type = state.get("run_source", "cached")
    if source_type == "live":
        st.markdown('Data Source: <span class="source-badge-live">● LIVE LLM</span>', unsafe_allow_html=True)
    else:
        st.markdown('Data Source: <span class="source-badge-cached">● CACHED (Offline Safe)</span>', unsafe_allow_html=True)

    st.markdown(f"📅 **As Of:** `{AS_OF}`")
    st.divider()

    st.subheader("⚡ Pipeline Controls")
    has_api_key = bool(os.getenv("GROQ_API_KEY") or os.getenv("GEMINI_API_KEY"))

    if st.button("🚀 Run Live Pipeline", disabled=not has_api_key, help="Call live LLM model (Groq/Gemini) if API key is configured in .env"):
        items = load_raw_items()
        with st.spinner("Calling LLM pipeline..."):
            out = pipeline.run_pipeline(items, use_cache=False)
            state["run_source"] = out.get("run_source", "live")
            state["headline"] = out.get("headline", state.get("headline"))
            state["challenge"] = out.get("challenge", state.get("challenge"))
            state["items"] = storage.merge(items, out)
            storage.save_state(state)
            st.session_state["state"] = state
            st.success("Pipeline refreshed!")
            st.rerun()

    if not has_api_key:
        st.caption("ℹ️ *Add `GROQ_API_KEY` or `GEMINI_API_KEY` to `.env` to enable live LLM re-ranking.*")

    if st.button("↺ Reset Demo State", help="Wipe all edits and reload fresh initial dataset"):
        if os.path.exists(STATE_PATH):
            os.remove(STATE_PATH)
        st.session_state.clear()
        st.rerun()

    st.divider()
    with st.expander("ℹ️ About & Formula"):
        st.markdown("""
        **Scoring Formula:**
        `R = 0.35T + 0.25P + 0.20N + 0.15L + 0.05Q`
        
        - **T (35%):** Tools & Practical Utility
        - **P (25%):** Professional / Career Impact
        - **N (20%):** Novelty & Breakthrough
        - **L (15%):** Learning Accessibility
        - **Q (5%):** Source Credibility
        
        **Publish Gate:**
        Requires at least 3 human-approved items within the selected time window (Weekly: 7 days, Monthly: 30 days).
        """)


# --- MAIN HEADER ---
h1, h2 = st.columns([8, 2])
with h1:
    st.title("⚡ AI Pulse")
    st.markdown("**Club Coordinator Review Station & Automated Newsletter Publisher**")
with h2:
    status_icon = "🟢" if state.get("run_source") == "live" else "🟡"
    st.write(f"### {status_icon} `{state.get('run_source', 'cached').upper()}`")


# --- TABS ---
tab1, tab2, tab3 = st.tabs(["📋 Review Station", "📰 Newsletter Preview", "📤 Export & Publish"])

with tab1:
    render_review_tab(state)

with tab2:
    render_newsletter_tab(state)

with tab3:
    render_export_tab(state)
