"""Constants only. Mirrors CONTRACT.md section 1. Do not edit without team agreement."""
AS_OF = "2026-10-14"  # fixed "today" for the demo; never use datetime.now()
DAILY_WINDOW_DAYS = 1
WEEKLY_WINDOW_DAYS = 7
MONTHLY_WINDOW_DAYS = 30

DAILY_MAX_ITEMS = 2
WEEKLY_MAX_ITEMS = 3
MONTHLY_MAX_ITEMS = 5
MIN_ITEMS_TO_PUBLISH = 3
RECOMMEND_THRESHOLD = 50
WORDS_PER_MIN = 200

# Official scoring formula weights: R = 0.35T + 0.25P + 0.20N + 0.15L + 0.05Q
WEIGHT_T = 0.35  # Relevance to AI & software engineering
WEIGHT_P = 0.25  # Practical value for students
WEIGHT_N = 0.20  # Recency
WEIGHT_L = 0.15  # Learning or career value
WEIGHT_Q = 0.05  # Source quality

TOPICS = ["Tools", "Models", "Career", "Research", "Learning"]
PERIODS = ["daily", "weekly", "monthly"]

SAMPLE_ITEMS_PATH = "data/sample_items.json"
LLM_OUTPUT_CACHE_PATH = "data/llm_output.json"
STATE_PATH = "data/state.json"

