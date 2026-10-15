"""Person B owns this file. State persistence + merge(). See CONTRACT.md sections 4, 5, 7."""
import json
import math
import os

from config import STATE_PATH, WORDS_PER_MIN


def load_state() -> dict:
    if not os.path.exists(STATE_PATH):
        return {}
    try:
        with open(STATE_PATH, encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return {}


def save_state(state: dict) -> None:
    os.makedirs(os.path.dirname(STATE_PATH), exist_ok=True)
    tmp = STATE_PATH + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2, ensure_ascii=False)
    os.replace(tmp, STATE_PATH)


def merge(items: list[dict], llm_out: dict) -> list[dict]:
    """Input items + LLM item fields + status/edited/reading_time_min/date_flag."""
    by_id = {x["id"]: x for x in llm_out.get("items", [])}
    merged = []
    for it in items:
        ai = by_id.get(it["id"])
        if ai is None:
            continue
        m = {**it, **ai}
        m["reading_time_min"] = max(1, math.ceil(it.get("word_count", 0) / WORDS_PER_MIN))
        m["status"] = "pending"
        m["edited"] = False
        m["date_flag"] = "missing_date" if not it.get("published") else None
        merged.append(m)
    return merged
