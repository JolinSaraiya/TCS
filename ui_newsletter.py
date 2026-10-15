"""Person C owns this file. Newsletter + Export tabs."""
import streamlit as st

import newsletter


def render_newsletter_tab(state: dict) -> None:
    """TODO (C): weekly/monthly toggle, preview, publish gate."""
    st.info("STUB: Newsletter (Person C)")
    nl = newsletter.build_newsletter(state, state.get("period", "weekly"))
    st.markdown(newsletter.export_markdown(nl))
    if nl["message"]:
        st.warning(nl["message"])


def render_export_tab(state: dict) -> None:
    """TODO (C): download .md / .html, copy box."""
    nl = newsletter.build_newsletter(state, state.get("period", "weekly"))
    st.download_button("Download Markdown", newsletter.export_markdown(nl), "ai_pulse.md",
                       disabled=not nl["publishable"])
