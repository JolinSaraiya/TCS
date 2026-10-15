# TASKS — Roles, timeline, checklists

> Branches and merge order: see `GIT_WORKFLOW.md`. The repo skeleton already runs with stubs.

## Roles
| | Person A: Data + AI | Person B: Review Station | Person C: Newsletter + Demo |
|---|---|---|---|
| Owns | `llm.py`, `pipeline.py`, `prompts/ranker.md`, `data/*.json` | `storage.py`, Review tab | `newsletter.py`, Newsletter + Export tabs, `DEMO.md`, `tests/` |
| Blocked by | nobody | A's `llm_output.json` (use a hand-faked copy until then) | A's `llm_output.json` (same) |

**Unblock trick:** A's FIRST deliverable (by minute ~25) is a hand-written `llm_output.json` with 3 items, valid per contract. B and C build against that while A perfects the prompt.

## Timeline (matches the handbook)
| Clock | Phase | Everyone | A | B | C |
|---|---|---|---|---|---|
| 1:30-1:40 | Understand | Read `PRD.md`, confirm `CONTRACT.md` | | | Write user/input/output/success on a slide |
| 1:40-1:55 | Sample data | Setup env together (README) | Write 15 items | Scaffold Streamlit + dummy cards | Write 5 test cases + ideal top 5 |
| 1:55-2:20 | Build logic | **Merge at 2:15** | Prompt + `run_pipeline` + cache | `merge()`, `save/load_state`, card rendering | `build_newsletter`, window, cap, gate |
| 2:20-2:40 | Output view | | Run all test cases, tune prompt | Approve/Edit/Reject working + persist | Toggle, preview, exports |
| 2:40-3:00 | Test + demo | Rehearse twice with timer | Fix prompt issues | Fix UI bugs | Run `TEST_CASES.md`, finalize `DEMO.md` |

## MVP checklist (nothing else until all ticked)
**Data / AI (A)**
- [ ] `sample_items.json` has 15 items with real URLs and the planted edge cases
- [ ] Prompt returns valid JSON on 3 consecutive runs
- [ ] `llm_output.json` saved from a good run
- [ ] Fallback works with API key removed

**Review Station (B)**
- [ ] Cards sorted by score, with breakdown
- [ ] Decision / Reason / Next Action visible on each card
- [ ] Approve / Edit / Reject persist across reruns
- [ ] Filtered items shown in a collapsed section with reasons
- [ ] Cached/live badge

**Newsletter (C)**
- [ ] Weekly/monthly toggle changes window and cap
- [ ] Publish gate disabled below 3 approved
- [ ] Markdown and HTML downloads open correctly
- [ ] Every item shows source and link

**Team**
- [ ] All 5 test cases pass
- [ ] Demo rehearsed twice, under 5 minutes
- [ ] Ideal-top-5 match count written down

## Stretch (only after MVP)
- [ ] Live RSS toggle
- [ ] Copy buttons, print view
- [ ] n8n weekly trigger workflow (off critical path)
- [ ] Manual date input for missing-date items
