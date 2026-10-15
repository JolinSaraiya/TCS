"""Person B owns this file. Review Station tab."""
import streamlit as st


def render_review_tab(state: dict) -> None:
    """TODO (B): cards with score breakdown, Decision/Reason/Next Action, Approve/Edit/Reject."""
    st.info("STUB: Review Station (Person B)")
    for i in sorted(state.get("items", []), key=lambda x: x.get("total", 0), reverse=True):
        st.write(f"**{i['title']}** — {i['decision']} ({i['total']}) — {i['status']}")
