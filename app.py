"""Person C owns this shell. Already wired; only touch to fix bugs."""
import json
import os

import streamlit as st
from dotenv import load_dotenv

import pipeline
import storage
from config import SAMPLE_ITEMS_PATH, STATE_PATH
from ui_newsletter import render_export_tab, render_newsletter_tab
from ui_review import render_review_tab

load_dotenv()
st.set_page_config(page_title="AI Pulse", layout="wide")


def init_state() -> dict:
    if "state" not in st.session_state:
        state = storage.load_state()
        if not state.get("items"):
            with open(SAMPLE_ITEMS_PATH, encoding="utf-8") as f:
                items = json.load(f)
            use_cache = os.getenv("USE_CACHE_ONLY", "true").lower() == "true"
            out = pipeline.run_pipeline(items, use_cache=use_cache)
            state = {"run_source": out.get("run_source", "cached"), "headline": out.get("headline", ""),
                     "challenge": out.get("challenge", ""), "period": "weekly",
                     "items": storage.merge(items, out)}
            storage.save_state(state)
        st.session_state["state"] = state
    return st.session_state["state"]


state = init_state()
st.title("AI Pulse")
st.caption(f"Data source: **{state['run_source']}**")

with st.sidebar:
    if st.button("Reset demo state"):
        if os.path.exists(STATE_PATH):
            os.remove(STATE_PATH)
        st.session_state.clear()
        st.rerun()

tab1, tab2, tab3 = st.tabs(["Review Station", "Newsletter", "Export"])
with tab1:
    render_review_tab(state)
with tab2:
    render_newsletter_tab(state)
with tab3:
    render_export_tab(state)
