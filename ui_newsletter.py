"""Newsletter and Export tabs (Phase 4).
Interactive preview, weekly/monthly window toggle, publish gate validation, and exports.
"""
import streamlit as st
import newsletter
import storage


def render_newsletter_tab(state: dict) -> None:
    st.subheader("📰 Newsletter Preview & Configuration")

    # Period Toggle: Weekly vs Monthly
    c1, c2 = st.columns([3, 7])
    with c1:
        current_period = state.get("period", "weekly")
        period = st.radio(
            "Select Edition Window",
            ["weekly", "monthly"],
            index=0 if current_period == "weekly" else 1,
            format_func=lambda x: "Weekly (Last 7 days, max 3 items)" if x == "weekly" else "Monthly (Last 30 days, max 5 items)",
            key="newsletter_period_radio"
        )
        if period != current_period:
            state["period"] = period
            storage.save_state(state)
            st.rerun()

    # Build newsletter object
    nl = newsletter.build_newsletter(state, period)

    # Publish Gate Banner
    with c2:
        if nl["publishable"]:
            st.success(
                f"✅ **Publish Gate PASSED**: {len(nl['items'])} items approved and within the {period} window. Ready to publish!",
                icon="🚀"
            )
        else:
            st.warning(
                f"⚠️ **Publish Gate LOCKED**: {nl['message']}\n\n*Head over to the Review Station tab to approve items.*",
                icon="🔒"
            )

    st.divider()

    # Editable Headline and Challenge
    h_col, c_col = st.columns([1, 1])
    with h_col:
        new_headline = st.text_input(
            "Newsletter Headline (Max 10 words)",
            value=state.get("headline", ""),
            key="nl_headline_input"
        )
        if new_headline != state.get("headline", ""):
            state["headline"] = new_headline
            storage.save_state(state)

    with c_col:
        new_challenge = st.text_input(
            "5-Minute Learning Challenge",
            value=state.get("challenge", ""),
            key="nl_challenge_input"
        )
        if new_challenge != state.get("challenge", ""):
            state["challenge"] = new_challenge
            storage.save_state(state)

    st.divider()

    # Preview Section
    st.markdown("### 👁️ Issue Preview")
    if not nl["items"]:
        st.info(f"No approved items found within the {period} window. Go to the Review Station and approve items published in the last {'7' if period == 'weekly' else '30'} days.")
    else:
        # Render the formatted HTML inside Streamlit
        html_content = newsletter.export_html(nl)
        st.components.v1.html(html_content, height=750, scrolling=True)


def render_export_tab(state: dict) -> None:
    st.subheader("📤 Export & Distribution")
    period = state.get("period", "weekly")
    nl = newsletter.build_newsletter(state, period)

    if not nl["publishable"]:
        st.error(
            f"🚫 **Export Disabled by Publish Gate**\n\n{nl['message']}\n\n"
            f"You currently have **{len(nl['items'])}** approved items in the {period} window. "
            f"Minimum required is **3** to maintain high newsletter quality.",
            icon="🔒"
        )
        return

    st.success(f"🎉 Newsletter is ready for export with **{len(nl['items'])}** curated stories!")

    d1, d2 = st.columns(2)
    md_content = newsletter.export_markdown(nl)
    html_content = newsletter.export_html(nl)

    with d1:
        st.download_button(
            label="📥 Download Markdown (.md)",
            data=md_content,
            file_name=f"ai_pulse_{period}_{nl['as_of']}.md",
            mime="text/markdown",
            key="download_md_btn"
        )

    with d2:
        st.download_button(
            label="📥 Download HTML (.html)",
            data=html_content,
            file_name=f"ai_pulse_{period}_{nl['as_of']}.html",
            mime="text/html",
            key="download_html_btn"
        )

    st.divider()

    exp1, exp2 = st.tabs(["Markdown Source", "HTML Source"])
    with exp1:
        st.code(md_content, language="markdown")
    with exp2:
        st.code(html_content, language="html")
