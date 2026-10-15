# TEAM PROMPTS
Check out your branch first, then paste your prompt into your AI coding tool (Cursor / Claude Code / Copilot / Codex).

| Person | Branch | Role |
|---|---|---|
| A | `feat/a-ai-pipeline` | Data + AI |
| B | `feat/b-review-station` | Review Station |
| C | `feat/c-newsletter` | Newsletter + Demo |

---

## PROMPT A: Data + AI

```
You are my pair-programmer. I am Person A (Data + AI) on a 3-person, 90-minute hackathon team building "AI Pulse", a Streamlit app that turns cached AI news into a student newsletter. I am on branch feat/a-ai-pipeline.

FIRST read README.md, PRD.md, CONTRACT.md, ARCHITECTURE.md, AGENTS.md, GIT_WORKFLOW.md. Follow AGENTS.md strictly. CONTRACT.md field names are law.

I may ONLY edit: llm.py, pipeline.py, prompts/ranker.md, data/sample_items.json, data/llm_output.json. Do not touch any other file.

Do these in order, one at a time, showing me complete code:

1. llm.py: call_llm(prompt: str) -> str. Provider from env LLM_PROVIDER (groq | gemini), keys from .env, model from LLM_MODEL or a sensible default, JSON mode where supported, temperature 0.2, 20s timeout, raise on any failure.

2. prompts/ranker.md: ONE batched prompt with placeholders {AS_OF} and {ITEMS_JSON}. It must instruct the model to, for EVERY input item:
   - score with the rubric: tools 0-40, career 0-30, accessibility 0-30, noise_penalty -50..0; total = clamp(sum, 0, 100)
   - decision = "recommended" if total >= 50 and the item is not a duplicate, else "filtered"
   - reason: one line, why kept or filtered
   - topic: one of Tools, Models, Career, Research, Learning
   - summary: max 30 words, using ONLY the item's excerpt, no outside facts, no invented versions/URLs/APIs
   - why_it_matters: max 20 words, aimed at CS students
   - next_action: read | try | skip
   - duplicate_of: id of the primary item if it is the SAME story from another source (keep the best source), else null. Items about the same product but DIFFERENT news (e.g. release vs pricing) are NOT duplicates.
   Also return: headline (max 10 words) and ONE 5-minute challenge for the whole newsletter.
   Output ONLY valid JSON matching CONTRACT.md section 3. No prose, no code fences. Include few-shot guidance only if short.

3. pipeline.py run_pipeline(items, use_cache=True): if use_cache is True or no API key -> load data/llm_output.json. Else build the prompt, call_llm, strip code fences, json.loads, validate with pydantic (enums, score ranges, every input id present exactly once, duplicate_of references a real id), retry ONCE telling the model what was wrong, and on ANY failure fall back to the cache. Always set out["run_source"] to "cached" or "live". It must never raise. Add `python pipeline.py --live --save` to run live on data/sample_items.json, print a summary table, and save the result (without run_source) to data/llm_output.json.

4. data/sample_items.json: 15 items per CONTRACT section 2. Do NOT invent URLs or articles. Ask me to paste real articles (title, publisher, URL, date, my own 2-3 sentence excerpt, approx word count) for these slots, and you format the JSON:
   - 2 high-relevance tools/models (one is an open-source coding model release)
   - 2 career/hiring reports
   - 2 items that are the SAME story from two sources (duplicate pair)
   - 2 items about the same product with DIFFERENT news (near-miss pair)
   - 1 corporate earnings or funding item
   - 1 item with published = null
   - 1 research summary, 1 learning resource, 1 medium-relevance item, 2 hype/noise items
   Dates: all within the 30 days before AS_OF (2026-10-14), at least 5 within the last 7 days.

5. Run the live pipeline 3 times. Report: valid JSON each time? Duplicates detected correctly? Earnings filtered? Near-miss not merged? Fix the prompt until all pass, then save the best run to data/llm_output.json.

Rules: never change CONTRACT field names; never use datetime.now(); pipeline must work with Wi-Fi off.
Commit small ("A: ..."), push with `git push origin HEAD`. Tell me when each step is done so I can message B and C.
```

---

## PROMPT B: Review Station

