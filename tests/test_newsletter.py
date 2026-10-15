"""Automated tests for newsletter builder, window filtering, publish gate, and exports."""
import json
import pytest
from config import AS_OF, MIN_ITEMS_TO_PUBLISH, SAMPLE_ITEMS_PATH
import newsletter
import pipeline
import storage


@pytest.fixture
def clean_state():
    with open(SAMPLE_ITEMS_PATH, encoding="utf-8") as f:
        items = json.load(f)
    out = pipeline.run_pipeline(items, use_cache=True)
    return {
        "run_source": out.get("run_source", "cached"),
        "headline": out.get("headline", ""),
        "challenge": out.get("challenge", ""),
        "period": "weekly",
        "items": storage.merge(items, out),
    }


def test_case_8_publish_gate_locked_when_under_min_approved(clean_state):
    """Case 8: When approved items < 3, publishable is False and message is set."""
    # Reset all to pending
    for it in clean_state["items"]:
        it["status"] = "pending"

    # 0 approved
    nl = newsletter.build_newsletter(clean_state, "weekly")
    assert nl["publishable"] is False
    assert f"Approve at least {MIN_ITEMS_TO_PUBLISH}" in nl["message"]

    # Approve only 2 items in weekly window (e.g. a01 and a02)
    clean_state["items"][0]["status"] = "approved"  # a01: 2026-10-12 (2 days ago)
    clean_state["items"][1]["status"] = "approved"  # a02: 2026-10-14 (0 days ago)

    nl = newsletter.build_newsletter(clean_state, "weekly")
    assert nl["publishable"] is False
    assert len(nl["items"]) == 2

    # Approve 3rd item in weekly window (a05: 2026-10-13)
    clean_state["items"][4]["status"] = "approved"
    nl = newsletter.build_newsletter(clean_state, "weekly")
    assert nl["publishable"] is True
    assert len(nl["items"]) == 3
    assert nl["message"] == ""


def test_case_9_weekly_vs_monthly_window(clean_state):
    """Case 9: Toggle weekly -> monthly reflects window days and max caps."""
    # Approve all recommended items
    for it in clean_state["items"]:
        if it.get("decision") == "recommended":
            it["status"] = "approved"

    # Weekly window: 7 days, cap 3
    nl_weekly = newsletter.build_newsletter(clean_state, "weekly")
    assert nl_weekly["publishable"] is True
    assert len(nl_weekly["items"]) <= 3
    for it in nl_weekly["items"]:
        # Verify within 7 days
        diff = (pytest.importorskip("datetime").date.fromisoformat(AS_OF) -
                pytest.importorskip("datetime").date.fromisoformat(it["published"])).days
        assert 0 <= diff <= 7

    # Monthly window: 30 days, cap 5
    nl_monthly = newsletter.build_newsletter(clean_state, "monthly")
    assert nl_monthly["publishable"] is True
    assert len(nl_monthly["items"]) <= 5
    for it in nl_monthly["items"]:
        diff = (pytest.importorskip("datetime").date.fromisoformat(AS_OF) -
                pytest.importorskip("datetime").date.fromisoformat(it["published"])).days
        assert 0 <= diff <= 30


def test_duplicate_and_missing_date_excluded_from_newsletter(clean_state):
    """Ensure duplicates and missing dates are excluded from the newsletter."""
    # Try approving duplicate a06 and missing date a10
    a06 = next(it for it in clean_state["items"] if it["id"] == "a06")
    a10 = next(it for it in clean_state["items"] if it["id"] == "a10")
    a06["status"] = "approved"
    a10["status"] = "approved"

    nl = newsletter.build_newsletter(clean_state, "monthly")
    ids_in_nl = {it["id"] for it in nl["items"]}
    assert "a06" not in ids_in_nl  # duplicate
    assert "a10" not in ids_in_nl  # missing date


def test_export_markdown_and_html(clean_state):
    """Verify markdown and HTML exports contain headline, items, URLs, and challenge."""
    # Approve top 3
    for it in clean_state["items"][:5]:
        if it.get("decision") == "recommended":
            it["status"] = "approved"

    nl = newsletter.build_newsletter(clean_state, "weekly")
    md = newsletter.export_markdown(nl)
    html_code = newsletter.export_html(nl)

    # Check Markdown
    assert nl["headline"] in md
    assert "5-Minute" in md
    for it in nl["items"]:
        assert it["title"] in md
        assert it["url"] in md
        assert it["source"] in md

    # Check HTML
    assert "<!DOCTYPE html>" in html_code
    assert nl["headline"] in html_code
    for it in nl["items"]:
        assert it["title"] in html_code
        assert it["url"] in html_code
