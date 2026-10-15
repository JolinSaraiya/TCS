"""Review Station tab (Phase 3).
Interactive curator station for reviewing, editing, approving, or rejecting AI news items.
"""
import streamlit as st
import storage


def render_review_tab(state: dict) -> None:
    items = state.get("items", [])
    if not items:
        st.warning("No items available in state.")
        return

    # --- TOP METRICS BAR ---
    total_count = len(items)
    recommended_count = sum(1 for x in items if x.get("decision") == "recommended")
    filtered_count = sum(1 for x in items if x.get("decision") == "filtered")
    approved_count = sum(1 for x in items if x.get("status") == "approved")
    rejected_count = sum(1 for x in items if x.get("status") == "rejected")
    pending_count = sum(1 for x in items if x.get("status") == "pending")

    m1, m2, m3, m4, m5 = st.columns(5)
    m1.metric("Total Items", total_count)
    m2.metric("AI Recommended", recommended_count, help="Items scored >= 50 and not duplicates")
    m3.metric("AI Filtered", filtered_count, help="Corporate noise, hype, or low student relevance")
    m4.metric("Approved by You", f"{approved_count}", delta=f"{approved_count - 3} vs min 3" if approved_count >= 3 else "- Needs >= 3", delta_color="normal" if approved_count >= 3 else "inverse")
    m5.metric("Pending Review", pending_count)

    st.divider()

    # --- CONTROLS / FILTERS ---
    c1, c2, c3, c4 = st.columns([2, 2, 2, 2])
    with c1:
        status_filter = st.selectbox(
            "Status Filter",
            ["All", "Pending", "Approved", "Rejected"],
            key="review_status_filter"
        )
    with c2:
        decision_filter = st.selectbox(
            "AI Decision",
            ["All", "Recommended", "Filtered"],
            key="review_decision_filter"
        )
    with c3:
        topic_filter = st.selectbox(
            "Topic Category",
            ["All", "Tools", "Models", "Career", "Research", "Learning"],
            key="review_topic_filter"
        )
    with c4:
        sort_by = st.selectbox(
            "Sort Order",
            ["Score (Highest first)", "Score (Lowest first)", "Reading Time", "ID"],
            key="review_sort_order"
        )

    search_query = st.text_input(
        "🔍 Search titles, summaries, or sources",
        "",
        key="review_search_input"
    ).strip().lower()

    # Bulk actions
    b1, b2, _ = st.columns([2, 2, 4])
    with b1:
        if st.button("✓ Approve All Recommended", key="btn_approve_all_rec"):
            changed = False
            for it in items:
                if it.get("decision") == "recommended" and not it.get("duplicate_of") and it.get("status") == "pending":
                    it["status"] = "approved"
                    changed = True
            if changed:
                storage.save_state(state)
                st.rerun()
    with b2:
        if st.button("↺ Reset All to Pending", key="btn_reset_all_pending"):
            for it in items:
                it["status"] = "pending"
            storage.save_state(state)
            st.rerun()

    # Apply filters
    filtered_items = []
    for it in items:
        # Status filter
        if status_filter != "All" and it.get("status", "pending") != status_filter.lower():
            continue
        # Decision filter
        if decision_filter != "All" and it.get("decision", "filtered") != decision_filter.lower():
            continue
        # Topic filter
        if topic_filter != "All" and it.get("topic") != topic_filter:
            continue
        # Search query
        if search_query:
            haystack = f"{it.get('title', '')} {it.get('summary', '')} {it.get('source', '')} {it.get('why_it_matters', '')}".lower()
            if search_query not in haystack:
                continue
        filtered_items.append(it)

    # Apply sorting
    if sort_by == "Score (Highest first)":
        filtered_items.sort(key=lambda x: x.get("total", 0), reverse=True)
    elif sort_by == "Score (Lowest first)":
        filtered_items.sort(key=lambda x: x.get("total", 0))
    elif sort_by == "Reading Time":
        filtered_items.sort(key=lambda x: x.get("reading_time_min", 1), reverse=True)
    elif sort_by == "ID":
        filtered_items.sort(key=lambda x: x.get("id", ""))

    st.caption(f"Showing **{len(filtered_items)}** of {total_count} items")

    if not filtered_items:
        st.info("No items match the selected filters.")
        return

    # --- ITEM CARDS ---
    for item in filtered_items:
        iid = item.get("id", "unknown")
        status = item.get("status", "pending")
        decision = item.get("decision", "filtered")
        total = item.get("total", 0)
        topic = item.get("topic", "General")
        is_dup = bool(item.get("duplicate_of"))
        is_missing_date = item.get("date_flag") == "missing_date"
        is_edited = item.get("edited", False)

        # Container card
        with st.container(border=True):
            # Header Row
            hdr1, hdr2 = st.columns([7, 3])
            with hdr1:
                # Title as clickable link
                url = item.get("url", "#")
                title = item.get("title", "Untitled")
                st.markdown(f"### [{title}]({url})")

                # Meta tags line
                pub_date = item.get("published") or "Date Unknown"
                source = item.get("source", "Unknown Source")
                read_time = item.get("reading_time_min", 1)
                st.caption(f"**Source:** {source} | **Published:** {pub_date} | **Read Time:** ~{read_time} min (est.) | **Category:** `{topic}`")

            with hdr2:
                # Badges
                st.markdown(f"**Score:** `{total}/100`")
                if decision == "recommended":
                    st.success("AI: Recommended", icon="✅")
                else:
                    st.warning("AI: Filtered", icon="🚫")

                if status == "approved":
                    st.info("Status: **Approved**", icon="👍")
                elif status == "rejected":
                    st.error("Status: **Rejected**", icon="👎")
                else:
                    st.caption("Status: **Pending**")

            # Warnings / Alerts
            if is_dup:
                st.error(f"⚠️ **Duplicate Story:** This is a duplicate of `{item.get('duplicate_of')}`. Filtered automatically to avoid spamming readers.")

            if is_missing_date:
                st.warning("⚠️ **Missing Publication Date:** Excluded from strict weekly/monthly time windows.")

            if is_edited:
                st.caption("✏️ *Edited by human reviewer*")

            # Score Breakdown Expander
            scores = item.get("scores", {})
            with st.expander(f"📊 Score Breakdown: {total}/100 (Official Formula)"):
                st.write("**Formula:** `R = 0.35×T + 0.25×P + 0.20×N + 0.15×L + 0.05×Q`")
                sc1, sc2, sc3, sc4, sc5 = st.columns(5)
                sc1.metric("Tools (T 35%)", f"{scores.get('T', 0)}/100")
                sc2.metric("Career (P 25%)", f"{scores.get('P', 0)}/100")
                sc3.metric("Novelty (N 20%)", f"{scores.get('N', 0)}/100")
                sc4.metric("Learning (L 15%)", f"{scores.get('L', 0)}/100")
                sc5.metric("Quality (Q 5%)", f"{scores.get('Q', 0)}/100")
                st.caption(f"**AI Reason:** {item.get('reason', 'N/A')}")

            # Content preview
            st.markdown(f"**Summary:** {item.get('summary', '')}")
            st.markdown(f"**Why it matters to students:** {item.get('why_it_matters', '')}")

            # Extra structured fields
            aud = item.get("target_audience")
            nxt = item.get("what_to_do_next")
            act = item.get("next_action")
            if aud or nxt or act:
                info_cols = st.columns([4, 4, 2])
                if aud:
                    info_cols[0].caption(f"🎯 **Target Audience:** {aud}")
                if nxt:
                    info_cols[1].caption(f"⚡ **What to do next:** {nxt}")
                if act:
                    info_cols[2].caption(f"💡 **Suggested Action:** `{act.upper()}`")

            # Action Buttons & Inline Editor
            btn_col1, btn_col2, btn_col3, edit_col = st.columns([1.5, 1.5, 1.5, 3.5])
            with btn_col1:
                if st.button("Approve", key=f"app_{iid}", type="primary" if status == "approved" else "secondary"):
                    item["status"] = "approved"
                    storage.save_state(state)
                    st.rerun()

            with btn_col2:
                if st.button("Reject", key=f"rej_{iid}", type="primary" if status == "rejected" else "secondary"):
                    item["status"] = "rejected"
                    storage.save_state(state)
                    st.rerun()

            with btn_col3:
                if st.button("Pending", key=f"pen_{iid}"):
                    item["status"] = "pending"
                    storage.save_state(state)
                    st.rerun()

            with edit_col:
                with st.expander("✏️ Edit Content"):
                    new_summary = st.text_area("Summary", value=item.get("summary", ""), key=f"sum_{iid}")
                    new_why = st.text_area("Why it matters", value=item.get("why_it_matters", ""), key=f"why_{iid}")
                    if st.button("Save Changes", key=f"save_{iid}"):
                        item["summary"] = new_summary
                        item["why_it_matters"] = new_why
                        item["edited"] = True
                        storage.save_state(state)
                        st.success("Saved!")
                        st.rerun()
