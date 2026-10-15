"""Person A owns this file. See CONTRACT.md section 7."""
import json
import os
import re
import sys

from config import AS_OF, LLM_OUTPUT_CACHE_PATH, SAMPLE_ITEMS_PATH, RECOMMEND_THRESHOLD


# ---------------------------------------------------------------------------
# Deduplication helpers
# ---------------------------------------------------------------------------

def _normalize(text: str) -> set[str]:
    """Lowercase, strip punctuation, return word set for Jaccard similarity."""
    words = re.sub(r"[^a-z0-9 ]", "", text.lower()).split()
    return set(words)


def _jaccard(a: set[str], b: set[str]) -> float:
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


def _find_duplicates(items: list[dict], threshold: float = 0.65) -> dict[str, str]:
    """Return {duplicate_id: primary_id} for items whose titles are too similar."""
    dups: dict[str, str] = {}
    normed = [(it["id"], _normalize(it.get("title", ""))) for it in items]
    for i, (id_a, words_a) in enumerate(normed):
        for j, (id_b, words_b) in enumerate(normed):
            if j <= i or id_a in dups or id_b in dups:
                continue
            if _jaccard(words_a, words_b) >= threshold:
                # keep the one from the higher-quality source (earlier in our curated list)
                dups[id_b] = id_a
    return dups


# ---------------------------------------------------------------------------
# Cache helpers
# ---------------------------------------------------------------------------

def _load_cache() -> dict:
    with open(LLM_OUTPUT_CACHE_PATH, encoding="utf-8") as f:
        return json.load(f)


def _save_cache(data: dict) -> None:
    # Save without run_source key
    clean = {k: v for k, v in data.items() if k != "run_source"}
    with open(LLM_OUTPUT_CACHE_PATH, "w", encoding="utf-8") as f:
        json.dump(clean, f, indent=2, ensure_ascii=False)


# ---------------------------------------------------------------------------
# Prompt builder
# ---------------------------------------------------------------------------

def _build_prompt(items: list[dict]) -> str:
    prompt_path = os.path.join(os.path.dirname(__file__), "prompts", "ranker.md")
    with open(prompt_path, encoding="utf-8") as f:
        template = f.read()
    items_json = json.dumps(items, indent=2, ensure_ascii=False)
    return template.replace("{AS_OF}", AS_OF).replace("{ITEMS_JSON}", items_json)


def _strip_fences(text: str) -> str:
    """Remove markdown code fences if the model wraps its output."""
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```\w*\n?", "", text)
        text = re.sub(r"\n?```$", "", text)
    return text.strip()


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------

_VALID_DECISIONS = {"recommended", "filtered"}
_VALID_ACTIONS = {"read", "try", "skip"}
_VALID_TOPICS = {"Tools", "Models", "Career", "Research", "Learning"}
_SCORE_KEYS = {"T", "P", "N", "L", "Q"}


def _validate(data: dict, input_ids: set[str]) -> list[str]:
    """Return a list of error strings. Empty means valid."""
    errors = []
    if "headline" not in data or not isinstance(data.get("headline"), str):
        errors.append("Missing or invalid 'headline'")
    if "challenge" not in data or not isinstance(data.get("challenge"), str):
        errors.append("Missing or invalid 'challenge'")
    items = data.get("items")
    if not isinstance(items, list):
        errors.append("'items' must be a list")
        return errors

    seen_ids = set()
    for idx, it in enumerate(items):
        iid = it.get("id", f"<index {idx}>")
        seen_ids.add(iid)
        scores = it.get("scores", {})
        if not isinstance(scores, dict) or not _SCORE_KEYS.issubset(scores.keys()):
            errors.append(f"{iid}: scores must have keys {_SCORE_KEYS}")
        for k in _SCORE_KEYS:
            v = scores.get(k, -1)
            if not isinstance(v, (int, float)) or not (0 <= v <= 100):
                errors.append(f"{iid}: scores.{k} must be 0-100, got {v}")
        if it.get("decision") not in _VALID_DECISIONS:
            errors.append(f"{iid}: decision must be one of {_VALID_DECISIONS}")
        if it.get("next_action") not in _VALID_ACTIONS:
            errors.append(f"{iid}: next_action must be one of {_VALID_ACTIONS}")
        if it.get("topic") not in _VALID_TOPICS:
            errors.append(f"{iid}: topic must be one of {_VALID_TOPICS}")
        dup = it.get("duplicate_of")
        if dup is not None and dup not in input_ids:
            errors.append(f"{iid}: duplicate_of '{dup}' is not a valid input id")

    missing = input_ids - seen_ids
    if missing:
        errors.append(f"Missing items for ids: {missing}")

    return errors


# ---------------------------------------------------------------------------
# Main pipeline
# ---------------------------------------------------------------------------

def run_pipeline(items: list[dict], use_cache: bool = True) -> dict:
    """Return the LLM-output shape (CONTRACT section 3) plus run_source.

    Cache-first by default. Live call only when use_cache=False AND an API key exists.
    Falls back to cache on ANY failure. Never raises.
    """
    # Fast path: use cache
    if use_cache or not items:
        try:
            out = _load_cache()
            out["run_source"] = "cached"
            return out
        except Exception:
            return {"headline": "", "challenge": "", "items": [], "run_source": "cached"}

    # Live path
    input_ids = {it["id"] for it in items}
    try:
        from llm import call_llm  # late import so cache path never needs API deps

        prompt = _build_prompt(items)
        raw = call_llm(prompt)
        text = _strip_fences(raw)
        data = json.loads(text)
        errors = _validate(data, input_ids)

        # Retry once if there are validation errors
        if errors:
            retry_prompt = prompt + "\n\nYour previous output had errors:\n" + "\n".join(errors) + "\nPlease fix and return valid JSON."
            raw2 = call_llm(retry_prompt)
            text2 = _strip_fences(raw2)
            data = json.loads(text2)
            errors2 = _validate(data, input_ids)
            if errors2:
                raise ValueError(f"Validation failed after retry: {errors2}")

        data["run_source"] = "live"
        return data

    except Exception as exc:
        print(f"[pipeline] Live call failed ({exc}), falling back to cache.", file=sys.stderr)
        try:
            out = _load_cache()
            out["run_source"] = "cached"
            return out
        except Exception:
            return {"headline": "", "challenge": "", "items": [], "run_source": "cached"}


# ---------------------------------------------------------------------------
# CLI: python pipeline.py [--live] [--save]
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    live = "--live" in sys.argv
    save = "--save" in sys.argv

    with open(SAMPLE_ITEMS_PATH, encoding="utf-8") as f:
        items = json.load(f)

    out = run_pipeline(items, use_cache=not live)
    print(f"Source: {out.get('run_source', '?')}")
    print(f"Headline: {out.get('headline', '')}")
    print(f"Challenge: {out.get('challenge', '')}")
    print(f"Items: {len(out.get('items', []))}")
    print()
    item_titles = {it["id"]: it.get("title", it["id"]) for it in items}
    for it in out.get("items", []):
        flag = "✓" if it["decision"] == "recommended" else "✗"
        dup = f" [dup of {it['duplicate_of']}]" if it.get("duplicate_of") else ""
        title = item_titles.get(it["id"], it["id"])
        print(f"  {flag} {it['id']} ({it['total']:3d}) {it['topic']:10s} {title[:60]}{dup}")

    if save and out.get("run_source") == "live":
        _save_cache(out)
        print(f"\nSaved to {LLM_OUTPUT_CACHE_PATH}")
