# CONTRACT — Source of truth for all data

**Field names and enums below are final. Do not rename, add, or remove without all 3 agreeing.**
When prompting any AI coding tool, paste this file at the top.

## 1. Constants (`config.py`)
```python
AS_OF = "2026-10-14"            # fixed "today" for the demo; never use datetime.now()
WEEKLY_WINDOW_DAYS = 7
MONTHLY_WINDOW_DAYS = 30
WEEKLY_MAX_ITEMS = 3
MONTHLY_MAX_ITEMS = 5
MIN_ITEMS_TO_PUBLISH = 3
RECOMMEND_THRESHOLD = 50
WORDS_PER_MIN = 200
TOPICS = ["Tools", "Models", "Career", "Research", "Learning"]
```

## 2. Input item — `data/sample_items.json` (array)
```json
{
  "id": "a01",
  "title": "string",
  "source": "string (publisher name)",
  "url": "string (real, clickable)",
  "published": "YYYY-MM-DD or null",
  "excerpt": "2-3 sentences in our own words, NOT copied from the article",
  "word_count": 1400
}
```
Rules: 15 items, dates spread across the 30 days before `AS_OF`, at least one duplicate pair, one near-miss pair, one earnings item, one item with `published: null`.

## 3. LLM output — `data/llm_output.json`
```json
{
  "headline": "string, max 10 words",
  "challenge": "string, ONE 5-minute learning task for the whole newsletter",
  "items": [
    {
      "id": "a01",
      "scores": { "T": 85, "P": 90, "N": 95, "L": 80, "Q": 90 },
      "total": 88,
      "decision": "recommended",
      "reason": "one line: why kept or filtered",
      "topic": "Tools",
      "summary": "max 30 words, What happened? ONLY from excerpt",
      "why_it_matters": "max 20 words, The value to students",
      "target_audience": "e.g., CS students, Python devs, job seekers (Who is it for?)",
      "what_to_do_next": "e.g., Try Ollama command, apply on portal (What to do next)",
      "next_action": "read",
      "duplicate_of": null
    }
  ]
}
```
Formula: `total = round(0.35*T + 0.25*P + 0.20*N + 0.15*L + 0.05*Q)`
Enums:
- `decision`: `recommended` | `filtered`
- `topic`: one of `TOPICS`
- `next_action`: `read` | `try` | `skip`
- `duplicate_of`: item `id` string or `null`

## 4. Merged item (what the UI works with)
Input item fields + LLM item fields + these:
```json
{
  "reading_time_min": 7,
  "status": "pending",
  "edited": false,
  "date_flag": null
}
```
- `status`: `pending` | `approved` | `rejected`
- `reading_time_min = max(1, ceil(word_count / 200))`, always displayed as "~N min (est.)"
- `date_flag`: `"missing_date"` if `published` is null, else `null`
- Editing a card changes `summary` / `why_it_matters` in place and sets `edited: true`. It does not change status.

## 5. App state — `data/state.json`
```json
{
  "run_source": "cached",
  "headline": "",
  "challenge": "",
  "period": "weekly",
  "items": [ /* merged items */ ]
}
```
- `run_source`: `cached` | `live` — shown as a badge in the UI, always.

## 6. Newsletter object (output of `newsletter.build_newsletter`)
```json
{
  "headline": "",
  "challenge": "",
  "period": "weekly",
  "as_of": "2026-10-14",
  "items": [ /* merged items, approved only, in window, sorted by total desc, capped */ ],
  "publishable": true,
  "message": "empty string or reason why not publishable"
}
```

## 7. Module interfaces (the only cross-person calls)
```python
# pipeline.py (Person A)
def run_pipeline(items: list[dict], use_cache: bool = True) -> dict:
    """Returns the LLM-output shape (section 3). Falls back to cache on any failure.
    Must also return key "run_source": "cached" | "live"."""

# storage.py (Person B)
def load_state() -> dict: ...
def save_state(state: dict) -> None: ...
def merge(items: list[dict], llm_out: dict) -> list[dict]:
    """Builds merged items (section 4) from input items + LLM output."""

# newsletter.py (Person C)
def build_newsletter(state: dict, period: str) -> dict: ...      # section 6
def export_markdown(nl: dict) -> str: ...
def export_html(nl: dict) -> str: ...
```

## 8. Change log
| When | Change | Agreed by |
|---|---|---|
| start | Initial contract | A, B, C |