```
You are my pair-programmer. I am Person B (Review Station) on a 3-person, 90-minute hackathon team building "AI Pulse", a Streamlit app that turns cached AI news into a student newsletter. I am on branch feat/b-review-station.

FIRST read README.md, PRD.md, CONTRACT.md, ARCHITECTURE.md, AGENTS.md, GIT_WORKFLOW.md. Follow AGENTS.md strictly. CONTRACT.md field names are law.

I may ONLY edit: storage.py and ui_review.py. Do not touch any other file. The repo already runs with `streamlit run app.py` using stubs and 4 seed items in data/; build against those. Person A will later replace the data with 15 real items, so never hardcode ids or counts.

Tasks, in order, with complete code:

1. storage.py: harden load_state/save_state (atomic write already there; handle corrupt/missing file), and merge(items, llm_out) per CONTRACT section 4. If an item has no LLM result, keep it with decision "filtered" and reason "not scored" instead of dropping it.

2. ui_review.py render_review_tab(state):
   - Header: data-source badge from state["run_source"] and counter "Approved X / 3 needed".
   - Cards for decision == "recommended" and not duplicate, sorted by total desc. Each card shows: title as a link to url, source, published date (or a warning chip if date_flag == "missing_date"), total score with the 4-part breakdown (tools/career/accessibility/noise_penalty), an explicit row "Decision / Reason / Next Action", summary, why it matters, topic chip, "~N min (est.)", and status badge.
   - Buttons per card: Approve, Reject, Edit. Edit reveals text areas for summary and why_it_matters with Save/Cancel; saving sets edited=True and keeps status. 
   - Duplicates: shown under their primary item as "Also reported by: <source>", not as their own cards.
   - A collapsed expander "Filtered out (and why)" listing filtered items with reason and score breakdown, each with an "Override and include" button that sets decision to "recommended" (keep original reason visible).
   - Every click mutates the state dict, calls storage.save_state(state), and st.rerun(). All widgets need stable keys that include the item id.

3. Edge cases that must NOT crash: item with published null, all items rejected, zero recommended items, duplicate_of pointing to a filtered item, very long summary.

4. Test locally with Wi-Fi off. Walk through: approve 3, edit one, reject one, refresh the browser, confirm state persists.

Rules: never change CONTRACT field names; do not edit app.py, newsletter.py, pipeline.py, config.py; no new dependencies.
Commit small ("B: ..."), push with `git push origin HEAD`. Tell me when each task is done.
```

---

## PROMPT C: Newsletter + Demo

```
You are my pair-programmer. I am Person C (Newsletter + Demo) on a 3-person, 90-minute hackathon team building "AI Pulse", a Streamlit app that turns cached AI news into a student newsletter. I am on branch feat/c-newsletter.

FIRST read README.md, PRD.md, CONTRACT.md, ARCHITECTURE.md, AGENTS.md, GIT_WORKFLOW.md, DEMO.md, tests/TEST_CASES.md. Follow AGENTS.md strictly. CONTRACT.md field names are law.

I may ONLY edit: newsletter.py, ui_newsletter.py, app.py, tests/, DEMO.md. Do not touch any other file. The repo already runs with `streamlit run app.py` using stubs and 4 seed items in data/; build against those. Person B builds the Review Station, so for testing, set statuses by hand in data/state.json or in a small test script. Never hardcode ids or counts.

Tasks, in order, with complete code:

1. newsletter.py: review and harden build_newsletter(state, period) per CONTRACT section 6. Weekly = window of 7 days before AS_OF, max 3 items; monthly = 30 days, max 5. Include only approved, non-duplicate items with a published date inside the window, sorted by total desc. publishable = len(items) >= MIN_ITEMS_TO_PUBLISH, else message explains how many more approvals are needed. Polish export_markdown and export_html (headline, edition + AS_OF, per item: topic, "~N min (est.)", summary, why it matters, source + link, then the challenge, footer "AI-assisted, reviewed by a human coordinator"). HTML must escape content and look clean with inline CSS only.

2. ui_newsletter.py:
   - render_newsletter_tab: Weekly/Monthly radio that writes state["period"] and calls storage.save_state(state); styled preview of the newsletter; if not publishable show the message and a DISABLED Publish button; if publishable show an enabled Publish button that shows a success message pointing to the Export tab.
   - render_export_tab: download buttons for .md and .html, plus a read-only text area with the Markdown to copy. Disabled with an explanation when not publishable.

3. app.py: keep it a thin shell. Only fix bugs. Make sure the data-source badge and the Reset button work.

4. tests/: write tests/run_checks.py (plain asserts, no pytest) covering: weekly vs monthly give different sets/caps, missing-date item excluded, duplicate excluded, <3 approved => publishable False, exports contain every item's url. Run it.

5. DEMO.md and tests/TEST_CASES.md: after Person A pushes the 15 real items, hand-label the ideal top 5 BEFORE seeing the AI output, then fill in the match count and pass/fail table. Rehearse the 5-minute demo with a timer.

Rules: never change CONTRACT field names; never use datetime.now(); do not edit storage.py, ui_review.py, pipeline.py, llm.py, config.py; no new dependencies.
Commit small ("C: ..."), push with `git push origin HEAD`. Tell me when each task is done.
```

---

## MERGE CAPTAIN prompt (for whoever merges)

```
Read GIT_WORKFLOW.md. Help me merge feat/a-ai-pipeline, feat/b-review-station, feat/c-newsletter into main in that order with --no-ff. After each merge run `streamlit run app.py` (Wi-Fi off) and tell me what to check. If there is a conflict, tell me which person owns the file (see ARCHITECTURE.md) and keep that owner's version. Do not edit CONTRACT.md.
```
