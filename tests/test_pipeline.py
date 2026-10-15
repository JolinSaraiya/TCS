"""Automated tests for pipeline, scoring, deduplication, and edge cases."""
import json
import pytest
from config import AS_OF, RECOMMEND_THRESHOLD, SAMPLE_ITEMS_PATH
import pipeline
import storage


@pytest.fixture
def sample_items():
    with open(SAMPLE_ITEMS_PATH, encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture
def pipeline_output(sample_items):
    return pipeline.run_pipeline(sample_items, use_cache=True)


@pytest.fixture
def merged_state(sample_items, pipeline_output):
    return {
        "run_source": pipeline_output.get("run_source", "cached"),
        "headline": pipeline_output.get("headline", ""),
        "challenge": pipeline_output.get("challenge", ""),
        "period": "weekly",
        "items": storage.merge(sample_items, pipeline_output),
    }


def test_case_1_normal_model_release(merged_state):
    """Case 1: Normal open-source coding model release (a01 - Llama 3.3)."""
    item = next(it for it in merged_state["items"] if it["id"] == "a01")
    assert item["decision"] == "recommended"
    assert item["topic"] in ("Models", "Tools")
    assert item["total"] >= RECOMMEND_THRESHOLD
    assert item["scores"]["T"] >= 80  # high tools/practicality


def test_case_2_career_item(merged_state):
    """Case 2: Career / hiring report (a03 - Stanford AI Index)."""
    item = next(it for it in merged_state["items"] if it["id"] == "a03")
    assert item["decision"] == "recommended"
    assert item["topic"] == "Career"
    assert item["scores"]["P"] >= 60  # high professional impact
    assert item["total"] >= RECOMMEND_THRESHOLD


def test_case_3_duplicate_handling(merged_state):
    """Case 3: Exact duplicate pair (a05 vs a06 - Gemini Flash)."""
    a05 = next(it for it in merged_state["items"] if it["id"] == "a05")
    a06 = next(it for it in merged_state["items"] if it["id"] == "a06")
    # a05 is primary (recommended), a06 is marked duplicate_of a05
    assert a05["decision"] == "recommended"
    assert a05["duplicate_of"] is None
    assert a06["duplicate_of"] == "a05"
    assert a06["decision"] == "filtered"


def test_case_4_edge_corporate_noise(merged_state):
    """Case 4: Corporate earnings / noise item (a09 - Nvidia Q3 earnings)."""
    item = next(it for it in merged_state["items"] if it["id"] == "a09")
    assert item["decision"] == "filtered"
    assert item["total"] < RECOMMEND_THRESHOLD
    assert "earnings" in item["reason"].lower() or "financial" in item["reason"].lower() or "corporate" in item["reason"].lower()


def test_case_5_missing_date_flag(merged_state):
    """Case 5: Item with published: null (a10)."""
    item = next(it for it in merged_state["items"] if it["id"] == "a10")
    assert item["published"] is None
    assert item["date_flag"] == "missing_date"


def test_case_6_near_miss_not_duplicated(sample_items):
    """Case 6: Near-miss pair (a07 Cursor feature vs a08 Cursor funding)."""
    # Jaccard title similarity should NOT mark a08 as duplicate of a07
    dups = pipeline._find_duplicates(sample_items)
    assert dups.get("a08") != "a07"


def test_case_7_offline_fallback():
    """Case 7: Cache fallback works seamlessly without API key."""
    # When use_cache=True, should return valid structure with run_source="cached"
    items = [{"id": "x01", "title": "Test", "url": "https://example.com", "excerpt": "Short excerpt"}]
    out = pipeline.run_pipeline(items, use_cache=True)
    assert out["run_source"] == "cached"
    assert "items" in out
    assert "headline" in out
    assert "challenge" in out


def test_score_formula_calculation():
    """Verify official formula: total = round(0.35*T + 0.25*P + 0.20*N + 0.15*L + 0.05*Q)."""
    with open(SAMPLE_ITEMS_PATH, encoding="utf-8") as f:
        items = json.load(f)
    out = pipeline.run_pipeline(items, use_cache=True)
    for it in out["items"]:
        sc = it["scores"]
        expected = round(0.35 * sc["T"] + 0.25 * sc["P"] + 0.20 * sc["N"] + 0.15 * sc["L"] + 0.05 * sc["Q"])
        assert it["total"] == expected, f"Item {it['id']} total {it['total']} != expected {expected}"
