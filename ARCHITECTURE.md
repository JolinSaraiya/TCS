# ARCHITECTURE

## Design choice
Single Streamlit app, plain Python modules, JSON files. No separate backend, no frontend build, no database. This removes the #1 hackathon killer: frontend-backend integration.

## Flow
```
data/sample_items.json
        │
        ▼
pipeline.run_pipeline()  ── USE_CACHE_ONLY or API fail ──► data/llm_output.json
        │  (ONE batched LLM call, validated with pydantic, 1 retry)
        ▼
storage.merge()  → merged items (+ status, reading_time_min, date_flag)
        │
        ▼
data/state.json  ◄──── Review Station (Approve / Edit / Reject)
        │
        ▼
newsletter.build_newsletter(period)  → window + cap + publish gate
        │
        ▼
export_markdown() / export_html()  → download buttons
```

## Modules
| File | Owner | Responsibility |
|---|---|---|
| `llm.py` | A | `call_llm(prompt: str) -> str`. Provider switch via `.env`. Timeout 20s. |
| `pipeline.py` | A | Build prompt from `prompts/ranker.md` + items + `AS_OF`; call LLM; parse JSON (strip code fences); validate; retry once; fallback to cache; tag `run_source`. |
| `prompts/ranker.md` | A | The batched prompt with rubric and JSON schema. |
| `storage.py` | B | State persistence and `merge()`. Save on every click. |
| `ui_review.py` | B | `render_review_tab(state)`: Review Station UI. |
| `newsletter.py` | C | Date window, cap, publish gate, Markdown/HTML export. |
| `ui_newsletter.py` | C | `render_newsletter_tab(state)` and `render_export_tab(state)`. |
| `app.py` | C | Shell only (already wired in the skeleton): page config, state init, tab wiring. |
| `config.py` | shared | Constants only. |

The skeleton on `main` already runs end to end with stubs. Each person replaces their stubs on their own branch; branches never touch each other's files, so merges are conflict-free.

## UI structure
| Tab | Shows |
|---|---|
| Review Station | Run-source badge. Cards sorted by `total` desc. Each: title, source link, score + 4-part breakdown, Decision / Reason / Next Action, summary, why it matters, topic chip, est. reading time, date flag, Approve / Edit / Reject. Collapsed section "Filtered out (and why)". Duplicates shown merged under the primary item. |
| Newsletter | Weekly/Monthly radio. Headline, items, challenge. Publish-gate message if < 3 approved. |
| Export | Download `.md`, download `.html`, text area to copy. |

## Key behaviors
- **Weekly:** window = 7 days before `AS_OF`, max 3 items. **Monthly:** 30 days, max 5.
- **Publish gate:** `publishable = approved_in_window >= 3`.
- **Missing date:** item is kept, flagged `missing_date`, excluded from windowed newsletters unless the coordinator edits it (stretch: manual date input).
- **Cache-first:** default `USE_CACHE_ONLY=true`. A "Run live" button is shown only if an API key exists; on failure it falls back to cache and the badge says `cached`.
- **Persistence:** every Approve/Edit/Reject calls `save_state()`. Streamlit reruns must not lose state: initialize from `st.session_state` first, then `state.json`.

## Optional n8n layer (stretch, off the critical path)
```
Schedule Trigger (weekly) → RSS Read (approved feeds) → HTTP Request → (future) /generate → Email/Slack coordinator
```
The Streamlit app must run fully without it. If it is not working by the 2:20 mark, drop it.

## Failure handling
| Failure | Behavior |
|---|---|
| Invalid JSON from LLM | Strip fences → parse → pydantic validate → retry once → cache |
| API timeout / no key / no Wi-Fi | Cache, badge `cached` |
| Missing `published` | Flag, don't crash |
| Fewer than 3 approved | Publish disabled with explanation |
