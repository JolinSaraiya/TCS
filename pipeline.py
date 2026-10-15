"""Person A owns this file. See CONTRACT.md section 7."""
import json

from config import LLM_OUTPUT_CACHE_PATH


def _load_cache() -> dict:
    with open(LLM_OUTPUT_CACHE_PATH, encoding="utf-8") as f:
        return json.load(f)


def run_pipeline(items: list[dict], use_cache: bool = True) -> dict:
    """Return the LLM-output shape (CONTRACT section 3) plus run_source.

    Skeleton: always returns the cached file. TODO (A): live call, validation, retry, fallback.
    """
    out = _load_cache()
    out["run_source"] = "cached"
    return out
