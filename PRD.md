# PRD — AI Pulse

## 1. One-liner
A web app that turns a whitelist of trusted AI sources into a short, student-friendly newsletter, which a club coordinator reviews and approves before publishing.

## 2. User
**Primary:** college club coordinator (non-expert in every AI sub-topic, short on time).
**Reader:** students and future software engineers.

## 3. Problem
Finding, vetting, and summarizing AI news relevant to software-engineering students takes hours every week, so newsletters are late, inconsistent, or never sent.

## 4. Goal and success metrics
| Metric | Target |
|---|---|
| Time from open-app to published newsletter | < 2 minutes (cached run) |
| Items per newsletter | 3-5, every one with source + link |
| Human review | 100% of published items approved by coordinator |
| Relevance accuracy | At least 4 of AI's top 5 match our hand-labeled "ideal top 5" |
| Demo reliability | Works with Wi-Fi off |

## 5. Scope

### MVP (must ship)
- Load approved-source items (cached JSON)
- One batched LLM call: score, filter, dedupe, summarize, why-it-matters, topic, next action, headline, challenge
- Review Station: per-item card with Decision / Reason / Next Action, Approve / Edit / Reject
- Newsletter preview with weekly/monthly toggle
- Publish gate (needs >= 3 approved items)
- Export Markdown + HTML
- Source attribution and link on every item
- Cached fallback with visible "cached" badge

### Should have (only if MVP is done)
- Live RSS toggle
- Copy-to-clipboard buttons
- Print view

### Explicitly out of scope
FastAPI/React, user accounts, database, email sending, social media sources, per-item challenges, regenerate endpoint, n8n on the critical path.

## 6. Requirements mapping (problem statement → feature)
| Requirement | Where it lives |
|---|---|
| Approved-source input | `sample_items.json` with a `source` allow-list |
| Remove duplicates | LLM sets `duplicate_of`; UI hides duplicates |
| AI filtering by relevance | LLM scores each item with breakdown; `decision` |
| Headline, 3-5 updates | Newsletter object: `headline` + capped `items` |
| Plain-language summary + why it matters | `summary`, `why_it_matters` |
| Attribution + link | `source`, `url` shown on every card |
| Topic categories, reading time | `topic`, `reading_time_min` (est.) |
| Weekly / monthly | Window + item cap in `newsletter.py` |
| Review step (edit/approve/remove) | Review Station tab |
| Learning challenge (example in spec) | One `challenge` per newsletter |

## 7. Scoring rubric (explainable)
| Dimension | Range | Meaning |
|---|---|---|
| `tools` | 0-40 | Affects tools/stacks students will use (coding assistants, open models, frameworks) |
| `career` | 0-30 | Affects skills, jobs, hiring, practices for software engineers |
| `accessibility` | 0-30 | Understandable and usable by a student without paid access or deep expertise |
| `noise_penalty` | -50 to 0 | Earnings, funding gossip, hype, unverifiable claims, social-media-only |

`total = clamp(sum, 0, 100)`. `decision = recommended` if `total >= 50` and not a duplicate, else `filtered`.

## 8. Risks and mitigations
| Risk | Mitigation |
|---|---|
| LLM returns bad JSON | Validate with pydantic, retry once, fall back to `llm_output.json` |
| LLM hallucinates | Summary may use ONLY the excerpt; max 30 words |
| API / Wi-Fi fails | `USE_CACHE_ONLY=true` default; "cached" badge shown honestly |
| Date window empty on demo day | Fixed `AS_OF` date in `config.py`, never `now()` |
| Reject drops below 3 items | Publish disabled + UI hint to approve more |
| Scope creep | MVP checklist in `TASKS.md`; B and C review each other's PRs |

## 9. Limitations to state in the demo
LLM can err; relevance is subjective; sources are hand-curated; reading time is estimated from stored word count; prototype uses cached content.
