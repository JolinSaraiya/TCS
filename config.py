"""Constants only. Mirrors CONTRACT.md section 1. Do not edit without team agreement."""
AS_OF = "2026-10-14"  # fixed "today" for the demo; never use datetime.now()
WEEKLY_WINDOW_DAYS = 7
MONTHLY_WINDOW_DAYS = 30
WEEKLY_MAX_ITEMS = 3
MONTHLY_MAX_ITEMS = 5
MIN_ITEMS_TO_PUBLISH = 3
RECOMMEND_THRESHOLD = 50
WORDS_PER_MIN = 200
TOPICS = ["Tools", "Models", "Career", "Research", "Learning"]

SAMPLE_ITEMS_PATH = "data/sample_items.json"
LLM_OUTPUT_CACHE_PATH = "data/llm_output.json"
STATE_PATH = "data/state.json"
